#!/usr/bin/env python3
"""Versioned package integrity and optional installed-copy comparison (offline)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MANIFEST = "package-manifest.json"
IGNORED = {"__pycache__", ".git", ".pytest_cache"}


def inventory(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(p in IGNORED for p in relative.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError("package contains a symlink")
        if path.is_file() and relative.as_posix() != MANIFEST:
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def version(root: Path) -> str:
    value = (root / "VERSION").read_text(encoding="utf-8-sig").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", value):
        raise ValueError("invalid package version")
    return value


def build(root: Path) -> None:
    files = inventory(root)
    if not {"SKILL.md", "LICENSE", "VERSION"}.issubset(files):
        raise ValueError("package requires SKILL.md, LICENSE and VERSION")
    data = {"schema_version": 1, "version": version(root), "files": files}
    (root / MANIFEST).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def verify(root: Path, installed: Path | None = None) -> list[str]:
    data = json.loads((root / MANIFEST).read_text(encoding="utf-8-sig"))
    errors = []
    if data["schema_version"] != 1 or data["version"] != version(root):
        errors.append("manifest schema/version differs from package")
    actual, recorded = inventory(root), data["files"]
    if not {"SKILL.md", "LICENSE", "VERSION"}.issubset(recorded):
        errors.append("manifest lacks required package files")
    for name in sorted(set(actual) | set(recorded)):
        if actual.get(name) != recorded.get(name):
            errors.append(f"package differs from manifest: {name}")
    if installed is not None:
        installed_files = inventory(installed)
        for name in sorted(set(actual) | set(installed_files)):
            if actual.get(name) != installed_files.get(name):
                errors.append(f"installed copy differs: {name}")
        if not (installed / MANIFEST).is_file() or (installed / MANIFEST).read_bytes() != (root / MANIFEST).read_bytes():
            errors.append("installed manifest differs or is missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build-manifest", "verify"))
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--installed", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build-manifest":
            if args.installed:
                parser.error("--installed is only supported with verify")
            build(args.package)
            print(f"Recorded package {version(args.package)}. Run tests before publishing.")
            return 0
        errors = verify(args.package, args.installed)
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Package {version(args.package)}: {len(errors)} error(s). No files modified.")
        return 1 if errors else 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print(f"Package check could not complete ({type(exc).__name__}).", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
