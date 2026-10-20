# README opening contract

This is the single source of truth for the default opening layout. Use it for new READMEs and authorized header redesigns. An explicit user layout or an accepted existing layout in a focused update takes precedence; record that exception instead of silently rearranging unrelated content.

## Default: showcase

Keep these five elements in one centered identity block, in this order:

1. One semantic project H1.
2. One current Hero with descriptive alt text.
3. One short, concrete value sentence (prefer bold).
4. One quick-navigation paragraph, normally three to five useful links.
5. One badge paragraph, normally two to five verified, nonredundant badges.

Close the centered block before any maturity/scope callout or body content. Paragraphs, tables, commands, and detailed explanations in the body stay left aligned. Add a callout only for a material limitation; never invent a limitation to fill the template.

Do not move the badges above the Hero, combine navigation with badges, place a long introduction in the identity block, or alternate alignment between its elements. Use blank lines between Markdown blocks and HTML wrappers, as in `assets/readme-template.md`. Do not rely on custom CSS, flexbox, or fixed no-wrap rows in GitHub. Badge and navigation rows may wrap naturally on mobile.

### Other modes and focused updates

- **Compact:** for libraries and CLIs, keep the same centered H1 → value → navigation → badges order; an optional compact logo/visual may appear after the title. Put the real usage snippet and install command in the left-aligned body. A cinematic Hero is unnecessary.
- **Preserve:** for an explicit user layout, evidence report, or a narrow update to an accepted layout, retain that layout. Supply a concrete `--header-note` with `--header-style preserve`. This skips the default arrangement checks, not link, asset, SVG, privacy, or truthfulness checks. Do not select this mode just to suppress an unexplained failure.
- Header-only or badge-only work should preserve the chosen arrangement unless the user asks to change it. Do not redesign other published repositories merely because this default has changed.

## Badge selection is an evidence decision

Before writing badges, make a short working list of **label/value → source → include/omit reason**. It is a verification note, not an extra README section. Assess these dimensions:

| Dimension | Evidence to check | Selection rule |
| --- | --- | --- |
| Current version or stage | Manifest, actual tag/release, or an explicit project status | Use a real version when available; otherwise a supported stage. Do not invent v1.0 or a Release link. |
| Essential technology/runtime | Imports, dependency manifest, vendored library header, tested runtime | Select what helps a reader understand or run this project. Distinct authoring and browser runtimes may both matter. |
| License/permissions | Actual license file and owner's decision | Match existing permissions. A public repository is not automatically MIT or open source. |
| Additional useful status | Existing CI, measured coverage, supported platforms | Include only when it adds information and the value/target can be verified. |

Two to five is a readability guideline, not a completeness score. A three-badge opening can be better than five redundant badges. Prefer version/stage, an essential runtime, and licensing when all are established; explain unavailable dimensions in the working note, not with fabricated badges. Never add CI, downloads, stars, coverage, or compatibility solely as decoration. A generic project-type badge must not crowd out useful current-state information.

### Select for the project and reader

- Rank candidates by the project's main use and intended reader. For a browser product, its primary framework and browser runtime usually matter more than a build-time prerequisite; for a CLI or SDK, the installation runtime may be essential. Select distinct signals rather than a dependency list.
- When the user references an accepted project, inspect the available example and reuse its badge density and familiar visual treatment where appropriate.
- For feedback such as "too few" or "not suitable", reassess relevance, size and style before increasing the count. Keep features and detailed validation in the body unless a badge helps the reader decide something.
- Review the combined row at normal reading size and record the strongest inclusion/omission choices. If version and stage overlap, keep one badge and explain maturity in the body. Structural validation does not establish that the selection is useful or visually balanced.

Keep local SVG badges in `docs/badges/` (or another `badges/` directory) so tooling recognizes them. Use one consistent style and readable label/value text. Keep them self-contained, with `<title>`/`<desc>` and meaningful README alt text. Link badges to real evidence or the relevant README section when useful. A static version badge is legitimate without a Git tag; do not create a release to justify it.

## Hero framing

- Prefer a horizontal composition around 2:1–2.4:1. Show the product large enough to understand while preserving essential edges and controls. Recapture/reframe a real product when possible; do not stretch the image or fabricate implemented UI.
- Avoid a tall full-width screenshot that pushes the value, navigation, and badges far below the opening. If the whole scene needs a taller frame, use a concise horizontal opening and place the detailed/full view in the body, or retain an explicitly requested layout.
- Keep photo/capture explanations in alt text or a body caption when possible, rather than inserting an extra introductory paragraph between the five elements.
- Preserve each project's colors, visual identity, and truthful content. A common reading order does not require identical banners.

## Verification

Run `python scripts/verify_project.py --strict --visual <repo>` for the showcase default. Use `--header-style compact` for a compact opening, or `--header-style preserve --header-note "specific reason"` for an intentional exception. `--header-style showcase` can also check the opening without `--visual`. Routine nonvisual checks without a header option do not force an unrelated existing README redesign.

The checker detects missing/duplicate titles, missing badges, misplaced or split badge paragraphs, wrong opening order, mixed alignment, centered body content, and an unusually tall local Hero when its dimensions are readable. It recognizes local badge paths and does not count them as a Hero. It is a structural heuristic: it cannot establish whether a badge claim is true, whether prose is a good value sentence, or whether GitHub actually renders attractively.

Inspect the actual GitHub README at desktop and mobile widths after an authorized publication. Check the five-element order, image framing, readable badges, natural wrapping, left-aligned body, and light/dark legibility. Before publication, a local preview is provisional; do not label it GitHub rendering evidence. Resolve structural warnings or document a real layout exception; retain manual evidence checks even when the script passes.
