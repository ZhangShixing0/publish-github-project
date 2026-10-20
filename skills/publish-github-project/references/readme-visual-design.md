# README visual design

Use this guide for requests such as “README 太 low”, “做得更好看”, “增加 Hero”, or “让仓库更适合展示”. GitHub README supports Markdown and a restricted HTML subset; design inside those constraints instead of depending on custom CSS or JavaScript.

## 1. Choose a design mode

| Mode | Best for | First-screen treatment |
| --- | --- | --- |
| Product showcase | User-facing apps, SaaS, dashboards, multi-role systems | Showcase opening from `readme-header.md` |
| Developer tool | Libraries, CLIs, SDKs, APIs | Compact opening from `readme-header.md`, then real usage/install commands |
| Evidence report | Research, datasets, benchmarks, internal methods | Preserve a purposeful report layout with a documented header exception |

Do not force a large Hero onto a small library. Do not reduce a visual product to a badge wall and directory listing.

## 2. Compose the first screen

Read `readme-header.md` for the canonical sequence, centered identity boundary, badge evidence, and mode exceptions. Use `assets/readme-template.md` as its implementation; do not maintain an alternative sequence here.

Keep Release and Tags discoverable without requiring readers to understand GitHub navigation.

## 3. Build a useful Hero

For a product showcase without usable screenshots, first follow `project-media.md` to capture the actual product when feasible. A Hero can complement those views or explain the workflow when capture is blocked; it must not imply that a designed interface is already implemented.

Prefer an existing current brand asset or privacy-safe product screenshot when it is accurate and legible. If none exists, create a repository-native SVG:

- Canvas: roughly 1200–1600 × 500–700 with a 2:1 to 2.4:1 ratio.
- Payload: aim below 250 KiB; keep it as SVG instead of embedding raster data.
- Content: project identity, one product promise, current version/state, and a small visual motif that explains the workflow or interface.
- Style: one dark or light surface, one primary accent, one supporting accent, consistent corner radii and spacing.
- Typography: system font stack with CJK fallbacks; do not fetch web fonts.
- Accessibility: include SVG `<title>` and `<desc>`, plus meaningful README alt text.
- Safety: no `<script>`, `foreignObject`, event handlers, external `href`, remote images, copied logos, or sensitive screenshots.

Render the SVG to a raster preview at the intended dimensions and inspect overlap, clipping, contrast, CJK fallback, and small text. Source inspection alone is not visual QA.

## 4. Make versions obvious

When releases or historical tags exist, place a compact version center immediately after the first callout:

| Version | Meaning | Link |
| --- | --- | --- |
| Current | Supported or recommended state | Direct Release and source-tree links |
| Previous | Why it remains useful | Direct Tag link |

Use user-facing aliases such as “v721” alongside canonical tags when both exist. Never imply a tag contains later commits.

## 5. Reduce the information wall

- For an established showcase, preserve the accepted visual identity and improve one reading path at a time. Keep the current release visible while folding historical version tables when they dominate the page.
- Product screenshots can complement video for readers who do not play it. Use a small, reviewed set of real synthetic-data views, with captions describing tasks or results. Do not fabricate a product UI to fill a decorative card.
- A first-use walkthrough should say what to do after startup and what observable result to expect. Use existing supported flows and verified sample data; keep detailed steps in a linked guide when long.
- Prefer vertically stacked media and narrow tables that remain readable on mobile. Test any HTML or picture-based treatment on GitHub itself; an attractive custom HTML mockup is not evidence of README compatibility.
- Keep the problem, workflow, current scope, and quick start expanded.
- Move long trees, detailed security boundaries, and limitations into `<details>` when they remain important but secondary.
- Use a Mermaid diagram only for a real sequence or relationship with at least three meaningful nodes.
- Use tables for exact mappings such as role → responsibility → entrypoint. A role table may accompany a workflow diagram when each contributes distinct information; avoid choosing between them solely to make the page shorter.

### Workflow diagrams

- Reuse an accurate existing diagram. When a meaningful workflow lacks one, derive a compact Mermaid diagram from verified code and documentation: show actual inputs, responsibilities, handoffs, outputs, and required human decisions. Keep implementation detail in the linked architecture document when it obscures the overview.
- Inspect labels at the intended README width. A long horizontal diagram may shrink its text; use grouping or a vertical layout when it improves reading. Small display size is not evidence of a rendering failure or excessive complexity.
- Verify both the Mermaid source and the actual GitHub output. On failure, distinguish syntax/version errors from component resource loading, timeouts, and the local browser environment. Use a targeted diagnostic attempt; do not repeat unchanged browser retries or announce a repository-wide failure based only on one automated preview.
- If rendering remains blocked, state what is verified and what is not. A reviewed self-contained SVG following the asset rules can provide a fallback while retaining editable diagram source. Preserve the workflow information; do not silently replace it with an incomplete slogan or arrow list.

## 6. Protect the repository

- Treat capture folders, browser screenshots, design iterations, visual-regression outputs, and exported customer images as high-risk until reviewed.
- Never upload an entire screenshot cache to make a README look rich.
- Add only the final referenced asset; confirm the PR changed-file list contains no cache directory, database, log, archive, or unrelated binary.
- Use synthetic or anonymized data in any product visual.
- Verify third-party asset licenses before copying them. Prefer original repository-native shapes and text.

## 7. Sign off visual work

1. Run `scripts/verify_project.py --strict --visual <repo>`; choose a documented `--header-style` from `readme-header.md` when the showcase default does not fit.
2. Render and inspect every new Hero or SVG.
3. Check local links, image alt text, Release/Tag links, badge targets, and mobile-width tables.
4. Review `git diff --check`, staged file sizes, and the exact staged paths.
5. After publishing, confirm the remote blob hashes or file list and inspect CI.
6. Do not claim browser or visual QA unless the rendered output was actually inspected.
