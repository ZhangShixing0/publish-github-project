import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import verify_remote as verifier

SHA='1'*40
BLOB='2'*40

class RemoteVerificationTests(unittest.TestCase):
    def test_api_snapshot_reads_exact_ref_and_unicode_paths(self):
        responses=[{'object':{'sha':SHA}},{'tree':{'sha':'3'*40}},{'truncated':False,'tree':[{'path':'说明/工作流.svg','type':'blob','sha':BLOB}]}]
        with patch.object(verifier,'github_api',side_effect=responses) as api:
            self.assertEqual(verifier.github_snapshot('github.com','owner/repo','codex/preview'),(SHA,{'说明/工作流.svg':BLOB}))
        self.assertEqual(api.call_args_list[0].args[2],'git/ref/heads/codex/preview')

    def test_truncated_api_tree_is_not_reported_complete(self):
        with patch.object(verifier,'github_api',side_effect=[{'object':{'sha':SHA}},{'tree':{'sha':'3'*40}},{'truncated':True,'tree':[]}]):
            with self.assertRaisesRegex(RuntimeError,'truncated'):
                verifier.github_snapshot('github.com','owner/repo','main')

    def invoke(self, remote_sha=SHA, tree=None, extra=None):
        output=io.StringIO()
        args=['verify_remote.py','--transport','github-api','--github-repo','owner/repo','--branch','codex/preview','--expected-sha',SHA,*(extra or [])]
        with patch('sys.argv',args), patch.object(verifier,'repository_root',return_value=Path('.')), patch.object(verifier,'run',return_value='') as git, patch.object(verifier,'github_snapshot',return_value=(remote_sha,tree or {})), contextlib.redirect_stdout(output):
            code=verifier.main()
        self.assertFalse(any('HEAD' in call.args for call in git.call_args_list))
        return code,output.getvalue()

    def test_api_created_commit_does_not_require_local_head_match(self):
        code,_=self.invoke()
        self.assertEqual(code,0)

    def test_wrong_published_sha_fails(self):
        code,output=self.invoke(remote_sha='4'*40)
        self.assertEqual(code,1)
        self.assertIn('does not match',output)

    def test_api_tree_still_rejects_published_env(self):
        code,output=self.invoke(tree={'.env':BLOB})
        self.assertEqual(code,1)
        self.assertIn('blocked filename',output)

    def test_missing_manifest_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest=Path(directory)/'files.json'
            manifest.write_text(json.dumps({'docs/图.svg':BLOB}),encoding='utf-8')
            code,output=self.invoke(extra=['--file-manifest',str(manifest)])
        self.assertEqual(code,1)
        self.assertIn('missing or differs',output)

    def test_git_tree_preserves_unicode_and_newlines_in_names(self):
        name='文档/line\nbreak.txt'
        with patch.object(verifier,'run',return_value=f'100644 blob {BLOB}\t{name}\0'):
            self.assertEqual(verifier.git_tree(Path('.'),SHA),{name:BLOB})

if __name__=='__main__':
    unittest.main()
