"""Small, standard-library checks for the publishing skill's README opening.

This is deliberately not a Markdown renderer or a badge-claim verifier.
The supported default is blank-line-separated Markdown/HTML inside a center div.
"""
from __future__ import annotations

import re
import struct
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


def without_comments(text: str) -> str:
    return re.sub(r"<!--[\s\S]*?-->", lambda m: "\n" * m[0].count("\n"), text)


def is_badge(source: str) -> bool:
    url = urlsplit(source)
    host = (url.hostname or "").lower()
    path = unquote(url.path).replace("\\", "/").lower()
    if host in {"img.shields.io", "badgen.net", "codecov.io", "coveralls.io"}:
        return True
    parts = path.split("/")
    # A stable path convention recognizes offline badges without guessing from
    # aspect ratio (which would also classify small logos as badges).
    return (
        "badges" in parts or "badge" in parts
        or bool(re.search(r"(?:^|[-_/])badge(?:[-_.]|$)", path))
    )


def semantic_h1_count(text: str) -> int:
    return len(re.findall(r"(?im)^ {0,3}#\s+\S|<h1\b", text))


class Alignment(HTMLParser):
    """Record rendered-text/image alignment, including explicit nested overrides."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack: list[tuple[str, str]] = []
        self.lines: dict[int, list[bool]] = {}

    def centered(self):
        return bool(self.stack and self.stack[-1][1] == "center")

    def mark(self, line):
        self.lines.setdefault(line, []).append(self.centered())

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        inherited = self.stack[-1][1] if self.stack else "left"
        align = (attrs.get("align") or inherited).lower()
        if tag == "center":
            align = "center"
        if tag not in self.VOID:
            self.stack.append((tag, align))
        if tag in {"img", "source"}:
            self.mark(self.getpos()[0])

    def handle_startendtag(self, tag, attributes):
        self.handle_starttag(tag, attributes)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        start = self.getpos()[0]
        for offset, line in enumerate(data.splitlines()):
            if line.strip():
                self.mark(start + offset)


def dimensions(path: Path) -> tuple[float, float] | None:
    """Read common local Hero dimensions without an image-library dependency."""
    try:
        with path.open("rb") as stream:
            head = stream.read(24)
            if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) == 24:
                return struct.unpack(">II", head[16:24])
            if head[:2] == b"\xff\xd8":
                stream.seek(2)
                while marker := stream.read(1):
                    if marker != b"\xff":
                        continue
                    while (code := stream.read(1)) == b"\xff":
                        pass
                    if not code or code in {b"\xd9", b"\xda"}:
                        break
                    if code[0] in {0x01, *range(0xD0, 0xD9)}:
                        continue
                    size_data = stream.read(2)
                    if len(size_data) != 2:
                        break
                    size = struct.unpack(">H", size_data)[0]
                    if size < 2:
                        break
                    if code[0] in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                        frame = stream.read(5)
                        if len(frame) == 5:
                            height, width = struct.unpack(">HH", frame[1:])
                            return width, height
                        break
                    stream.seek(size - 2, 1)
        if path.suffix.lower() == ".svg":
            svg = ET.parse(path).getroot()
            view = re.split(r"[\s,]+", svg.get("viewBox", "").strip())
            if len(view) == 4:
                return float(view[2]), float(view[3])
            w, h = svg.get("width", ""), svg.get("height", "")
            if re.fullmatch(r"[\d.]+(?:px)?", w) and re.fullmatch(r"[\d.]+(?:px)?", h):
                return float(w.removesuffix("px")), float(h.removesuffix("px"))
    except (OSError, ValueError, ET.ParseError, struct.error):
        pass
    return None


def opening_issues(text: str, images, root: Path, readme: Path, style: str) -> list[str]:
    """Accept text with fenced examples/comments already blanked out."""
    if style == "preserve":
        return []
    issues = []
    lines = text.splitlines()
    boundary = next((i for i, line in enumerate(lines)
                     if re.match(r"\s*(?:#{2,6}\s|>\s*\[!|<h[2-6]\b)", line, re.I)), len(lines))
    alignment = Alignment()
    alignment.feed(text)

    blocks: list[tuple[int, int, str]] = []
    current: list[str] = []
    start = 1
    for i, line in enumerate(lines[:boundary] + [""], 1):
        # Container-only lines are not content blocks; the HTML parser above
        # still tracks their effect on subsequent Markdown and body text.
        if re.fullmatch(r"\s*</?(?:div|center)\b[^>]*>\s*", line, re.I):
            line = ""
        if line.strip():
            if not current:
                start = i
            current.append(line)
        elif current:
            blocks.append((start, i - 1, "\n".join(current)))
            current = []

    roles = []
    hero = None
    badge_count = 0
    for start, end, block in blocks:
        refs = [r for r in images if start <= r.line <= end and r.requires_alt]
        if semantic_h1_count(block):
            role = "title"
        elif refs:
            badges = [r for r in refs if is_badge(r.source)]
            if badges and len(badges) == len(refs):
                role = "badges"
                badge_count += len({r.source for r in badges})
                # A linked badge includes a nested image, not a separate nav link.
                remainder = re.sub(r"\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)", "", block)
                remainder = re.sub(r"!\[[^\]]*\]\([^)]+\)|<img\b[^>]*>", "", remainder, flags=re.I)
                if re.search(r"\[[^\]]+\]\([^)]+\)|<a\b[^>]*>\s*[^<\s]", remainder, re.I):
                    issues.append("header: keep navigation separate from the badge paragraph")
            else:
                role = "hero"
                hero = hero or refs[0]
                if badges:
                    issues.append("header: Hero and badges must be separate blocks")
        else:
            links = len(re.findall(r"(?<!!)\[[^\]]+\]\([^)]+\)|<a\b[^>]*\bhref=", block, re.I))
            role = "navigation" if links >= 2 else "value"
        roles.append(role)
        centered = [v for n in range(start, end + 1) for v in alignment.lines.get(n, [])]
        if not centered or not all(centered):
            issues.append(f"header: {role} block at line {start} must be centered")

    expected = ["title", "hero", "value", "navigation", "badges"]
    if style == "compact" and "hero" not in roles:
        expected.remove("hero")
    if roles != expected:
        issues.append(f"header: expected {' -> '.join(expected)}; found {' -> '.join(roles) or 'no opening blocks'}")
    if badge_count == 0:
        issues.append("header: missing verified badge paragraph (local badges belong in a badges/ directory)")
    elif not 2 <= badge_count <= 5:
        issues.append(f"header: {badge_count} badges; review information coverage and use 2-5 useful badges, or document a layout exception")

    # Flag a centered callout/section boundary, including a div closed too late.
    for i, line in enumerate(lines[boundary:], boundary + 1):
        if re.match(r"\s*(?:#{2,6}\s|>|<h[2-6]\b)", line, re.I) and any(alignment.lines.get(i, [])):
            issues.append(f"header: body/callout is still centered at line {i}; close the identity block first")
            break

    if style == "showcase" and hero and not urlsplit(hero.source).scheme:
        path = (root / hero.source.lstrip("/")) if hero.source.startswith("/") else readme.parent / hero.source
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            return issues  # The main verifier reports the path escape.
        size = dimensions(path)
        if size and size[1] > 0 and size[0] / size[1] < 1.6:
            issues.append("header: local Hero is unusually tall for a full-width opening; reframe horizontally or document an intentional layout exception")
    return issues
