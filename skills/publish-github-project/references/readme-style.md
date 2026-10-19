# README style

## Goal

Make the first screen answer five questions: what this is, who it helps, what state/version is current, how to see it working, and where to start. Favor trustworthy product documentation with a deliberate visual hierarchy.

For visual redesigns, read `readme-visual-design.md` after this file.

## Information order

1. Semantic H1, one-sentence value proposition, and optional Hero that communicates the product rather than adding decoration.
2. Short quick-navigation row and two to five verified badges. Separate navigation from status badges.
3. One GitHub callout for the most important maturity, safety, or scope limitation.
4. Version center near the top when the repository has Releases, Tags, multiple retained versions, or frequent confusion about the current version.
5. Problem and workflow, expressed with a narrow table and/or small Mermaid diagram when each clarifies distinct relationships.
6. Implemented capabilities and system components.
7. Tested quick start, verification command, and one synthetic example.
8. Deeper architecture, directory tree, security boundary, limitations, roadmap, contribution, and license. Collapse secondary detail when useful.

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

- Center the identity block, not the entire document.
- Keep one dominant Hero and one compact relationship visual at most.
- Prefer a current, purposeful image over a gallery of stale screenshots.
- Avoid emoji decoration unless the project already uses that voice.
- Use one accent system and consistent geometry; do not mix unrelated badge, illustration, and banner styles.
- Preserve a real H1 and descriptive alt text even when title typography appears inside the Hero.
