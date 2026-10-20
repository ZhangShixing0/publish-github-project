# Focused updates to an existing repository

Use for adding media, improving a README, or updating repository metadata without changing application behavior.

## Scope and presentation

- Read the current default branch and inspect local changes before editing. Use an isolated checkout when the user's working tree contains unrelated work.
- Preserve accepted brand assets and information unless the requested improvement benefits from changing them. A new video does not require a new Hero, release, license, or deployment.
- Keep a precise changed-file allowlist. Record the base SHA and approved operation; existing authorization for that same operation persists during the task. Approval for an earlier, different PR does not authorize a new merge.
- Prepare a concrete preview before any approval that is still required. Default to a branch and draft PR for an established repository.
- For substantive README redesigns and media replacements, use the local baseline/decision record in `publication-plan.md`. Preserve ordinary small-update efficiency; do not create a full redesign plan for a typo or metadata-only task.

## Preserve meaning when restyling a README

- Before rewriting, identify the existing information readers need: intended users and problem solved; workflow inputs, responsibilities, handoffs, outputs, and required human decisions; current capabilities and limits; and the path to run and verify the project. Use the actual repository, not a fixed section template.
- In working notes, map each affected item to its new location or explain its removal. Rewording, merging, and moving secondary detail are allowed; retain an understandable problem and workflow overview in the README, with direct links for moved details. No extra published report is required.
- Preserve unique, still-valid information when shortening. A heading or slogan alone does not preserve the explanation beneath it. A Hero, screenshot, or video complements the explanation; readers should not have to play media to discover essential inputs, outputs, or handoffs.
- Keep useful tables and diagrams, or replace them with an equally informative treatment. For example, a role table and a workflow diagram can answer different questions; a bare arrow sequence may omit the table's input/output mapping or the diagram's handoff conditions. Do not require every project to use either format.
- Remove inaccurate, obsolete, duplicated, or explicitly unwanted material with a concrete reason. A request to make the page more attractive is not by itself a reason to drop meaningful content.
- Before publishing, compare the candidate with the baseline using the mapping and diff. Restore unexplained losses or resolve a material scope ambiguity with the user. `verify_project.py` checks structure and assets; passing keyword/heading checks does not establish semantic completeness.
- `verify_project.py --plan` checks the recorded section mapping and detects unreviewed body changes. It still cannot determine whether an approved rewrite preserved the meaning; perform that comparison before writing its review note.

## Proportionate verification

- Audit the base and final tree with the same options. Review every new or changed finding; unchanged findings may be carried forward only when their path, category, and context have already been reviewed. Never accept all warnings merely because the total stayed constant.
- For docs/media changes, check local links, intended asset provenance and sizes, staged scope, and the relevant visual/media behavior. Run full project checks for runtime changes or when repository rules require them; inspect whatever CI actually runs.
- Validate new quick-start or walkthrough commands in a disposable environment. Do not promise a setup duration without measuring it; distinguish installation from the subsequent product walkthrough.
- After publishing, verify the intended SHA, changed paths, asset hashes where relevant, unchanged metadata, and CI. One successful verification is enough unless later changes invalidate it.
- Distinguish working-tree, index, and remote evidence: audit the index before a Git commit, or the exact candidate bytes before API upload. Review binary-media and scan-limit findings manually; a zero-error scan does not establish that a video or screenshot is safe.

## Verify an API-created commit

When an authorized API publish succeeds but local HEAD still points to the base commit, verify the recorded new SHA explicitly. With an already authenticated GitHub CLI:

```shell
python scripts/verify_remote.py /path/to/repo --transport github-api --github-repo OWNER/REPO --branch codex/showcase --expected-sha FULL_COMMIT_SHA --file-manifest /path/to/file-blobs.json --allow-dirty
```

The manifest is a JSON object mapping intended paths to Git blob IDs, such as `{"README.md": "FULL_GIT_BLOB_ID"}`; SHA-256 file hashes are not Git blob IDs. Keep the manifest outside the published files. Use `--allow-dirty` only when the deliberate local candidate state has been reviewed, and `--github-host` for the actual configured enterprise host if applicable. The API mode only reads remote state and refuses to accept a truncated tree as complete.

This verifies the branch, tree, and supplied blob IDs. Separately compare the PR's complete changed-file list with the allowlist and check metadata, CI, media privacy, and rendered behavior. `--offline` uses a cached tracking ref and cannot prove the current remote state. If `gh` is unavailable, use equivalent read-only connector evidence instead of requiring a new installation.

## GitHub connection recovery

1. Check the required operation and available connector/CLI capabilities before choosing a transport. A tool version may support repository reads but not media attachments.
2. Classify failures: network/connectivity, authentication, repository permission, unsupported feature, or branch policy. A network failure from an authentication command is not evidence that stored credentials are invalid.
3. Use an already authenticated alternative that has the required capability, such as the connector, local CLI, or API. Preserve the same repository, branch, file scope, and approval boundary. Never print tokens or request broader credentials just to retry.
4. Before retrying a timed-out write, inspect the remote state to determine whether it already succeeded. Avoid duplicate uploads, commits, PRs, or merges.
5. If Git transport is unavailable but the API works, use API evidence for verification and say which checks were performed. Do not claim a successful fetch or clone. After a failed retry with no new evidence, report the concrete blocker instead of looping through transports.
6. Keep diagnostic output to necessary resource paths, status codes, and error classes. Omit cookies, authorization headers, and signed URL query strings. A failure in an automated browser is evidence about that attempt, not proof that every visitor sees a broken page.
