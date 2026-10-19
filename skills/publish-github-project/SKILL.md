---
name: publish-github-project
description: Turn a local codebase into a safe, reproducible, presentation-ready GitHub project, including repository description, topics, visibility, and other GitHub metadata. Use when the user asks to 整理项目并上传 GitHub, 发布仓库, 设计、优化或重写精美 README, 增加 README Hero/版本入口/架构图, 补齐安全与贡献文档, 检查密钥或截图缓存后发布, or verify that a GitHub repository can be reproduced from scratch.
---

# Publish GitHub Project

Build from codebase evidence, not generic marketing copy. Preserve user work, make every public claim verifiable, and give the repository a deliberate visual identity when the project benefits from one.

## Workflow

Choose the scope first. For an established repository receiving a README, media, or metadata update, read `references/focused-updates.md` and preserve the accepted presentation and unrelated files. Use the full workflow for initial publication, broad restructuring, or changes to runtime behavior. When a product showcase needs screenshots or video, read `references/project-media.md`: proactively capture a runnable product when suitable screenshots are missing; omit unavailable video unless the user requires it.

1. Confirm the repository root, visibility, target owner/name, release scope, and whether the user wants a branch/PR or an explicitly authorized direct-main update. Default new repositories to private and established repositories to a branch plus draft PR.
2. Define the GitHub repository metadata before publishing: a concise description, 3–10 truthful topics, homepage/demo URL when one exists, and whether the repository should be archived or template-enabled. Preserve existing metadata on established repositories unless the user authorizes changes. Read `references/repository-metadata.md` for the field rules and commands.
3. Inspect `git status`, `.gitignore`, tracked and untracked candidates, manifests, entrypoints, tests, screenshots, docs, license, tags/releases, and remote configuration. Never assume an untracked file is disposable.
4. Run `scripts/audit_repository.py <repo>`. Ask for known client names, identifiers, or institution markers when privacy matters; pass them with `--deny` or `--deny-file`. Stop on new findings before staging or publishing.
5. Read `references/readme-style.md` before creating or substantially rewriting a README. When the user asks for a beautiful README, repository showcase, Hero, or stronger GitHub presentation, also read `references/readme-visual-design.md` and select the smallest fitting design mode.
6. Adapt `assets/readme-template.md` to verified project facts. Create a repository-native SVG Hero only when it improves comprehension and no current, privacy-safe visual already exists. Keep it self-contained, accessible, lightweight, and visibly tied to the product.
7. Add only architecture, deployment, security, roadmap, contribution, or changelog documents that materially help reproduction or governance. Link to detail instead of turning the README into a wall of text.
8. Run checks appropriate to the changed scope in an isolated or project-local environment; full publication includes the project's release checks. For an existing README, complete the before/after content review in `references/focused-updates.md`. Run `scripts/verify_project.py --strict <repo>`; add `--visual` after a visual README redesign. Inspect rendered assets before claiming visual QA. Once required checks pass, repeat only when a change, failure, or unresolved concern warrants it.
9. Read `references/publishing-policy.md`. Review the exact staged scope, run `audit_repository.py --staged <repo>` on the index bytes, and verify that secrets, datasets, runtime outputs, screenshot caches, and generated customer artifacts are excluded. For API-created commits, audit the exact upload candidates and retain their Git blob IDs for remote comparison.
10. Publish intentionally with the available GitHub integration. Commit, push the chosen branch, and open a draft PR for established repositories. Apply the confirmed repository metadata as part of the same authorized publish operation. Never delete a repository, force-push, rewrite history, make a repository public, merge, or create a release without explicit authority.
11. Run `scripts/verify_remote.py <repo>` after publishing; use its GitHub API mode from `references/focused-updates.md` when Git transport is unavailable or the commit was created through the API. Separately confirm the changed-file list and repository metadata, inspect CI, and verify rendered assets and version links. The script does not establish those separate checks.

## README standard

- Make the first screen answer: what is this, who is it for, what state/version is current, and where can a reader start.
- Keep one semantic H1 even when the Hero contains display typography.
- Put a concrete value sentence before technology details; use only truthful, useful badges.
- For product-showcase READMEs, use one coherent Hero, a short navigation row, and one compact workflow visual. Add an early version center when versions or Releases exist and readers need to distinguish them.
- For libraries and developer tools, prefer a compact lockup plus a real usage snippet over a cinematic banner.
- Link current Release/Tag and retained historical versions directly when version discovery matters.
- Explain the problem and workflow before implementation details, then provide a tested shortest-path quick start.
- Collapse deep directory, security, or limitation detail when it interrupts first-time scanning.
- State maturity, security boundaries, license, and limitations plainly.
- Distinguish repository visibility, product access (such as private beta), and license permissions. Preserve the owner's licensing choice; clarify contradictory wording without granting new permissions.
- Never invent adoption numbers, compatibility, performance, badges, integrations, or roadmap commitments.
- Treat the template as a starting structure for new content; preserve an established README's useful information. Role tables and workflow diagrams may coexist when they explain different aspects.
- Keep repository-list metadata separate from README content: a README does not populate the GitHub description or topics automatically.

## Visual asset rules

- Prefer existing brand assets or current synthetic-data product visuals. Do not publish local capture folders or a gallery of stale iterations.
- Prefer code-native SVG for abstract product Heroes. Do not embed raster screenshots as base64 inside SVG.
- Use system font fallbacks, `<title>`/`<desc>`, descriptive README alt text, and sufficient contrast.
- Do not include scripts, `foreignObject`, event handlers, external fonts, external image references, or copied third-party logos in SVG.
- Keep one strong Hero instead of several decorative banners. Optimize assets before publishing.
- Inspect the rendered asset, not only its source. Verify mobile scanability and GitHub light/dark compatibility.

## Safety gates

- Treat `.env*`, credentials, private keys, real names, identity numbers, phone numbers, customer documents, spreadsheets, archives, databases, logs, screenshots, browser captures, and generated outputs as high-risk.
- Do not echo secret values or sensitive matched text; report only the category and path.
- Automated scanning is a heuristic, not privacy clearance. Review binary-media findings and scan-limit warnings explicitly; it does not inspect video frames/audio or replace a broader history/secret audit when needed.
- Distinguish intentional, referenced product media from screenshot caches such as `_screenshots/`, `tmp/`, test artifacts, and design iteration exports.
- Distinguish the current tree from Git history. Explain when deletion does not remove historical content and request approval before destructive remediation.
- Preserve dirty-worktree changes and unrelated files. Stage only the intended scope.
- Keep organization-specific names, credentials, and policies in untracked configuration or repository docs, never in this reusable skill.

## Resources

- `references/readme-style.md`: information order, writing, evidence, and restraint.
- `references/readme-visual-design.md`: design modes, Hero construction, version navigation, GitHub constraints, and visual QA.
- `references/publishing-policy.md`: authority and pre/post-publish gates.
- `references/repository-metadata.md`: description, topics, homepage, visibility, and post-publish metadata verification.
- `references/focused-updates.md`: small update scope, proportionate verification, and GitHub connection recovery.
- `references/project-media.md`: missing-media decisions, real product screenshot capture, and video preparation and playback verification.
- `assets/readme-template.md`: adaptable product-showcase skeleton; remove unused placeholders.
- `scripts/audit_repository.py`: scan working-tree candidates or exact index bytes (`--staged`), including text/SVG/OOXML, credential literals, identifiers, deny terms, and media requiring manual review.
- `scripts/verify_project.py`: check README structure, links, image assets, safe SVG, visual mode, and manifest discoverability.
- `scripts/verify_remote.py`: verify the published branch SHA and file tree via Git or the GitHub API, with optional expected blob IDs; metadata, CI, privacy and rendering need separate verification.
