#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


MANIFESTS = (
    "requirements.txt", "pyproject.toml", "package.json", "pnpm-lock.yaml", "yarn.lock",
    "package-lock.json", "Cargo.toml", "go.mod", "Gemfile", "composer.json",
)
RISKY_ASSET_PARTS = {
    ".tmp", "tmp", "temp", "cache", "caches", "_screenshots", "playwright-report",
    "test-results", "preview-output", "visual-regression", "screenshots-cache",
}
BADGE_MARKERS = (
    "img.shields.io", "/actions/workflows/", "badge.svg", "badgen.net",
    "codecov.io", "coveralls.io",
)


@dataclass(frozen=True)
class ImageRef:
    source: str
    alt: str
    line: int
    requires_alt: bool = True


def repository_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError("not a Git repository")
    return Path(result.stdout.strip()).resolve()


def clean_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1:target.index(">")]
    else:
        target = re.sub(r'''\s+(?:"[^"]*"|'[^']*')\s*$''', "", target)
    if is_remote(target):
        return target
    # Query strings select a GitHub representation, not a filesystem name.
    # Decode after parsing so %23 and %3F remain part of a literal filename.
    return unquote(urlsplit(target).path)


def is_remote(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "data:"))


def without_fenced_code(markdown: str) -> str:
    lines = []
    fence = None
    for line in markdown.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence is None and marker:
            fence = marker.group(1)
            lines.append("\n" if line.endswith("\n") else "")
        elif fence is not None:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) and not marker.group(2).strip():
                fence = None
            lines.append("\n" if line.endswith("\n") else "")
        else:
            lines.append(line)
    return "".join(lines)


def markdown_links(markdown: str) -> list[str]:
    markdown = without_fenced_code(markdown)
    result: list[str] = []
    for match in re.finditer(r"!?(?:\[[^\]]*\])\(([^)]+)\)", markdown):
        target = clean_target(match.group(1))
        if target and not is_remote(target) and not target.startswith("#"):
            result.append(target)
    return result


def image_references(markdown: str) -> list[ImageRef]:
    markdown = without_fenced_code(markdown)
    result: list[ImageRef] = []
    for match in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", markdown):
        result.append(ImageRef(clean_target(match.group(2)), match.group(1).strip(), markdown.count("\n", 0, match.start()) + 1))
    class Images(HTMLParser):
        def handle_starttag(self, tag, attributes):
            if tag not in {"img", "source"}:
                return
            attrs = dict(attributes)
            alt = (attrs.get("alt") or "").strip()
            if tag == "img" and attrs.get("src"):
                result.append(ImageRef(clean_target(attrs["src"]), alt, self.getpos()[0]))
            # Validate all responsive candidates, including those hidden on desktop.
            srcset = attrs.get("srcset") or ""
            candidates = [srcset] if srcset.startswith("data:") else srcset.split(",")
            for candidate in candidates:
                if candidate.strip():
                    source = candidate.strip().split()[0]
                    result.append(ImageRef(clean_target(source), alt, self.getpos()[0], tag == "img"))
    Images().feed(markdown)
    return result


def resolve_local(root: Path, readme: Path, target: str) -> Path:
    if target.startswith("/"):
        return (root / target.lstrip("/")).resolve()
    return (readme.parent / target).resolve()


def is_badge(source: str) -> bool:
    lowered = source.lower()
    return any(marker in lowered for marker in BADGE_MARKERS)


def local_name(tag_or_attr: str) -> str:
    return tag_or_attr.rsplit("}", 1)[-1].lower()


def verify_svg(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        source = path.read_text(encoding="utf-8-sig")
        root = ET.fromstring(source)
    except (ET.ParseError, OSError) as exc:
        return [f"invalid SVG XML ({exc})"]

    if re.search(r"(?i)@import|url\(\s*['\"]?(?:https?:|data:)", source):
        problems.append("external or embedded CSS asset")

    for element in root.iter():
        tag = local_name(element.tag)
        if tag in {"script", "foreignobject"}:
            problems.append(f"unsafe <{tag}> element")
        for raw_name, raw_value in element.attrib.items():
            name = local_name(raw_name)
            value = raw_value.strip()
            if name.startswith("on"):
                problems.append(f"event handler attribute: {name}")
            if name in {"href", "src"} and value and not value.startswith("#"):
                problems.append(f"linked asset is not self-contained: {value}")
    return sorted(set(problems))


def git_tags(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "tag", "--list"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()] if result.returncode == 0 else []


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify README structure, visuals, and repository discoverability.")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true", help="Treat structural warnings as errors.")
    parser.add_argument("--visual", action="store_true", help="Require and validate a deliberate first-screen visual treatment.")
    args = parser.parse_args()

    try:
        root = repository_root(Path(args.repository).resolve())
        readme = next((root / name for name in ("README.md", "README.MD", "readme.md") if (root / name).is_file()), None)
        if not readme:
            print("ERROR README: missing README.md")
            return 1

        text = readme.read_text(encoding="utf-8-sig")
        errors: list[str] = []
        warnings: list[str] = []

        if re.search(r"\{\{[A-Z0-9_ -]+\}\}|\[TODO(?::[^\]]*)?\]", text, re.I):
            errors.append("README contains template placeholders or TODO markers")
        if not re.search(r"(?im)^#\s+\S", text):
            errors.append("README has no semantic H1 project title")

        section_rules = {
            "problem/value": r"项目解决什么问题|解决.*问题|why|problem|overview",
            "quick start": r"快速开始|本地复现|quick\s*start|getting\s*started|installation",
            "verification": r"验证|测试|verify|tests?",
            "security": r"安全|隐私|security|privacy",
        }
        for label, pattern in section_rules.items():
            if not re.search(pattern, text, re.I):
                warnings.append(f"README does not clearly expose a {label} section")

        checked_targets: set[str] = set()
        for target in markdown_links(text):
            if target in checked_targets:
                continue
            checked_targets.add(target)
            candidate = resolve_local(root, readme, target)
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"README local link escapes the repository: {target}")
                continue
            if not candidate.exists():
                errors.append(f"README local link is broken: {target}")

        images = image_references(text)
        local_images: list[tuple[ImageRef, Path]] = []
        for image in images:
            if args.visual and image.requires_alt and not image.alt and not is_badge(image.source):
                warnings.append(f"README image has no descriptive alt text at line {image.line}: {image.source}")
            if args.visual and is_remote(image.source) and not is_badge(image.source):
                warnings.append(f"README visual depends on a remote image; prefer a repository asset: {image.source}")
            if not image.source or is_remote(image.source):
                continue
            candidate = resolve_local(root, readme, image.source)
            try:
                relative = candidate.relative_to(root)
            except ValueError:
                errors.append(f"README image escapes the repository: {image.source}")
                continue
            if not candidate.is_file():
                errors.append(f"README image is missing: {image.source}")
                continue
            local_images.append((image, candidate))
            if any(part.lower() in RISKY_ASSET_PARTS for part in relative.parts):
                errors.append(f"README image points to a generated/cache path: {image.source}")

            size = candidate.stat().st_size
            suffix = candidate.suffix.lower()
            if suffix == ".svg":
                if size > 256 * 1024:
                    warnings.append(f"README SVG is unusually large ({size} bytes): {image.source}")
                for problem in verify_svg(candidate):
                    errors.append(f"unsafe README SVG {image.source}: {problem}")
            elif size > 5 * 1024 * 1024:
                errors.append(f"README image exceeds 5 MiB: {image.source}")
            elif size > 2 * 1024 * 1024:
                warnings.append(f"README image exceeds 2 MiB and should be optimized: {image.source}")

        if args.visual:
            first_screen = "\n".join(text.splitlines()[:80])
            first_screen_images = [ref for ref in image_references(first_screen) if not is_badge(ref.source)]
            if not first_screen_images:
                warnings.append("visual mode found no non-badge image in the first 80 README lines")
            tags = git_tags(root)
            if tags and not re.search(r"(?i)(/releases|/tags|CHANGELOG|版本中心|release|tag)", first_screen):
                warnings.append("repository has Git tags but the first screen has no clear version/Release entry")

        present_manifests = [name for name in MANIFESTS if (root / name).exists()]
        if present_manifests and not any(name in text for name in present_manifests):
            warnings.append("README does not mention any detected dependency manifest")
        if (root / "LICENSE").exists() and not re.search(r"license|许可|授权", text, re.I):
            warnings.append("LICENSE exists but README does not explain licensing")
        if not (root / ".gitignore").exists():
            warnings.append("repository has no .gitignore")

        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARNING: {message}")
        print(
            f"Verified README and repository structure: {len(errors)} error(s), "
            f"{len(warnings)} warning(s), {len(local_images)} local image(s)."
        )
        return 1 if errors or (args.strict and warnings) else 0
    except (OSError, RuntimeError, UnicodeError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
