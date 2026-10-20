from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

from publication_plan import initialize, sha256, verify_plan
from readme_content import has_mermaid, sections
from skill_package import build, verify


README = """# Sample

## Problem
Turn case materials into a reviewed draft.

## Workflow
An operator supplies files. Two roles extract and prepare a draft; a human checks the result.
<picture><source srcset="mobile.svg"><img src="workflow.svg" alt="Role handoffs"></picture>

## Quick start
Run the documented command with sample inputs.

## Tests
Run the repository checks.

## Security and license
Use synthetic data for demonstrations.
"""


class PublicationPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        self.readme = self.root / "README.md"
        self.readme.write_text(README, encoding="utf-8")
        for name in ("workflow.svg", "mobile.svg"):
            (self.root / name).write_text('<svg xmlns="http://www.w3.org/2000/svg"><title>Handoffs</title></svg>', encoding="utf-8")
        self.path = self.base / "plan.json"
        initialize(self.root, self.path, "skill", "readme")
        self.plan = json.loads(self.path.read_text(encoding="utf-8"))
        self.plan["diagram"] = {"kind": "image", "heading": "Workflow", "path": "workflow.svg"}
        self.plan["order_note"] = "Deliverables are explained together with the problem."
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.plan), encoding="utf-8")

    def errors(self):
        self.save()
        return verify_plan(self.root, self.path)

    def review_rewrite(self, heading):
        for record in self.plan["preserve"]:
            if record["source"] == heading:
                record["action"] = "rewrite"
                record["review_note"] = "Compared baseline responsibilities, inputs, handoffs and outputs."

    def test_existing_svg_workflow_passes_without_mermaid(self):
        self.assertEqual(self.errors(), [])

    def test_mobile_source_can_be_selected_as_the_diagram(self):
        self.plan["diagram"]["path"] = "mobile.svg"
        self.assertEqual(self.errors(), [])

    def test_removing_problem_body_fails_even_if_navigation_mentions_it(self):
        self.readme.write_text(README.replace("Turn case materials into a reviewed draft.", "[Problem](#problem)"), encoding="utf-8")
        self.assertTrue(any("populated" in e for e in self.errors()))

    def test_lost_handoff_is_detected_before_a_rewrite_is_reviewed(self):
        self.readme.write_text(README.replace("a human checks the result", "the draft is complete"), encoding="utf-8")
        self.assertTrue(any("rewrite review" in e for e in self.errors()))

    def test_reviewed_rewrite_is_allowed_but_still_needs_semantic_review(self):
        self.readme.write_text(README.replace("a human checks the result", "a reviewer confirms every field"), encoding="utf-8")
        self.review_rewrite("Workflow")
        self.assertEqual(self.errors(), [])

    def test_preservation_mapping_cannot_silently_omit_baseline_sections(self):
        self.plan["preserve"].pop()
        self.assertTrue(any("every baseline" in e for e in self.errors()))

    def test_changed_baseline_cannot_be_used_as_evidence(self):
        (self.base / self.plan["baseline"]["file"]).write_text("modified", encoding="utf-8")
        self.assertTrue(any("baseline changed" in e for e in self.errors()))

    def test_single_step_tool_can_omit_diagram_with_reason(self):
        self.plan["diagram"] = {"kind": "none", "reason": "A single conversion is clearer as input/output."}
        self.assertEqual(self.errors(), [])
        self.plan["diagram"]["reason"] = ""
        self.assertTrue(any("needs a reason" in e for e in self.errors()))

    def test_missing_or_unreferenced_diagram_fails(self):
        self.plan["diagram"]["path"] = "missing.svg"
        self.assertTrue(any("diagram is missing" in e for e in self.errors()))
        self.plan["diagram"]["path"] = "../secret.svg"
        with self.assertRaises(ValueError):
            self.errors()

    def test_diagram_decision_and_module_order_are_explicit(self):
        self.plan["diagram"] = {"kind": "undecided"}
        self.assertTrue(any("incomplete" in e for e in self.errors()))
        self.plan["order_note"] = ""
        self.plan["modules"].reverse()
        self.assertTrue(any("module order" in e for e in self.errors()))

    def test_mermaid_is_an_alternative_to_an_image(self):
        self.plan["diagram"] = {"kind": "mermaid", "heading": "Workflow"}
        self.assertTrue(any("Mermaid diagram is missing" in e for e in self.errors()))
        self.readme.write_text(README.replace(
            '<picture><source srcset="mobile.svg"><img src="workflow.svg" alt="Role handoffs"></picture>',
            '```mermaid\nflowchart TD\nA[Input] --> B[Review] --> C[Output]\n```'
        ), encoding="utf-8")
        self.review_rewrite("Workflow")
        self.assertEqual(self.errors(), [])

    def test_commented_example_empty_and_unclosed_mermaid_do_not_count(self):
        for value in (
            "<!--\n```mermaid\nflowchart TD\nA-->B\n```\n-->",
            "~~~~markdown\n```mermaid\nflowchart TD\nA-->B\n```\n~~~~",
            "```mermaid\n```",
            "```mermaid\nflowchart TD\nA-->B",
        ):
            with self.subTest(value=value):
                self.assertFalse(has_mermaid(value))
        self.assertTrue(has_mermaid("~~~mermaid\nflowchart TD\nA-->B\n~~~~"))

    def test_initial_project_can_capture_an_empty_baseline(self):
        empty = self.base / "new-project"
        empty.mkdir()
        path = self.base / "new-plan.json"
        initialize(empty, path, "tool", "initial")
        data = json.loads(path.read_text())
        self.assertEqual(data["preserve"], [])
        self.assertEqual(data["profile"], "tool")
        self.assertEqual((self.base / data["baseline"]["file"]).read_bytes(), b"")

    def test_malformed_plan_returns_input_error_without_exposing_values(self):
        self.path.write_text('{"private": "never-print-this",', encoding="utf-8")
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("publication_plan.py")),
                                 "verify", str(self.root), "--plan", str(self.path)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("never-print-this", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def add_media(self):
        source = self.base / "source.mp4"
        source.write_bytes(b"supplied-original-version")
        published = self.root / "intro.mp4"
        shutil.copyfile(source, published)
        self.readme.write_text(README + "\n[Video](intro.mp4)\n", encoding="utf-8")
        self.review_rewrite("Security and license")
        self.plan["media"] = [{
            "source_file": str(source), "source_sha256": sha256(source),
            "published_path": "intro.mp4", "published_sha256": sha256(published),
            "transform": "original", "references": ["intro.mp4"],
            "privacy_review": "Reviewed this version using synthetic fixture evidence.",
        }]
        return source, published

    def test_original_must_match_supplied_file_even_if_candidate_hash_is_updated(self):
        _, published = self.add_media()
        self.assertEqual(self.errors(), [])
        published.write_bytes(b"old-redacted-version")
        self.plan["media"][0]["published_sha256"] = sha256(published)
        self.assertTrue(any("original must match" in e for e in self.errors()))

    def test_transformed_media_requires_current_decision_and_review(self):
        _, published = self.add_media()
        published.write_bytes(b"new-encoded-preview")
        item = self.plan["media"][0]
        item.update(transform="transcode", published_sha256=sha256(published))
        self.assertTrue(any("own decision" in e for e in self.errors()))
        item.update(decision_note="Smaller full-duration preview", review_note="Checked timeline, audio and frames")
        self.assertEqual(self.errors(), [])

    def test_replaced_source_and_retired_file_or_link_fail(self):
        source, _ = self.add_media()
        source.write_bytes(b"a-different-source-version")
        self.assertTrue(any("source version changed" in e for e in self.errors()))
        self.plan["retired_paths"] = ["intro.mp4"]
        self.plan["retired_references"] = ["intro.mp4"]
        errors = self.errors()
        self.assertTrue(any("still exists" in e for e in errors))
        self.assertTrue(any("reference remains" in e for e in errors))

    def test_media_only_update_does_not_demand_a_redesign(self):
        other = self.base / "media-plan.json"
        initialize(self.root, other, "app", "media")
        data = json.loads(other.read_text())
        self.assertEqual(data["modules"], [])
        self.assertEqual(data["diagram"]["kind"], "unchanged")
        self.assertTrue(any("versioned media" in e for e in verify_plan(self.root, other)))

    def test_plan_never_overwrites_existing_decisions_or_enters_publication_tree(self):
        with self.assertRaises(ValueError):
            initialize(self.root, self.path, "app", "readme")
        with self.assertRaises(ValueError):
            initialize(self.root, self.root / "plan.json", "app", "readme")

    def test_fenced_headings_are_not_modules_and_html_setext_are_supported(self):
        value = "```md\n## Problem\nfake\n```\n## Actual\nbody\n<h2>HTML section</h2>\ntext\nSetext section\n---\nbody"
        self.assertEqual([s["title"] for s in sections(value)], ["Actual", "HTML section", "Setext section"])

    def test_navigation_and_code_keywords_do_not_pass_basic_verifier(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("tmp/\n")
        self.readme.write_text("# Sample\n[Problem](#problem)\n```text\nquick start tests security\n```\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("verify_project.py")), str(self.root), "--strict"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("problem/value section", result.stdout)
        self.assertIn("quick start section", result.stdout)

    def test_verifier_integrates_plan_failures(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("tmp/\n")
        self.readme.write_text(README.replace("a human checks the result", "automatic"), encoding="utf-8")
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("verify_project.py")), str(self.root), "--plan", str(self.path)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("rewrite review", result.stdout)


class PackageTests(unittest.TestCase):
    def test_missing_changed_and_extra_installed_files_are_reported_without_modification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "package"
            root.mkdir()
            for name, text in {"VERSION": "0.2.0\n", "SKILL.md": "instructions", "LICENSE": "MIT"}.items():
                (root / name).write_text(text)
            build(root)
            self.assertEqual(verify(root), [])
            installed = Path(directory) / "installed"
            shutil.copytree(root, installed)
            self.assertEqual(verify(root, installed), [])
            (installed / "SKILL.md").write_text("personal customization")
            (installed / "extra.md").write_text("retain me")
            errors = verify(root, installed)
            self.assertTrue(any("SKILL.md" in e for e in errors))
            self.assertTrue(any("extra.md" in e for e in errors))
            self.assertEqual((installed / "extra.md").read_text(), "retain me")
            (root / "LICENSE").unlink()
            self.assertTrue(any("LICENSE" in e for e in verify(root)))

    def test_python_caches_do_not_create_version_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("SKILL.md", "LICENSE"):
                (root / name).write_text("sample")
            (root / "VERSION").write_text("0.2.0")
            build(root)
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "module.pyc").write_bytes(b"cache")
            self.assertEqual(verify(root), [])


if __name__ == "__main__":
    unittest.main()
