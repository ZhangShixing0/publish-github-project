import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from render_badges import outputs, render, text_width


class BadgeRenderingTests(unittest.TestCase):
    def test_xml_escaping_prevents_injected_elements(self):
        root = ET.fromstring(render("A & B", "<script>x</script>", category="technology"))
        self.assertEqual(root.find("{*}title").text, "A & B: <script>x</script>")
        self.assertEqual(root.findall(".//{*}script"), [])

    def test_unicode_width_and_invalid_controls(self):
        self.assertGreater(text_width("许可证说明"), text_width("MIT"))
        with self.assertRaises(ValueError):
            render("version", "x\nx")
        with self.assertRaises(ValueError):
            render("version", "1", -2)

    def test_square_style_uses_fixed_category_colors_and_white_text(self):
        for category, color in (
            ("version","#456a63"), ("platform","#a86b3a"),
            ("runtime","#427d89"), ("license","#686d74"),
        ):
            root = ET.fromstring(render("Label","Value",category=category))
            rects = root.findall("{*}rect")
            self.assertEqual(root.get("height"),"20")
            self.assertEqual([r.get("fill") for r in rects],["#555555",color])
            self.assertTrue(all(r.get("rx") is None for r in rects))
            self.assertEqual(root.find("{*}g").get("fill"),"#ffffff")

    def test_square_style_requires_a_known_category(self):
        for category in (None,"random-color"):
            with self.assertRaises(ValueError):
                render("Label","Value",category=category)

    def test_accepted_legacy_style_still_renders(self):
        root = ET.fromstring(render("version","1",style="forest-v1"))
        self.assertEqual(root.get("height"),"26")
        self.assertEqual(root.find("{*}rect").get("rx"),"5")

    def test_manifest_refuses_escape_duplicate_and_unknown_style(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"badges.json"
            entry = {"file":"ok.svg","label":"version","value":"1","evidence":"VERSION"}
            for data in (
                {"style":"forest-v1","badges":[dict(entry,file="../outside.svg")]},
                {"style":"forest-v1","badges":[entry,entry]},
                {"style":"other","badges":[entry]},
            ):
                path.write_text(json.dumps(data),encoding="utf-8")
                with self.assertRaises(ValueError):
                    outputs(path)

    def test_read_only_check_detects_drift_without_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"badges.json"
            path.write_text(json.dumps({"style":"forest-v1","badges":[
                {"file":"version.svg","label":"version","value":"1","evidence":"VERSION"}
            ]}),encoding="utf-8")
            command = [sys.executable,str(Path(__file__).with_name("render_badges.py")),str(path)]
            subprocess.run(command,check=True,capture_output=True)
            self.assertEqual(subprocess.run(command+["--check"],capture_output=True).returncode,0)
            badge = path.with_name("version.svg")
            altered = badge.read_bytes().replace(b"#234e40",b"#000000")
            badge.write_bytes(altered)
            self.assertEqual(subprocess.run(command+["--check"],capture_output=True).returncode,1)
            self.assertEqual(badge.read_bytes(),altered)


if __name__ == "__main__":
    unittest.main()
