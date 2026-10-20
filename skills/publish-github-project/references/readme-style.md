# README style

## Goal

Make the first screen answer five questions: what this is, who it helps, what state/version is current, how to see it working, and where to start. Favor trustworthy product documentation with a deliberate visual hierarchy.

For visual redesigns, read `readme-visual-design.md` after this file.

## Information order

1. Compose the opening using `readme-header.md`, the sole specification for order, alignment, and mode exceptions.
2. Select useful badges from project evidence using that specification; do not pad the count or infer missing versions/licenses.
3. Use `publication-plan.md` to choose the body reading path for apps, tools or skills. Preserve user-selected layouts and focused-update scope; record justified deviations rather than imposing one sequence on every project.
4. Keep the concrete problem early. Include a left-aligned maturity/scope callout or version entry near the top only when readers need it.
5. Select real demonstration evidence and a workflow/architecture diagram or input/output example according to that profile. SVG and Mermaid are both valid diagram formats.
6. Provide a tested shortest-path quick start and verification, then link deeper capabilities, architecture, security, limitations, contribution and license information where useful.

## Writing rules

- Match the repository's primary language; default to Chinese for predominantly Chinese projects.
- Use a concrete verb-led value proposition. Avoid unverifiable superlatives.
- Put user outcomes before the technology stack.
- Keep paragraphs short and tables narrow enough for mobile GitHub rendering.
- Use consistent names for services, commands, ports, versions, and stages.
- Label internal pilots, prototypes, and incomplete paths explicitly.
- Link to deeper documents instead of overloading the README.
- Omit unsupported or low-value sections.

## Evidence checklist

- Derive install commands from manifests and scripts, then run them when safe.
- Verify every local link, image path, badge target, Release, and Tag.
- Confirm version numbers, ports, filenames, dependency versions, test totals, and status labels.
- Ensure screenshots, examples, diagrams, and output snippets contain only synthetic data.
- Ensure the license statement matches the actual license file or clearly states that no license is granted.
- Compare the remote changed-file list with the intended scope after publishing.

## Visual restraint

- Apply the opening alignment in `readme-header.md`; keep body reading comfortable and left aligned.
- Keep one dominant Hero and one compact relationship visual at most.
- Prefer a current, purposeful image over a gallery of stale screenshots.
- Avoid emoji decoration unless the project already uses that voice.
- Use one accent system and consistent geometry; do not mix unrelated badge, illustration, and banner styles.
- Preserve a real H1 and descriptive alt text even when title typography appears inside the Hero.
