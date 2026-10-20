# README language editions

Apply when the user requests a bilingual title, multiple README editions, or maintenance of existing translations. A bilingual title alone does not require translating the whole repository. Preserve the project's chosen primary language; do not force English or two editions on every project.

## Identity and switching

- For a requested Chinese/English README, use `README.md` as the chosen default and `README.en.md` (or the established locale filename) as the other complete edition.
- Keep one semantic H1. A Chinese primary identity can use `<h1>中文项目名称<br><sub>English Project Name</sub></h1>`. The English edition may reverse the order. Keep the code/package identifier unchanged.
- Put a separate centered switch immediately after the H1, before the Hero. Use relative Markdown links in both files, including the current language; bold the current choice. Do not hardcode `main`, so preview branches and forks continue to work.

```markdown
**[简体中文](README.md)** · [English](README.en.md)
```

In the English edition, move the bold emphasis to English. The language switch is separate from section navigation and badges. Switching opens the other README; GitHub does not automatically translate content or guarantee that it retains the current scroll position.

## Keep content in sync

- Translate the useful content, tables, prompts, notices, captions, and alt text, not just headings. Match capabilities, omissions, prerequisites, version, license, authorization boundaries, and verification claims.
- Share version/license badges and other language-neutral assets. Translate text-heavy workflow diagrams when needed. Existing bilingual brand art can remain shared; do not invent a translated product interface.
- Translate heading anchors and navigation links within each edition. Keep code paths, package identifiers, runnable commands, and actual repository URLs correct. Label links to untranslated secondary guides with their language.
- When editing a maintained claim or step, update every supplied edition in the same change. Review a section-by-section mapping; structural checks cannot establish semantic translation parity.

## Verify each edition

```shell
python /path/to/skill/scripts/verify_project.py /path/to/repo --strict --visual
python /path/to/skill/scripts/verify_project.py /path/to/repo --strict --visual --readme README.en.md
```

`--readme` checks the selected file and resolves its assets relative to that file. A publication plan records the default README baseline, so use `--plan` on a separate default-README invocation. These checks verify local Markdown targets, structure and media, not translation accuracy or reciprocal navigation.

After an authorized preview publication, open both GitHub pages and click each language switch. Check that the branch is retained, section anchors work, shared images load, translated diagrams remain readable, titles stay centered, and mobile/light/dark layouts remain usable. Do not report a full English documentation set when only the README has been translated.
