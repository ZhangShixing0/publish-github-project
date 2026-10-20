#!/usr/bin/env python3
"""Render the skill's fixed badge style from a repository-owned JSON manifest."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys
import unicodedata

STYLE = "flat-square-v1"
STYLES = {STYLE, "forest-v1"}
COLORS = {
    "version": "#456a63",
    "platform": "#a86b3a",
    "technology": "#456a63",
    "runtime": "#427d89",
    "license": "#686d74",
    "status": "#686d74",
}
FONT = "'Segoe UI','Microsoft YaHei',sans-serif"


def text_width(text: str) -> int:
    return max(44, 20 + sum(12 if unicodedata.east_asian_width(c) in "WF" else 8 for c in text))


def render(label: str, value: str, left: int | None = None, right: int | None = None,
           *, style: str = STYLE, category: str | None = None) -> str:
    for text in (label, value):
        if not isinstance(text, str) or not text.strip() or len(text) > 40 or any(ord(c) < 32 for c in text):
            raise ValueError("badge label/value must contain 1-40 printable characters")
    left = text_width(label) if left is None else left
    right = text_width(value) if right is None else right
    if any(type(w) is not int or not 24 <= w <= 600 for w in (left, right)):
        raise ValueError("badge widths must be integers between 24 and 600")
    if style not in STYLES:
        raise ValueError("unknown badge style")
    width = left + right
    if style == STYLE:
        if category not in COLORS:
            raise ValueError("flat-square badges require a supported category")
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" viewBox="0 0 {width} 20" role="img" aria-labelledby="title desc">
<title id="title">{escape(label)}: {escape(value)}</title>
<desc id="desc">Project information: {escape(label)} {escape(value)}.</desc>
<rect width="{left}" height="20" fill="#555555"/>
<rect x="{left}" width="{right}" height="20" fill="{COLORS[category]}"/>
<g font-family="Verdana,Arial,'Microsoft YaHei',sans-serif" font-size="11" fill="#ffffff" text-anchor="middle">
<text x="{left/2}" y="14">{escape(label)}</text>
<text x="{left+right/2}" y="14">{escape(value)}</text>
</g></svg>
'''
    # Preserve bytes for accepted forest-v1 manifests; changing the default
    # must not restyle unrelated projects when their checks run.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="26" viewBox="0 0 {width} 26" role="img" aria-labelledby="title desc">
<title id="title">{escape(label)}: {escape(value)}</title>
<desc id="desc">Project information: {escape(label)} {escape(value)}.</desc>
<rect width="{width}" height="26" rx="5" fill="#eaf0e9"/>
<path d="M5 0h{left-5}v26H5a5 5 0 0 1-5-5V5a5 5 0 0 1 5-5Z" fill="#234e40"/>
<g font-family="{FONT}" font-size="12" text-anchor="middle">
<text x="{left/2}" y="17.5" fill="#ffffff">{escape(label)}</text>
<text x="{left+right/2}" y="17.5" font-weight="600" fill="#234e40">{escape(value)}</text>
</g></svg>
'''


def outputs(manifest: Path) -> list[tuple[Path, str]]:
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if data.get("style") not in STYLES or not isinstance(data.get("badges"), list) or not data["badges"]:
        raise ValueError("manifest requires a supported style and a nonempty badges list")
    result, seen = [], set()
    for badge in data["badges"]:
        filename = badge["file"]
        if not isinstance(filename, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*\.svg", filename) or filename in seen:
            raise ValueError("badge filenames must be unique lowercase SVG basenames")
        seen.add(filename)
        if not isinstance(badge.get("evidence"), str) or not badge["evidence"].strip():
            raise ValueError("each badge needs an evidence reference; manually verify its claim")
        target = manifest.parent / filename
        if target.is_symlink():
            raise ValueError("badge output must not be a symlink")
        result.append((target, render(badge["label"], badge["value"], badge.get("label_width"), badge.get("value_width"),
                                      style=data["style"], category=badge.get("category"))))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="JSON manifest beside the generated SVG files")
    parser.add_argument("--check", action="store_true", help="Read-only: fail if any rendered badge differs")
    args = parser.parse_args()
    try:
        rendered = outputs(args.manifest)
        different = []
        for path, text in rendered:
            if args.check:
                if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
                    different.append(path.name)
            else:
                path.write_text(text, encoding="utf-8", newline="\n")
        if different:
            print("Badge style/content differs: " + ", ".join(different))
            return 1
        print(f"{'Checked' if args.check else 'Rendered'} {len(rendered)} badges using the manifest style. Evidence needs manual review.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Badge rendering could not complete ({type(exc).__name__}).", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
