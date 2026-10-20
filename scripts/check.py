#!/usr/bin/env python3
"""Run offline repository checks using the Python standard library and Git."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "publish-github-project" / "scripts"


def main():
    if sys.version_info < (3, 10):
        print("Python 3.10+ is required.", file=sys.stderr)
        return 2
    # Keep test fixtures in a predictable, ignored project-local location.
    work = ROOT / ".test-work"
    work.mkdir(exist_ok=True)
    previous_temp = tempfile.tempdir
    tempfile.tempdir = str(work)
    sys.path.insert(0, str(SCRIPTS))
    try:
        suite = unittest.defaultTestLoader.discover(str(SCRIPTS), pattern="test_*.py")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        tempfile.tempdir = previous_temp
    if not result.wasSuccessful():
        return 1
    for name, flags in (
        ("verify_project.py", ["--strict", "--visual", "--header-style", "preserve",
                               "--header-note", "Retain the owner's approved cover and existing README opening"]),
        ("audit_repository.py", []),
    ):
        outcome = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(SCRIPTS / name), str(ROOT), *flags],
            cwd=ROOT,
            check=False,
        )
        if outcome.returncode:
            return outcome.returncode
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "skill_package.py"), "verify"],
        cwd=ROOT, check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
