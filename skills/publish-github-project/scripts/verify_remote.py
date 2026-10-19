#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


BLOCKED_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
RISKY_SUFFIXES = {".xls", ".xlsx", ".zip", ".7z", ".sqlite", ".sqlite3", ".db"}


def run(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def repository_root(path: Path) -> Path:
    output = run(path, "rev-parse", "--show-toplevel")
    return Path(output).resolve()


def github_api(host: str, repository: str, endpoint: str) -> dict:
    result = subprocess.run(
        ["gh", "api", "--hostname", host, "--method", "GET", f"repos/{repository}/{endpoint}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "GitHub API read failed")
    return json.loads(result.stdout)


def github_snapshot(host: str, repository: str, branch: str) -> tuple[str, dict[str, str]]:
    reference = github_api(host, repository, "git/ref/heads/" + quote(branch, safe="/"))
    sha = reference["object"]["sha"]
    commit = github_api(host, repository, "git/commits/" + sha)
    tree = github_api(host, repository, "git/trees/" + commit["tree"]["sha"] + "?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("GitHub returned a truncated tree; full file verification is incomplete")
    return sha, {entry["path"]: entry["sha"] for entry in tree["tree"] if entry["type"] in {"blob", "commit"}}


def git_tree(root: Path, sha: str) -> dict[str, str]:
    files = {}
    for entry in run(root, "ls-tree", "-r", "-z", sha).split("\0"):
        if entry:
            metadata, name = entry.split("\t", 1)
            files[name] = metadata.split()[2]
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a published branch SHA and file tree via Git or read-only GitHub API. Metadata, CI and rendered media require separate checks.")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch")
    parser.add_argument("--offline", action="store_true", help="Compare against the local remote-tracking ref without network access.")
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--transport", choices=("git", "github-api"), default="git")
    parser.add_argument("--github-repo", help="Explicit OWNER/REPO for GitHub API verification.")
    parser.add_argument("--github-host", default="github.com", help="GitHub host for the authenticated gh CLI.")
    parser.add_argument("--expected-sha", help="Full intended commit SHA, including commits created through an API; defaults to local HEAD.")
    parser.add_argument("--file-manifest", type=Path, help="JSON object mapping intended repository-relative paths to Git blob IDs (not SHA-256 file hashes).")
    args = parser.parse_args()
    if args.transport == "github-api" and (args.offline or not args.github_repo):
        parser.error("github-api requires --github-repo and cannot be combined with --offline")
    if args.github_repo and not re.fullmatch(r"[\w.-]+/[\w.-]+", args.github_repo):
        parser.error("--github-repo must be OWNER/REPO")
    if args.expected_sha and not re.fullmatch(r"(?:[a-fA-F0-9]{40}|[a-fA-F0-9]{64})", args.expected_sha):
        parser.error("--expected-sha must be a full hexadecimal commit ID")

    try:
        root = repository_root(Path(args.repository).resolve())
        branch = args.branch or run(root, "branch", "--show-current")
        if not branch:
            raise RuntimeError("detached HEAD; pass --branch explicitly")
        dirty = run(root, "status", "--porcelain")
        if dirty and not args.allow_dirty:
            print("ERROR: working tree is not clean")
            return 1

        expected_sha = args.expected_sha.lower() if args.expected_sha else run(root, "rev-parse", "HEAD")
        if args.transport == "github-api":
            remote_sha, tree = github_snapshot(args.github_host, args.github_repo, branch)
            source = f"GitHub API ({args.github_host}/{args.github_repo})"
        elif args.offline:
            remote_sha = run(root, "rev-parse", f"refs/remotes/{args.remote}/{branch}")
            source = "local remote-tracking ref"
        else:
            lines = run(root, "ls-remote", args.remote, f"refs/heads/{branch}").splitlines()
            if not lines:
                raise RuntimeError(f"remote branch not found: {args.remote}/{branch}")
            remote_sha = lines[0].split()[0]
            source = "remote"

        if args.transport == "git":
            tree = git_tree(root, remote_sha)

        errors: list[str] = []
        warnings: list[str] = []
        if expected_sha != remote_sha:
            errors.append(f"intended commit {expected_sha[:12]} does not match {source} {remote_sha[:12]}")
        if args.file_manifest:
            manifest = json.loads(args.file_manifest.read_text(encoding="utf-8-sig"))
            if not isinstance(manifest, dict) or not all(isinstance(p, str) and isinstance(oid, str) and re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", oid) for p, oid in manifest.items()):
                raise RuntimeError("file manifest must map repository-relative paths to full Git blob IDs")
            for name, oid in manifest.items():
                if tree.get(name) != oid.lower():
                    errors.append(f"published file is missing or differs from the intended blob: {name}")

        for relative in tree:
            path = Path(relative)
            lowered = relative.replace("\\", "/").lower()
            if path.name.lower() in BLOCKED_NAMES or (path.name.lower().startswith(".env.") and not path.name.lower().endswith((".example", ".sample", ".template"))):
                errors.append(f"blocked filename is published: {relative}")
            if path.suffix.lower() in RISKY_SUFFIXES:
                warnings.append(f"review published data/archive file: {relative}")
            if lowered.startswith(("tmp/", "work/", "outputs/", "runtime/")) and lowered not in {"outputs/.gitkeep"}:
                errors.append(f"runtime path is published: {relative}")

        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARNING: {message}")
        print(f"Verified {args.remote}/{branch} at {remote_sha[:12]} using {source}: {len(errors)} error(s), {len(warnings)} warning(s).")
        print("Scope: branch SHA, file tree, and supplied blob IDs only; metadata, CI, content privacy and rendering are separate checks.")
        return 1 if errors else 0
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        print(f"Remote verification failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
