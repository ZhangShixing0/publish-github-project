from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('audit_repository.py')

class PublicationAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)

    def audit(self, *options):
        result = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), str(self.root), '--json', *options], capture_output=True, text=True, encoding='utf-8')
        return result, json.loads(result.stdout)

    def test_video_audio_and_modern_images_require_review(self):
        for name in ['intro.mp4', 'voice.m4a', 'screen.webp', 'deck.pptx']:
            (self.root/name).write_bytes(b'synthetic binary fixture')
        result, report = self.audit()
        self.assertEqual(result.returncode, 0)
        self.assertEqual({f['path'] for f in report['findings'] if f['category']=='binary-review'}, {'intro.mp4','voice.m4a','screen.webp','deck.pptx'})

    def test_strict_video_review_fails_closed(self):
        (self.root/'intro.mp4').write_bytes(b'fixture')
        result, report = self.audit('--strict-binaries')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['errors'], 1)

    def test_staged_secret_is_found_even_when_worktree_is_cleaned(self):
        probe_value = 'synthetic-audit-probe-value'
        path = self.root/'config.txt'
        path.write_text('APP_SECRET='+probe_value+'\n', encoding='utf-8')
        subprocess.run(['git', '-C', str(self.root), 'add', 'config.txt'], check=True)
        path.write_text('APP_SECRET=your_secret\n', encoding='utf-8')
        result, report = self.audit('--staged')
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any(f['category']=='secret' for f in report['findings']))
        self.assertNotIn(probe_value, result.stdout+result.stderr)

    def test_complete_private_key_headers_are_detected(self):
        for prefix in ['', 'RSA ', 'EC ', 'OPENSSH ', 'ENCRYPTED ']:
            with self.subTest(prefix=prefix):
                (self.root/'fixture.txt').write_text('-----BEGIN '+prefix+'PRIVATE KEY-----\nsynthetic\n', encoding='utf-8')
                result, report = self.audit()
                self.assertEqual(result.returncode, 1)
                self.assertTrue(any(f['category']=='private-key' for f in report['findings']))

    def test_auditor_source_does_not_trigger_private_key_detection(self):
        (self.root/'scanner.py').write_bytes(SCRIPT.read_bytes())
        result, report = self.audit()
        self.assertEqual(result.returncode, 0)
        self.assertFalse(any(f['category']=='private-key' for f in report['findings']))

    def test_staged_audit_excludes_unstaged_files(self):
        (self.root/'README.md').write_text('# Safe\n', encoding='utf-8')
        subprocess.run(['git', '-C', str(self.root), 'add', 'README.md'], check=True)
        (self.root/'.env').write_text('APP_SECRET=synthetic-audit-probe-value\n', encoding='utf-8')
        result, report = self.audit('--staged')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report['files'], 1)

    def test_large_text_does_not_silently_pass_as_scanned(self):
        (self.root/'large.txt').write_bytes(b'x'*(8*1024*1024+1))
        _, report = self.audit()
        self.assertTrue(any(f['category']=='scan-limit' for f in report['findings']))

    def test_svg_text_is_scanned_for_blocked_markers(self):
        (self.root/'hero.svg').write_text('<svg><text>blocked-example-marker</text></svg>', encoding='utf-8')
        result, report = self.audit('--deny', 'blocked-example-marker')
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any(f['category']=='deny-term' for f in report['findings']))

    def test_compact_json_and_lowercase_credentials_are_detected_without_values(self):
        value='synthetic-audit-probe-value'
        (self.root/'config.json').write_text(json.dumps({'nested':{'apiKey':value}}),encoding='utf-8')
        (self.root/'settings.yaml').write_text('client_secret: "'+value+'"\n',encoding='utf-8')
        result,report=self.audit()
        self.assertEqual(result.returncode,1)
        self.assertEqual({f['path'] for f in report['findings'] if f['category']=='secret'},{'config.json','settings.yaml'})
        self.assertNotIn(value,result.stdout+result.stderr)

    def test_environment_lookup_expression_is_not_a_literal_secret(self):
        (self.root/'settings.py').write_text('APP_SECRET = os.environ.get("APP_SECRET", "")\n',encoding='utf-8')
        result,report=self.audit()
        self.assertEqual(result.returncode,0)
        self.assertFalse(any(f['category']=='secret' for f in report['findings']))

if __name__ == '__main__':
    unittest.main()
