from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from verify_project import clean_target, markdown_links, resolve_local, image_references


class LocalLinkTests(unittest.TestCase):
    def test_github_raw_query_resolves_to_existing_media(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "docs" / "intro.mp4"
            media.parent.mkdir()
            media.write_bytes(b"fixture")
            targets = markdown_links("[Original](docs/intro.mp4?raw=true#t=20)")
            self.assertEqual(len(targets), 1)
            self.assertEqual(resolve_local(root, root / "README.md", targets[0]), media)
            self.assertTrue(media.is_file())

    def test_encoded_path_characters_are_decoded_after_url_parsing(self):
        self.assertEqual(clean_target("docs/my%20demo%23one.mp4?raw=1"), "docs/my demo#one.mp4")
        self.assertEqual(clean_target("docs/demo%3Fone.mp4"), "docs/demo?one.mp4")

    def test_angle_wrapped_paths_with_spaces_and_titles(self):
        self.assertEqual(clean_target('<docs/my demo.png> "Demo"'),'docs/my demo.png')
        self.assertEqual(clean_target('docs/demo.png "Demo caption"'),'docs/demo.png')

    def test_fenced_documentation_examples_are_not_live_links(self):
        example='```markdown\n![Example](missing.png)\n<img src="missing-mobile.svg">\n```\n[Guide](docs/guide.md)'
        self.assertEqual(markdown_links(example),['docs/guide.md'])
        self.assertEqual(image_references(example),[])

    def test_anchor_only_and_remote_targets_are_not_local_files(self):
        self.assertEqual(markdown_links("[Part](#part) [Video](https://example.com/a.mp4?raw=1#t=2)"), [])

    def test_remote_signed_url_is_preserved(self):
        target = "https://example.com/a?signature=a%2Fb&raw=1#t=2"
        self.assertEqual(clean_target(target), target)

    def test_encoded_parent_traversal_remains_detectable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = clean_target("%2E%2E/private.txt?raw=1")
            candidate = resolve_local(root, root / "README.md", target)
            with self.assertRaises(ValueError):
                candidate.relative_to(root)


class ResponsiveImageTests(unittest.TestCase):
    def test_picture_source_and_img_srcset_are_included(self):
        text = '<picture><source srcset="mobile.svg 1x, mobile-2x.svg 2x"><img src="desktop.svg" srcset="desktop-2x.svg 2x" alt="Product workflow"></picture>'
        self.assertEqual({r.source for r in image_references(text)}, {'mobile.svg','mobile-2x.svg','desktop.svg','desktop-2x.svg'})

    def verify_picture(self, mobile_content=None):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(['git','init','-q',str(root)],check=True)
            (root/'.gitignore').write_text('tmp/\n',encoding='utf-8')
            (root/'README.md').write_text('# Product\n## Problem\nOverview.\n<picture><source srcset="mobile.svg"><img src="desktop.svg" alt="Workflow"></picture>\n## Quick start\nStart.\n## Tests\nVerify.\n## Security\nPrivate.\n',encoding='utf-8')
            (root/'desktop.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><title>Desktop</title></svg>',encoding='utf-8')
            if mobile_content is not None:(root/'mobile.svg').write_text(mobile_content,encoding='utf-8')
            return subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).with_name('verify_project.py')),'--strict','--visual',str(root)],capture_output=True,text=True,encoding='utf-8')

    def test_missing_mobile_source_fails_verification(self):
        result=self.verify_picture()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('mobile.svg',result.stdout)

    def test_unsafe_mobile_svg_fails_verification(self):
        result=self.verify_picture('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('unsafe',result.stdout)

    def test_safe_picture_does_not_require_source_alt(self):
        result=self.verify_picture('<svg xmlns="http://www.w3.org/2000/svg"><title>Mobile</title></svg>')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__ == "__main__":
    unittest.main()
