from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from verify_project import clean_target, markdown_links, resolve_local, image_references, without_fenced_code
from readme_header import dimensions, is_badge, opening_issues, semantic_h1_count


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
            (root/'README.md').write_text('<div align="center">\n\n# Product\n\n<picture><source srcset="mobile.svg"><img src="desktop.svg" alt="Workflow"></picture>\n\n**Run the workflow.**\n\n[Start](#quick-start) · [Security](#security)\n\n![Stage](https://img.shields.io/badge/stage-prototype-blue) ![License](https://img.shields.io/badge/license-MIT-green)\n\n</div>\n\n## Problem\nOverview.\n## Quick start\nStart.\n## Tests\nVerify.\n## Security\nPrivate.\n',encoding='utf-8')
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


class HeaderTests(unittest.TestCase):
    TITLE = '# Harbor'
    HERO = '![Harbor overview](docs/hero.svg)'
    VALUE = '**Walk around an interactive harbor.**'
    NAV = '[Start](#quick-start) · [Models](#models) · [License](#license)'
    BADGES = '[![Version 3.42](docs/badges/version.svg)](#version) ![Three.js r185](docs/badges/threejs.svg) ![All rights reserved](docs/badges/license.svg)'
    BODY = '## Problem\nOverview.\n\n## Quick start\nStart.\n\n## Tests\nVerify.\n\n## Security\nPrivate.\n'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'docs/badges').mkdir(parents=True)
        (self.root/'docs/hero.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 600"><title>Harbor</title></svg>', encoding='utf-8')
        for name in ('version','threejs','license'):
            (self.root/f'docs/badges/{name}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20"><title>Status</title></svg>',encoding='utf-8')

    def document(self, parts=None, centered=True, body_centered=False):
        if parts is None:
            parts = [self.TITLE,self.HERO,self.VALUE,self.NAV,self.BADGES]
        opening = '\n\n'.join(parts)
        if centered:
            opening = '<div align="center">\n\n' + opening + ('\n\n</div>' if not body_centered else '')
        return opening + '\n\n' + self.BODY + ('\n</div>' if body_centered else '')

    def issues(self, document=None, style='showcase'):
        text = self.document() if document is None else document
        return opening_issues(without_fenced_code(text),image_references(text),self.root,self.root/'README.md',style)

    def cli(self, text, *flags):
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        (self.root/'.gitignore').write_text('tmp/\n',encoding='utf-8')
        (self.root/'README.md').write_text(text,encoding='utf-8')
        return subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).with_name('verify_project.py')),str(self.root),'--strict',*flags],capture_output=True,text=True,encoding='utf-8')

    def test_canonical_centered_opening_with_local_badges_passes(self):
        self.assertEqual(self.issues(),[])
        result=self.cli(self.document(),'--visual')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_shipped_template_produces_the_canonical_opening(self):
        template=(Path(__file__).resolve().parents[1]/'assets/readme-template.md').read_text(encoding='utf-8')
        opening=template.split('> [!IMPORTANT]',1)[0]
        for name,value in {
            'PROJECT_NAME':'Harbor',
            'HERO_WITH_DESCRIPTIVE_ALT':self.HERO,
            'ONE_SENTENCE_VALUE':'Walk around an interactive harbor.',
            'QUICK_NAVIGATION':self.NAV,
            'VERIFIED_BADGES':self.BADGES,
        }.items():
            opening=opening.replace('{{'+name+'}}',value)
        self.assertEqual(self.issues(opening+'\n'+self.BODY),[])

    def test_value_and_navigation_swapped_are_detected(self):
        text=self.document([self.TITLE,self.HERO,self.NAV,self.VALUE,self.BADGES])
        self.assertTrue(any('expected' in issue for issue in self.issues(text)))

    def test_missing_badges_do_not_pass_strict_visual_cli(self):
        text=self.document([self.TITLE,self.HERO,self.VALUE,self.NAV])
        result=self.cli(text,'--visual')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('missing verified badge',result.stdout)

    def test_badges_before_hero_reproduces_first_reported_failure(self):
        issues=self.issues(self.document([self.TITLE,self.BADGES,self.HERO,self.VALUE,self.NAV]))
        self.assertTrue(any('expected title -> hero' in issue for issue in issues),issues)

    def test_left_aligned_header_reproduces_second_reported_failure(self):
        issues=self.issues(self.document(centered=False))
        self.assertEqual(sum('must be centered' in issue for issue in issues),5)

    def test_nested_left_aligned_badge_paragraph_is_detected(self):
        issues=self.issues(self.document([self.TITLE,self.HERO,self.VALUE,self.NAV,'<p align="left">'+self.BADGES+'</p>']))
        self.assertTrue(any('badges block' in issue and 'centered' in issue for issue in issues))

    def test_centered_body_and_callout_are_detected(self):
        text=self.document(body_centered=True)
        self.assertTrue(any('body/callout is still centered' in issue for issue in self.issues(text)))
        text=text.replace('## Problem','> [!IMPORTANT]\n> Prototype.\n\n## Problem')
        self.assertTrue(any('body/callout is still centered' in issue for issue in self.issues(text)))

    def test_badges_in_body_do_not_satisfy_opening(self):
        text=self.document([self.TITLE,self.HERO,self.VALUE,self.NAV])+self.BADGES
        self.assertTrue(any('missing verified badge' in issue for issue in self.issues(text)))

    def test_badges_are_not_mistaken_for_hero(self):
        text=self.document([self.TITLE,self.VALUE,self.NAV,self.BADGES])
        result=self.cli(text,'--visual')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('no non-badge image',result.stdout)

    def test_compact_mode_works_without_decorative_hero(self):
        text=self.document([self.TITLE,self.VALUE,self.NAV,self.BADGES])
        self.assertEqual(self.issues(text,'compact'),[])
        result=self.cli(text,'--visual','--header-style','compact')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_split_badges_and_mixed_navigation_are_detected(self):
        text=self.document([self.TITLE,self.HERO,self.VALUE,self.NAV,self.BADGES,'![Runtime](docs/badges/runtime.svg)'])
        self.assertTrue(any('expected' in issue for issue in self.issues(text)))
        text=self.document([self.TITLE,self.HERO,self.VALUE,self.NAV+' '+self.BADGES])
        self.assertTrue(any('navigation separate' in issue for issue in self.issues(text)))

    def test_comments_and_code_examples_do_not_supply_badges(self):
        text=self.document([self.TITLE,self.HERO,self.VALUE,self.NAV,'<!-- '+self.BADGES+' -->','```md\n'+self.BADGES+'\n```'])
        self.assertTrue(any('missing verified badge' in issue for issue in self.issues(text)))

    def test_html_title_and_separate_html_centered_blocks(self):
        text='\n\n'.join([
            '<h1 align="center">Harbor</h1>',
            '<p align="center"><img src="docs/hero.svg" alt="Harbor"></p>',
            '<p align="center"><strong>Walk around a harbor.</strong></p>',
            '<p align="center"><a href="#start">Start</a> · <a href="#models">Models</a></p>',
            '<p align="center"><a href="#version"><img src="docs/badges/version.svg" alt="Version 3.42"></a> <img src="docs/badges/threejs.svg" alt="Three.js r185"></p>',
            self.BODY,
        ])
        self.assertEqual(self.issues(text),[])
        result=self.cli(text,'--visual')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_tall_hero_requires_framing_review(self):
        (self.root/'docs/hero.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2100 1500"/>',encoding='utf-8')
        self.assertTrue(any('unusually tall' in issue for issue in self.issues()))

    def test_duplicate_h1_is_not_accepted(self):
        text=self.document()+'\n# Second title\n'
        result=self.cli(text)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('one semantic H1',result.stdout)

    def test_nonvisual_routine_check_does_not_force_a_redesign(self):
        result=self.cli(self.document([self.TITLE,self.VALUE],centered=False))
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_preserve_requires_reason_and_does_not_bypass_unsafe_svg(self):
        text=self.document(centered=False)
        missing_note=self.cli(text,'--visual','--header-style','preserve')
        self.assertEqual(missing_note.returncode,2)
        preserved=self.cli(text,'--visual','--header-style','preserve','--header-note','User requested the existing alignment')
        self.assertEqual(preserved.returncode,0,preserved.stdout+preserved.stderr)
        (self.root/'docs/badges/version.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',encoding='utf-8')
        unsafe=self.cli(text,'--visual','--header-style','preserve','--header-note','User requested the existing alignment')
        self.assertNotEqual(unsafe.returncode,0)
        self.assertIn('unsafe README SVG',unsafe.stdout)


class BadgeRecognitionTests(unittest.TestCase):
    def test_local_and_hosted_badges(self):
        for source in ('docs/badges/version.svg','./docs/badges/threejs.svg','docs/badges/license.svg?raw=1','assets/python-badge.svg','https://img.shields.io/badge/status-prototype-blue','https://github.com/owner/repo/actions/workflows/check.yml/badge.svg'):
            with self.subTest(source=source):
                self.assertTrue(is_badge(source))

    def test_regular_images_are_not_badges(self):
        for source in ('docs/hero.svg','docs/badger.png','docs/logo.svg','https://example.com/hero.png?provider=img.shields.io'):
            with self.subTest(source=source):
                self.assertFalse(is_badge(source))

    def test_heading_examples_are_not_titles(self):
        text='<!-- # Hidden\n<h1>Hidden</h1> -->\n```md\n# Example\n```\n<h1>Real</h1>'
        self.assertEqual(semantic_h1_count(without_fenced_code(text)),1)


if __name__ == "__main__":
    unittest.main()
