#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


TEXT_SUFFIXES = {
    "", ".bat", ".c", ".cfg", ".conf", ".cpp", ".css", ".csv", ".env",
    ".example", ".go", ".h", ".html", ".ini", ".java", ".js", ".json",
    ".jsx", ".md", ".mjs", ".php", ".properties", ".ps1", ".py", ".rb",
    ".rs", ".service", ".sh", ".sql", ".toml", ".ts", ".tsx", ".txt",
    ".xml", ".yaml", ".yml", ".svg",
}
OOXML_SUFFIXES = {".docx", ".xlsx", ".pptx"}
HIGH_RISK_BINARY_SUFFIXES = {
    ".7z", ".dat", ".db", ".doc", ".docx", ".gz", ".jpeg", ".jpg", ".pdf",
    ".png", ".sqlite", ".sqlite3", ".tar", ".xls", ".xlsx", ".zip",
    ".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".mp3", ".m4a",
    ".wav", ".aac", ".ogg", ".flac", ".webp", ".gif", ".avif", ".pptx",
}
MAX_TEXT_BYTES = 8 * 1024 * 1024
MAX_XML_BYTES = 32 * 1024 * 1024
RUNTIME_PREFIXES = ("tmp/", "temp/", "outputs/", "output/", "work/", "runtime/", "data/cases/")
SAFE_ENV_NAMES = {".env.example", ".env.sample", ".env.template"}
TEST_MARKERS = ("test", "demo", "example", "sample", "测试", "示例", "虚构")


@dataclass
class Finding:
    level: str
    category: str
    path: str
    message: str


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("utf-8", errors="surrogateescape")


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


def candidate_paths(root: Path) -> list[str]:
    raw = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    return sorted(item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item)


def index_entries(root: Path) -> dict[str, tuple[str, str]]:
    entries = {}
    for entry in git(root, "ls-files", "--stage", "-z").split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, oid, stage = metadata.split()
        if stage != "0":
            raise RuntimeError("resolve index conflicts before auditing publication")
        entries[name] = (mode, oid)
    return entries


class ScanLimit(Exception):
    pass


def decode_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def text_surfaces(path: Path, raw: bytes | None = None) -> list[str]:
    eligible = path.suffix.lower() in TEXT_SUFFIXES | OOXML_SUFFIXES or path.name.lower().startswith(".env")
    if not eligible:
        return []
    if (len(raw) if raw is not None else path.stat().st_size) > MAX_TEXT_BYTES:
        raise ScanLimit("text/document exceeds automatic scan size; review separately")
    if raw is None:
        raw = path.read_bytes()
    if path.suffix.lower() in OOXML_SUFFIXES and zipfile.is_zipfile(io.BytesIO(raw)):
        surfaces: list[str] = []
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = [info for info in archive.infolist() if info.filename.lower().endswith((".xml", ".rels"))]
            if sum(info.file_size for info in members) > MAX_XML_BYTES:
                raise ScanLimit("expanded document exceeds automatic scan size; review separately")
            for info in members:
                surfaces.append(decode_text(archive.read(info)))
        return surfaces
    if path.suffix.lower() in TEXT_SUFFIXES or path.name.lower().startswith(".env"):
        return [decode_text(raw)]
    return []


def placeholder(value: str) -> bool:
    lowered = value.strip().strip("'\"").lower()
    return (
        not lowered
        or lowered.startswith(("your_", "replace_", "example_", "demo_", "test_", "changeme"))
        or lowered in {"xxx", "xxxx", "placeholder", "none", "null"}
        or (len(lowered) >= 4 and set(lowered) <= {"x", "*", "0", "-", "_"})
        or "${" in lowered
        or "<" in lowered
    )


def valid_cn_id(value: str) -> bool:
    if not re.fullmatch(r"\d{17}[\dXx]", value) or value.startswith("000000"):
        return False
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    checks = "10X98765432"
    return checks[sum(int(value[i]) * weights[i] for i in range(17)) % 11] == value[-1].upper()


def credential_key(name: str) -> bool:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    return bool(re.search(r"(?:^|[_.-])(?:secret|token|password|passwd|private_?key|api_?key)(?:$|[_.-])", normalized))


def credential_fields(relative: str, text: str) -> set[str]:
    fields: set[str] = set()
    # JSON may be compact and nested; line-oriented patterns alone miss it.
    if Path(relative).suffix.lower() == ".json":
        try:
            pending = [json.loads(text)]
        except ValueError:
            pending = []
        while pending:
            item = pending.pop()
            if isinstance(item, dict):
                for key, value in item.items():
                    if credential_key(key) and isinstance(value, str) and not placeholder(value):
                        fields.add(key)
                    if isinstance(value, (dict, list)):
                        pending.append(value)
            elif isinstance(item, list):
                pending.extend(value for value in item if isinstance(value, (dict, list)))
    assignment = re.compile(r'''(?m)^\s*(?:(?:export|const|let|var)\s+)?["']?([A-Za-z_][\w.-]*)["']?\s*[:=]\s*(.*?)\s*$''')
    source_code = Path(relative).suffix.lower() in {".py", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs"}
    for match in assignment.finditer(text):
        name, expression = match.groups()
        if not credential_key(name):
            continue
        literal = re.fullmatch(r'''(["'])(.*?)\1\s*[,;]?\s*(?:(?:#|//).*)?''', expression)
        if literal:
            value = literal.group(2)
        elif not source_code and re.fullmatch(r"[^\s(){}]+(?:\s+#.*)?", expression):
            value = expression.split(" #", 1)[0]
        else:
            continue  # Environment lookups and expressions are not embedded credentials.
        if not placeholder(value) and not value.isdigit():
            fields.add(name)
    return fields


def inspect_text(relative: str, text: str, deny_terms: list[str], findings: list[Finding]) -> None:
    is_vendored = any(part in relative.lower().split("/") for part in ("vendor", "node_modules", ".venv", "site-packages"))
    for term in deny_terms:
        if term and term in text:
            findings.append(Finding("error", "deny-term", relative, "matched a user-supplied blocked marker"))
            break

    if not is_vendored:
        for name in sorted(credential_fields(relative, text)):
            findings.append(Finding("error", "secret", relative, f"non-placeholder credential assignment: {name}"))

    if re.search(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----", text):
        findings.append(Finding("error", "private-key", relative, "contains a private-key block"))
    if re.search(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b", text):
        findings.append(Finding("error", "github-token", relative, "contains a GitHub token pattern"))

    if not is_vendored:
        ids = {m.group(0) for m in re.finditer(r"(?<!\d)\d{17}[\dXx](?!\d)", text)}
        if any(valid_cn_id(value) for value in ids):
            findings.append(Finding("error", "identity-number", relative, "contains a checksum-valid Chinese identity number"))

        phones = {m.group(0) for m in re.finditer(r"(?<!\d)1[3-9]\d{9}(?!\d)", text)}
        unsafe_phones = {phone for phone in phones if not phone.startswith("1990000000")}
        if unsafe_phones:
            findings.append(Finding("error", "phone", relative, "contains a real-looking mobile number"))

        entity_pattern = re.compile(
            r"(?i)(?:[\"'](?:defendant_name|borrower_name|customer_name|plaintiff_name|company_name|借款人姓名|被告姓名|客户姓名)[\"']"
            r"|\b(?:defendant_name|borrower_name|customer_name|plaintiff_name|company_name)\b)"
            r"\s*:\s*[\"']([^\"']{2,80})[\"']"
        )
        for match in entity_pattern.finditer(text):
            raw_value = match.group(1).strip()
            value = raw_value.lower()
            label_values = {"姓名", "名称", "借款人姓名", "被告姓名", "客户姓名", "原告名称", "公司名称"}
            person_like = bool(re.fullmatch(r"[\u4e00-\u9fff·]{2,4}", raw_value)) and raw_value not in label_values
            organization_like = bool(re.search(r"(?:公司|银行|律所|律师事务所|中心|集团)$", raw_value))
            if (person_like or organization_like) and not any(marker in value for marker in TEST_MARKERS):
                findings.append(Finding("warning", "entity-review", relative, "literal person or organization field is not marked as test data"))
                break


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Git publication candidates without printing sensitive values.")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--deny", action="append", default=[], help="Additional exact marker to block; repeatable.")
    parser.add_argument("--deny-file", type=Path, help="UTF-8 file containing one blocked marker per line.")
    parser.add_argument("--strict-binaries", action="store_true", help="Treat high-risk binary candidates as errors.")
    parser.add_argument("--staged", action="store_true", help="Audit the full Git index bytes that the next commit would contain, excluding untracked/unstaged content.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        root = repository_root(Path(args.repository).resolve())
        deny_terms = list(args.deny)
        if args.deny_file:
            deny_terms.extend(
                line.strip() for line in args.deny_file.read_text(encoding="utf-8-sig").splitlines() if line.strip()
            )
        findings: list[Finding] = []
        entries = index_entries(root) if args.staged else {}
        paths = sorted(entries) if args.staged else candidate_paths(root)
        for relative in paths:
            normalized = relative.replace("\\", "/")
            lowered = normalized.lower()
            path = root / relative
            name = path.name.lower()

            if (name == ".env" or name.startswith(".env.")) and name not in SAFE_ENV_NAMES and not name.endswith((".example", ".sample", ".template")):
                findings.append(Finding("error", "environment", normalized, "environment file is a publication candidate"))
            if lowered.startswith(RUNTIME_PREFIXES) and lowered not in {"outputs/.gitkeep", "output/.gitkeep"}:
                findings.append(Finding("error", "runtime-output", normalized, "runtime/output path is a publication candidate"))
            for term in deny_terms:
                if term and term in normalized:
                    findings.append(Finding("error", "deny-term-path", normalized, "filename matched a user-supplied blocked marker"))
                    break
            if path.suffix.lower() in HIGH_RISK_BINARY_SUFFIXES:
                level = "error" if args.strict_binaries else "warning"
                findings.append(Finding(level, "binary-review", normalized, "high-risk binary file requires explicit review"))
            if (args.staged and entries[relative][0] == "120000") or (not args.staged and path.is_symlink()):
                findings.append(Finding("warning", "symlink-review", normalized, "symbolic link requires target review; external content was not read"))
                continue
            if args.staged and entries[relative][0] == "160000":
                findings.append(Finding("warning", "submodule-review", normalized, "submodule contents require a separate audit"))
                continue
            try:
                if args.staged:
                    if path.suffix.lower() not in TEXT_SUFFIXES | OOXML_SUFFIXES and not name.startswith(".env"):
                        continue
                    oid = entries[relative][1]
                    if int(git(root, "cat-file", "-s", oid)) > MAX_TEXT_BYTES:
                        raise ScanLimit("text/document exceeds automatic scan size; review separately")
                    raw = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", oid])
                    surfaces = text_surfaces(path, raw)
                elif path.is_file():
                    if not path.resolve().is_relative_to(root):
                        findings.append(Finding("error", "external-path", normalized, "candidate resolves outside the repository; content was not read"))
                        continue
                    surfaces = text_surfaces(path)
                else:
                    continue
                for surface in surfaces:
                    inspect_text(normalized, surface, deny_terms, findings)
            except ScanLimit as exc:
                findings.append(Finding("warning", "scan-limit", normalized, str(exc)))

        unique = {(f.level, f.category, f.path, f.message): f for f in findings}
        findings = sorted(unique.values(), key=lambda f: (f.level != "error", f.path, f.category))
        errors = sum(f.level == "error" for f in findings)
        warnings = sum(f.level == "warning" for f in findings)
        if args.as_json:
            print(json.dumps({"root": str(root), "source": "index" if args.staged else "working-tree", "files": len(paths), "errors": errors, "warnings": warnings, "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
        else:
            for finding in findings:
                print(f"{finding.level.upper()} [{finding.category}] {finding.path}: {finding.message}")
            print(f"Audited {len(paths)} publication candidates: {errors} error(s), {warnings} warning(s).")
        return 1 if errors else 0
    except (OSError, RuntimeError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
