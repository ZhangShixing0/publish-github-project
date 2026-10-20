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
        root = ET.fromstring(render("A & B", "<script>x</script>"))
        self.assertEqual(root.find("{*}title").text, "A & B: <script>x</script>")
        self.assertEqual(root.findall(".//{*}script"), [])

    def test_unicode_width_and_invalid_controls(self):
        self.assertGreater(text_width("许可证说明"), text_width("MIT"))
        with self.assertRaises(ValueError):
            render("version", "x\nx")
        with self.assertRaises(ValueError):
            render("version", "1", -2)

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
