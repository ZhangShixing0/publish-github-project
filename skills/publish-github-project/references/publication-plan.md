# Project structure and local publication records

Read for initial publication, substantive README redesigns, or media replacement. A typo, single link fix, or metadata-only update does not need a new plan.

## Two intents, three content profiles

Infer intent from the request: initial publication or improvement of an existing repository. Within an improvement, keep media-only changes focused. Do not ask again when context already establishes the choice.

Choose the closest content profile using the actual audience and task. These are recommended reading paths, not mandatory heading wording:

| Profile | Default body order after the opening | Evidence |
| --- | --- | --- |
| `app` | Problem → demonstration → workflow → quick start → capabilities, limits and deeper docs | Current screenshots/video, role handoffs, runnable entry |
| `tool` | Purpose → minimal input/output → installation → common usage → integration and limits | Real command/API example; diagram only if relationships warrant it |
| `skill` | User problem → deliverables → execution workflow → installation and first instruction → boundaries | Actual outputs, execution stages and authorization points |

Keep a concise problem explanation early. Version navigation can move earlier when readers genuinely need it; record the reason for any different order. Several roles may share one section when it clearly answers each question. Explicit user layouts and accepted focused-update scope take precedence. Use `readme-header.md` for the opening and `readme-visual-design.md` for visual styling; do not create a competing header specification here.

## Diagram decisions

- Multiple roles, handoffs or human review: prefer a compact business workflow; retain a role table when it adds input/output detail.
- Multiple interacting services: an architecture diagram may be more useful than a sequential flowchart.
- A one-step CLI/library transformation: a real input/output example can make a diagram unnecessary.
- A multi-stage skill: show user input, meaningful stages and final deliverables.
- Inventory existing SVG/PNG/Mermaid diagrams before proposing new ones. Format alone does not determine presence or quality.
- Select `image`, `mermaid`, or `none` with a concrete reason for omission. For media-only scope, `unchanged` preserves the existing diagram decision.
- Verify diagram facts and readable labels at desktop/mobile sizes. A structurally valid graph still needs rendering inspection. If GitHub Mermaid fails after a bounded check, follow the static fallback guidance in `readme-visual-design.md`.

## Capture before editing

The record is a local working aid, not another form for the user. Derive decisions from repository evidence and conversation; ask only about unresolved material choices.

```shell
python scripts/publication_plan.py init /path/to/project --profile skill --scope readme --output /private/task/plan.json
```

Use `--scope initial`, `readme`, or `media`. The output must be outside the target repository. The initializer copies the current README to a sibling baseline file, records its SHA-256, maps existing H2 sections, and suggests modules. It refuses to overwrite existing records. The draft deliberately leaves unresolved decisions incomplete.

Keep this record for later updates, but take a new baseline for each new task. Never replace a baseline merely to make a failed check pass. Existing user decisions should be carried forward only within their original scope; the latest explicit request governs a changed choice.

## Record fields

- `schema_version`: `1`.
- `profile` / `scope`: the selected values above.
- `baseline.file` / `sha256`: captured README and hash. Leave unchanged during this task.
- `modules`: ordered objects with `role`, exact `heading`, and `omit_reason`. Resolve each profile role, share headings where justified, or explain why an inapplicable module is omitted. A missing heading is an unfinished decision.
- `order_note`: why the actual module order differs from the planned order, if applicable.
- `preserve`: one record for every baseline H2, with exact `source` and `target` headings. `keep`/`move` require unchanged section body; `rewrite` requires `review_note` describing the semantic comparison. `remove` requires a concrete reason consistent with user intent. Moving details to another document still leaves an understandable overview/link in the README and counts as a reviewed rewrite.
- `diagram`: `kind` plus `heading` for an included diagram; `image` also needs its repository-relative `path`; `none`/`unchanged` need `reason`.
- `media`: one record per new/replaced published media file; see below.
- `retired_paths`: repository-relative files that must no longer exist in the candidate tree.
- `retired_references`: old asset paths/URLs that must no longer appear in the README. Separately check other affected docs and external surfaces within the requested scope. This does not purge Git history or delete hosted attachments.

### Versioned media

Record each supplied source independently, including new versions of the same video:

```json
{
  "source_file": "/private/task/supplied-video.mp4",
  "source_sha256": "replace-with-computed-source-sha256",
  "published_path": "docs/assets/intro.mp4",
  "published_sha256": "replace-with-computed-candidate-sha256",
  "transform": "original",
  "decision_note": "Use the newly supplied original in this update.",
  "review_note": "Reviewed the intended output.",
  "privacy_review": "Record the actual review and scoped decision for this source version.",
  "references": ["docs/assets/intro.mp4"]
}
```

Supported transformations: `original`, `transcode`, `redact`, `edit`. Original means byte-for-byte equality. Every transformed output needs its own decision and completed review notes. For an authorized redacted master and derived preview, use separate records: the preview's source is the reviewed master. Never treat a historical redaction choice as permission to alter a newly supplied source, or a new filename as privacy clearance.

Use streamed SHA-256 hashing, not filenames, to establish identity. Remote-only attachment workflows can keep the exact upload candidate in an ignored local location, record its repository-relative candidate path, and put the returned URL in `references`; the candidate need not be committed. Separately verify the actual remote bytes/playback. Local paths, review notes and baseline content may be private; do not publish these records.

## Verify and interpret

```shell
python scripts/verify_project.py /path/to/project --strict --plan /private/task/plan.json
python scripts/publication_plan.py verify /path/to/project --plan /private/task/plan.json
```

Checks cover section presence/order, baseline mapping, unreviewed text changes, declared image/Mermaid presence, local media hashes, original-byte equality, and retired files/README references. Missing/ambiguous inputs fail explicitly.

The parser supports common ATX, setext and HTML headings; baseline preservation tracks H2 sections. Opening text, unusual Markdown structures, linked external documents, semantic accuracy, privacy decisions, graph meaning and live playback still need direct review. A review note records the agent's completed comparison; it is not automatic proof or a new user approval requirement. Never auto-fill generic review notes just to clear failures.
