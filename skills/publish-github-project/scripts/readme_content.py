"""Small README section parser for structural checks, not a Markdown renderer."""
from __future__ import annotations

import re
from readme_header import without_comments


def has_mermaid(text: str) -> bool:
    fence, language, content = None, "", []
    for line in without_comments(text).splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is None and marker:
            fence, language, content = marker[1], marker[2].strip().lower(), []
        elif fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                if language == "mermaid" and "\n".join(content).strip():
                    return True
                fence = None
            else:
                content.append(line)
    return False


def without_fenced_code(markdown: str) -> str:
    markdown = without_comments(markdown)
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



def sections(text: str) -> list[dict]:
    """ATX, HTML and setext sections, with fences/comments excluded as headings."""
    visible = without_fenced_code(text)
    raw_lines = text.splitlines()
    lines = visible.splitlines()
    headings = []
    for i, line in enumerate(lines):
        match = re.match(r"^ {0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$", line)
        html = re.match(r"^\s*<h([1-6])(?:\s[^>]*)?>(.*?)</h\1>\s*$", line, re.I)
        if match:
            headings.append((i, i + 1, len(match[1]), match[2].strip()))
        elif html:
            headings.append((i, i + 1, int(html[1]), re.sub("<[^>]+>", "", html[2]).strip()))
        elif i and re.fullmatch(r" {0,3}(?:={3,}|-{3,})\s*", line) and lines[i - 1].strip():
            # Avoid interpreting table delimiters / list items as setext titles.
            if not re.match(r"^\s*[|>*#-]", lines[i - 1]):
                headings.append((i - 1, i + 1, 1 if "=" in line else 2, lines[i - 1].strip()))
    result = []
    for index, (start, content_start, level, title) in enumerate(headings):
        end = next((row[0] for row in headings[index + 1:] if row[2] <= level), len(raw_lines))
        result.append({"title": title, "level": level, "line": start + 1,
                       "body": "\n".join(raw_lines[content_start:end]).strip()})
    return result


def has_content(body: str) -> bool:
    # A heading, navigation link, comment or picture alone cannot explain meaning.
    value = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"<[^>]*>", "", value)
    value = re.sub(r"(?m)^#{1,6} .*?$|^[`~]{3,}.*?$", "", value)
    return bool(re.search(r"[\w\u4e00-\u9fff]", value))


def one_section(items: list[dict], title: str) -> dict | None:
    matches = [s for s in items if s["title"].casefold() == title.casefold()]
    return matches[0] if len(matches) == 1 else None
