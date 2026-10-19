# Project media

## Choose the available evidence

Inspect the repository and supplied assets before requesting media from the user. For a product showcase, use the following defaults within the requested publishing scope; a focused text or metadata update does not automatically need new screenshots.

| Situation | Default action |
| --- | --- |
| Suitable screenshots already exist | Verify that they show the current product, are legible, and contain publishable data; reuse or selectively recapture them. |
| Screenshots are missing and the product can run locally | Proactively start an isolated local instance using documented setup and synthetic data, then capture representative real views. Routine local startup and capture do not need another preference question. |
| Startup, access, or capture is blocked | Make a bounded attempt using the documented path and a targeted, low-impact correction when justified. Explain the concrete missing condition, ask only for necessary information, and continue independent README work. Use a truthful Hero or workflow diagram meanwhile. |
| The project has no graphical interface | Prefer actual command usage, sample input/output, or a relevant architecture diagram. Do not invent a GUI. |
| No video is available and the user has not required one | Omit the video section and its navigation link. Complete a coherent README without empty placeholders or a video-production dependency. |
| The user explicitly requires a video | Treat it as a deliverable. Resolve missing source material or production scope early; continue independent work, but do not report the publication task complete while the required video is missing. |

## Capture real product screenshots

1. Select views that explain the product's central task and observable result, usually a small set of two to four views when useful. Reuse an existing demo/experience mode or documented synthetic fixtures. A screenshot-only request does not authorize building missing features.
2. Run from an isolated checkout or disposable local environment, bound to loopback where appropriate. Keep runtime data and capture artifacts outside the intended commit scope. Do not connect to production data or modify a shared database to obtain a screenshot.
3. Use available browser or application capture tools. Complete the real interactions needed to show the selected state. Wait for images to finish decoding, layouts to settle, and transient notices to clear before capturing; inspect the resulting image, not just the tool's success status.
4. Keep screen contents faithful to the running product. Frames, captions, and layouts may present captured views, but must not add fictional controls or results. Label static demos and synthetic metrics. A designed Hero, mockup, or diagram is not a product screenshot.
5. Check legibility at the intended README size and mobile width when relevant. Inspect private information and publish only the final referenced assets, with descriptive alt text and concise captions. Preserve enough local provenance to identify the version, demo/fixture, and captured views; exclude credentials, session state, and raw private records.
6. Stop task-owned preview processes when capture is finished. Verify the published assets and layout using the README visual checks.

If accounts, unavailable services, or capture tools prevent this flow, name the blocker and request only what is needed. Missing screenshots do not require asking the user to provide an entire media package. Avoid turning the publishing task into a broad dependency migration or application repair; retain honest limitations and continue the work that is possible.

## Optional video production

Video is optional by default. If none was supplied, a brief delivery note may mention that it can be added later; do not interrupt ordinary publication merely to ask whether the user wants one. Do not silently expand screenshot preparation into scriptwriting, recording, voiceover, or editing.

When video production is requested, infer the goal and available material from context, clarify only unresolved choices that affect the result (such as demonstrated workflow, duration, or narration), and use an appropriate available production workflow. The following instructions cover preparing and publishing an existing video.

## Publish an existing video

Use the supplied video and verified product facts. Preserve the user's edit and narration unless they request changes.

### Prepare

- Inspect duration, file size, video/audio codecs, dimensions, and pixel format with an available media probe. Sample the beginning, product views, sensitive interfaces, and ending; inspect any frames that may contain personal or customer data.
- A “fictional/demo” label is not by itself evidence that visible identifiers are safe. Resolve material privacy findings within existing authorization, asking the user only when a decision remains unresolved. For authorized redaction, check repeated appearances, transitions, filenames, source paths, captions, thumbnails, and any spoken identifiers; reviewing one occurrence is insufficient.
- After redaction, derive every public preview and full-quality download from the reviewed redacted master. Keep the unredacted source local; an “original” or “1080p” download link must not expose fields hidden in the inline preview. Recheck the affected intervals after encoding, plus duration and intended audio preservation.
- Consult GitHub's current [attachment documentation](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files) before selecting an upload route. Limits depend on the destination and account; do not hardcode a previously observed limit as universal.
- Prefer the original when it fits and plays correctly. If a smaller preview is needed, preserve the complete timeline and audio, use browser-compatible encoding, and verify duration and playback. Keep a safety margin below the actual upload limit.
- Choose storage deliberately: a native GitHub attachment can provide inline playback; a stable original download may be a referenced repository asset or release asset according to repository size and update frequency. Creating a release requires its own authority. Do not automatically add two large copies to Git history.

### Present

- Put the video where it helps the reader understand the product, with a concise description, honest duration, and a full-quality link when available.
- Use the native attachment URL returned by GitHub when inline playback is needed. A raw repository MP4 link alone is not proof of an inline player.
- Add chapter times only when checked against the supplied video. Collapse the chapter list when it interrupts scanning.
- Keep asset filenames stable and meaningful. Only publish the final referenced media; exclude encoder logs, profiles, contact sheets, and temporary exports.

### Verify

- Verify a retained original byte-for-byte using a cryptographic hash or Git blob ID. For a transcoded preview, compare duration and inspect representative visual and audio segments.
- Test the actual published README on desktop and mobile: wait for GitHub hydration, confirm a stable video element, play muted, observe time advancing, and check dimensions and media errors. A poster frame alone does not prove playback.
- Confirm the download target resolves and the README does not create horizontal page overflow. Keep browser profiles and QA captures outside the commit scope.
