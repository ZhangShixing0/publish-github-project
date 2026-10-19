# Publishing policy

## Default decisions

- New repository visibility: private unless the user explicitly chooses public.
- Shared or established repository: feature branch plus draft PR.
- Direct push to the default branch: only when the user requests it or the repository is clearly a personal, low-risk initial publication.
- Release creation, merge, public visibility, repository deletion, force-push, and history rewrite: require separate explicit authority.

## Pre-publish gate

1. Record `git status --short` and preserve unrelated changes.
2. Inspect tracked plus unignored untracked candidates.
3. Confirm the intended repository description, topics, homepage, visibility, default branch, and any archive/template settings. Do not infer public visibility or overwrite existing metadata silently.
4. Confirm `.gitignore` covers secrets, environments, runtime data, generated outputs, databases, archives, screenshot caches, visual-regression artifacts, and customer artifacts appropriate to the project.
5. Run the privacy audit with any known names or identifiers supplied by the user.
6. Review staged filenames, staged sizes, and staged diff, then run `audit_repository.py --staged <repo>` on the full index. A cleaned working copy does not prove that earlier staged bytes are safe. For API uploads, audit the exact candidate bytes and retain their blob IDs instead. Ensure `.env`, spreadsheets, archives, databases, credentials, capture folders, and unrelated binary galleries are absent unless the user explicitly established an intended synthetic fixture or final README asset.
7. Run checks appropriate to the change and README verification; follow `focused-updates.md` for docs/media-only changes. Resolve scan-limit warnings and manually review intended binary media.
8. State the exact commit scope and repository metadata before publishing.

## History and incidents

- A new commit that deletes a value does not erase it from earlier commits.
- First determine whether the sensitive value was ever tracked or only existed in ignored local files.
- Prefer credential rotation over history surgery for leaked secrets.
- Before rewriting history, explain effects on collaborators, forks, open PRs, commit links, and cached views.
- Never keep a backup Git ref containing data the user asked to purge.

## Post-publish gate

- Confirm the remote branch points to the intended SHA.
- Verify repository visibility and default branch.
- Verify the repository description, topics, homepage, and any explicitly requested archive/template setting.
- Inspect CI/check results and report failures without hiding them.
- Verify the remote changed-file list has no blocked filenames, screenshot caches, or unexpected binary datasets.
- Return the repository/PR link, commit SHA, tests run, privacy result, and any limitations.
