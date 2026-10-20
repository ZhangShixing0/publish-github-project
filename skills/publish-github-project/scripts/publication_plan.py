#!/usr/bin/env python3
"""Local publication records; structural/hash checks do not prove semantic accuracy."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from verify_project import image_references
from readme_content import has_content, has_mermaid, one_section, sections, without_fenced_code

PROFILES = {
    "app": ["problem", "evidence", "workflow", "start", "limits"],
    "tool": ["problem", "example", "start", "usage", "limits"],
    "skill": ["problem", "deliverables", "workflow", "start", "limits"],
}
ALIASES = {
    "problem": r"解决.*问题|用途|项目介绍|简介|problem|overview|introduction|why",
    "evidence": r"演示|视频|截图|运行界面|产品一览|demo|screenshots?",
    "workflow": r"流程|协作|workflow|how it works",
    "start": r"快速开始|安装|quick\s*start|getting\s*started|installation",
    "limits": r"边界|限制|许可|安全|limitations?|licen[cs]e|security",
    "example": r"示例|examples?|usage|用法",
    "usage": r"使用|用法|usage|commands?",
    "deliverables": r"交付|解决.*问题|功能|outputs?|features?|problem",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def body_hash(body: str) -> str:
    return hashlib.sha256(body.strip().replace("\r\n", "\n").encode()).hexdigest()



def local_asset(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("asset path must stay within the target repository")
    return path


def initialize(root: Path, output: Path, profile: str, scope: str) -> None:
    root, output = root.resolve(), output.resolve()
    if output.is_relative_to(root):
        raise ValueError("keep publication records outside the repository")
    baseline = output.with_suffix(".baseline.md")
    if output.exists() or baseline.exists():
        raise ValueError("record already exists; review it instead of overwriting")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8-sig") if readme.exists() else ""
    current = sections(text)
    modules = []
    if scope != "media":
        for key in PROFILES[profile]:
            found = next((s["title"] for s in current if re.search(ALIASES[key], s["title"], re.I)), "")
            modules.append({"role": key, "heading": found, "omit_reason": ""})
    plan = {
        "schema_version": 1, "profile": profile, "scope": scope,
        "baseline": {"file": baseline.name, "sha256": ""},
        "modules": modules, "order_note": "",
        "preserve": [{"source": s["title"], "target": s["title"], "action": "keep", "review_note": ""}
                     for s in current if s["level"] == 2],
        "diagram": {"kind": "undecided", "reason": "", "heading": "", "path": ""},
        "media": [], "retired_paths": [], "retired_references": [],
    }
    if scope == "media":
        plan["diagram"] = {"kind": "unchanged", "reason": "Media-only update", "heading": "", "path": ""}
    output.parent.mkdir(parents=True, exist_ok=True)
    baseline.write_bytes(readme.read_bytes() if readme.exists() else b"")
    plan["baseline"]["sha256"] = sha256(baseline)
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_plan(root: Path, plan_path: Path) -> list[str]:
    """Fail closed on incomplete records; never print source media contents/URLs."""
    root, plan_path = root.resolve(), plan_path.resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    if plan.get("schema_version") != 1 or plan.get("profile") not in PROFILES:
        return ["unsupported publication plan schema/profile"]
    if plan.get("scope") not in {"initial", "readme", "media"}:
        return ["unsupported publication scope"]
    text = (root / "README.md").read_text(encoding="utf-8-sig")
    current = sections(text)
    errors = []
    baseline = plan_path.parent / plan["baseline"]["file"]
    if sha256(baseline) != plan["baseline"]["sha256"]:
        return ["baseline changed; recapture only after reviewing the task scope"]
    before = sections(baseline.read_text(encoding="utf-8-sig"))
    expected = [s for s in before if s["level"] == 2]
    records = plan["preserve"]
    if sorted(r["source"] for r in records) != sorted(s["title"] for s in expected):
        errors.append("preservation mapping does not cover every baseline H2 section exactly once")
    for record in records:
        source = one_section(expected, record["source"])
        target = one_section(current, record["target"])
        action = record["action"]
        if source is None:
            errors.append("preservation source is absent or ambiguous")
        if action == "remove":
            if not record.get("review_note", "").strip():
                errors.append("removing baseline content needs a concrete review note")
        elif action in {"keep", "rewrite", "move"}:
            if not target or not has_content(target["body"]):
                errors.append(f"preserved content has no populated target section: {record['target']}")
            elif source and action in {"keep", "move"} and body_hash(source["body"]) != body_hash(target["body"]):
                errors.append(f"preserved content changed without a rewrite review: {record['source']}")
            if action == "rewrite" and not record.get("review_note", "").strip():
                errors.append("rewritten content needs a note recording semantic comparison")
        else:
            errors.append("unknown preservation action")

    modules = plan["modules"]
    required = set(PROFILES[plan["profile"]]) if plan["scope"] != "media" else set()
    if not required.issubset({m["role"] for m in modules}):
        errors.append("profile modules are missing; record justified omissions explicitly")
    positions = []
    for module in modules:
        if module.get("omit_reason", "").strip():
            continue
        section = one_section(current, module["heading"])
        if not section or not has_content(section["body"]):
            errors.append(f"planned module has no populated, unique section: {module['role']}")
        else:
            positions.append(section["line"])
    if positions != sorted(positions) and not plan.get("order_note", "").strip():
        errors.append("module order differs from the plan; record the reader-facing reason")

    diagram = plan["diagram"]
    kind = diagram["kind"]
    if kind in {"none", "unchanged"}:
        if not diagram.get("reason", "").strip():
            errors.append("diagram omission/preservation needs a reason")
        if kind == "unchanged" and plan["scope"] != "media":
            errors.append("evaluate diagram needs during a README/initial publication")
    elif kind in {"mermaid", "image"}:
        section = one_section(current, diagram["heading"])
        if not section:
            errors.append("planned diagram section is absent or ambiguous")
        elif kind == "mermaid":
            if not has_mermaid(section["body"]):
                errors.append("planned Mermaid diagram is missing")
        else:
            path = local_asset(root, diagram["path"])
            sources = {ref.source for ref in image_references(section["body"])}
            if not path.is_file() or diagram["path"] not in sources:
                errors.append("planned image diagram is missing or not referenced in its section")
    else:
        errors.append("diagram decision is incomplete")

    for index, media in enumerate(plan["media"], 1):
        label = f"media item {index}"
        source = Path(media["source_file"])
        if not source.is_absolute():
            source = plan_path.parent / source
        published = local_asset(root, media["published_path"])
        if sha256(source) != media["source_sha256"]:
            errors.append(f"{label}: source version changed")
        output_hash = sha256(published)
        if output_hash != media["published_sha256"]:
            errors.append(f"{label}: publication candidate changed")
        transform = media["transform"]
        if transform == "original":
            if output_hash != media["source_sha256"]:
                errors.append(f"{label}: original must match source bytes exactly")
        elif transform in {"transcode", "redact", "edit"}:
            if not media.get("decision_note", "").strip() or not media.get("review_note", "").strip():
                errors.append(f"{label}: transformation requires its own decision and review")
        else:
            errors.append(f"{label}: unknown transformation")
        references = media.get("references", [])
        if not references:
            errors.append(f"{label}: missing publication reference")
        for reference in references:
            if reference not in text:
                errors.append(f"{label}: expected README reference missing")
        if not media.get("privacy_review", "").strip():
            errors.append(f"{label}: privacy decision not recorded for this source version")
    if plan["scope"] == "media" and not plan["media"]:
        errors.append("media update needs at least one versioned media item")
    for path in plan["retired_paths"]:
        if local_asset(root, path).exists():
            errors.append("retired asset still exists in the candidate tree")
    visible = without_fenced_code(text)
    for reference in plan["retired_references"]:
        if reference and reference in visible:
            errors.append("retired media reference remains in README")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Capture a baseline and draft a local task record")
    init.add_argument("repository", type=Path)
    init.add_argument("--output", type=Path, required=True)
    init.add_argument("--profile", choices=PROFILES, required=True)
    init.add_argument("--scope", choices=("initial", "readme", "media"), required=True)
    check = sub.add_parser("verify")
    check.add_argument("repository", type=Path)
    check.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.repository, args.output, args.profile, args.scope)
            print("Created local draft and baseline; resolve the decisions before verification.")
            return 0
        errors = verify_plan(args.repository, args.plan)
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Publication plan: {len(errors)} error(s). Semantic, privacy and live rendering review remain separate.")
        return 1 if errors else 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"Publication plan could not be checked ({type(exc).__name__}). Check schema and local files.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
