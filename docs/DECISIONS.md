# Decision log
Every choice between alternatives, and every gap the code leaves that we filled ourselves. IDs are permanent. To change a decision, add a new entry and set the old one's status to "superseded by D-number of the new entry"; do not rewrite it.

## D1. Agent scaffolding: AGENTS.md canonical, CLAUDE.md shim only (2026-10-17; status: accepted - confirmed by owner 2026-10-17)
- **Context:** Personal project worked on from the owner's Mac. Owner's standing convention is AGENTS.md as the single rules file.
- **Decision:** Rules live in `AGENTS.md`; `CLAUDE.md` is `@AGENTS.md`. No `.github/copilot-instructions.md` or Kiro steering file.
- **Alternatives:** Add a Copilot shim - not needed unless the repo is used on the Windows machine (open question in BRIEF).
- **Consequences:** Add the Copilot shim if the repo is ever opened with Copilot.
- **Evidence / source:** Owner defaults; project setup session 2026-10-17.

## D2. v1 output: slide image plus its transcript on each PDF page (2026-10-17; status: accepted)
- **Context:** The prototype produced slides only; transcripts were made separately in MacWhisper.
- **Decision:** v1 produces one PDF page per detected slide, with the transcript of that slide's time interval (and a timestamp) below the image. Slide intervals and transcript segments are joined by timestamp.
- **Alternatives:** Slides only first - postpones the most useful part; LLM-condensed notes per page - extra dependency, deferred past v1.
- **Consequences:** Slide detection must output time intervals, not just frames.
- **Evidence / source:** Owner choice, 2026-10-17.

## D3. Speech-to-text runs locally with Whisper, built into the pipeline (2026-10-17; status: accepted; library chosen in D13)
- **Context:** Owner used MacWhisper (a GUI around Whisper) because writing STT seemed like reinventing the wheel. Whisper can be called directly from Python on Apple Silicon.
- **Decision:** The pipeline calls a local Whisper implementation and uses its timestamped segments. Candidate libraries: `mlx-whisper` (Apple Silicon native) and `whisper.cpp` bindings; pick one in plan step 3 after a short comparison and record it as a new D entry.
- **Alternatives:** Import MacWhisper `.srt` exports - keeps a manual step; cloud STT APIs - ruled out by D4.
- **Consequences:** A one-time model download (hundreds of MB to ~3 GB depending on size) needs owner approval.
- **Evidence / source:** Owner choice, 2026-10-17.

## D4. Local only, no cloud services (2026-10-17; status: accepted)
- **Context:** Videos may be private; owner listed "no cloud services" as a non-goal.
- **Decision:** No network calls at runtime other than a one-time, user-approved model download.
- **Alternatives:** Cloud STT or multimodal LLM APIs - faster to build, but send media off the machine.
- **Consequences:** Any future LLM note-taking step must use a local model or be explicitly opt-in with a superseding decision.
- **Evidence / source:** Owner choice, 2026-10-17.

## D5. Media never committed; no READMEs inside videos/ or frames/ for now (2026-10-17; status: superseded by D12)
- **Context:** `videos/` holds third-party videos (sample is 68 MB); `pdfs/` and `frames/` are outputs. The usual convention tracks a README inside each ignored directory, but `main.py` deletes every non-`.mp4` file in `videos/` (after attempting an ffmpeg conversion) and everything in `frames/`.
- **Decision:** Ignore `videos/`, `pdfs/`, `frames/` entirely; document the layout in `AGENTS.md` instead of per-directory READMEs.
- **Alternatives:** Tracked READMEs - would be deleted by the next run of `main.py`.
- **Consequences:** Fresh clones lack these directories; `main.py` does not create them (see STATUS). Revisit when the pipeline is rewritten: it should create its own directories and never delete inputs.
- **Evidence / source:** `main.py` (video conversion loop and `frames/` clean-up), read 2026-10-17.

## D6. Environment: conda env `vid_to_pdf`, Python 3.12, from environment.yml (2026-10-17; status: accepted - confirmed by owner 2026-10-17)
- **Context:** PyCharm was configured for a conda env `vid_to_pdf` that no longer exists; there was no dependency list.
- **Decision:** Recreate `vid_to_pdf` from a committed `environment.yml` (conda-forge, Python 3.12). Python 3.12 rather than the newest release so ML/STT packages added later are likely to have wheels.
- **Alternatives:** uv/venv - not installed on this Mac; owner's other projects use conda.
- **Consequences:** `ffmpeg` stays a Homebrew system dependency.
- **Evidence / source:** `.idea/misc.xml` (`project-jdk-name="vid_to_pdf"`); `conda env create -f environment.yml` succeeded 2026-10-17.

## D7. Product keynotes are a target, after slide lectures (2026-10-17; status: accepted)
- **Context:** Keynotes (camera cuts, stage shots, screen demos, e.g. `Introducing_r1.mp4`) are much harder than slide lectures for change-based slide detection.
- **Decision:** v1 is tuned and judged on slide lectures. Keynotes are an explicit later goal: v1 design must not rule them out (e.g. keep detection pluggable, per-frame scores inspectable), but v1 is not blocked on them.
- **Alternatives:** Lectures only, forever - owner wants keynotes ideally; keynotes in v1 - would stall v1 on the hardest case.
- **Consequences:** Keep running `Introducing_r1.mp4` as a regression/stress sample and log its results.
- **Evidence / source:** Owner, 2026-10-17.

## D8. Videos without slides: warn and output whatever frames are found (2026-10-17; status: accepted)
- **Context:** Talking-head or camera-only videos have no slides to capture.
- **Decision:** The tool still runs, outputs the distinct frames it finds with their transcript, and prints a warning (and notes it in the PDF) that the video appears to have no slides. Making these videos genuinely useful is a later goal.
- **Alternatives:** Skip the video - loses the transcript; fail - unfriendly.
- **Consequences:** Needs a simple "looks like slides?" heuristic to trigger the warning.
- **Evidence / source:** Owner, 2026-10-17.

## D9. Post-v1 LLM notes: deferred; likely a cloud API (Gemini), not a local model (2026-10-17; status: accepted)
- **Context:** D4 says no cloud services. Owner has no local models and prefers not to install any; suggested Gemini via API.
- **Decision:** No LLM step in v1. If added later, it is opt-in and sends only transcript text (and optionally slide images) to the chosen API; implementing it requires a new decision that narrows D4 for that step. Video and audio still never leave the machine.
- **Alternatives:** Local LLM - owner prefers not to; no LLM ever - owner wants it eventually.
- **Consequences:** Keep page rendering separate from text content so a notes field can be added later.
- **Evidence / source:** Owner, 2026-10-17.

## D10. Slide detection: settle-then-capture on changed-pixel fraction (2026-10-17; status: accepted)
- **Context:** The prototype captured the first frame after a big mean difference: it missed most slides and caught fades (plan, "Why the prototype fails").
- **Decision:** Sample 2 fps via ffmpeg; compare 320 px-wide blurred grayscale thumbnails by the fraction of pixels whose gray level changed by > 20. A run is frames within 0.5% change of the run's first frame; a run lasting ≥ 1.5 s is a slide, shown by its last frame. Near-uniform thumbnails (std < 5) are dropped. Consecutive slides merge if they differ by ≤ 1% or the later one is a build-up (the earlier one's content is preserved and changes lie on its background). Page intervals tile the whole video so no speech is lost later. Videos with < 40% stable time get a warning (D8); if nothing is stable, frames every 60 s are used.
- **Alternatives:** SSIM or perceptual hash (plan's first idea) - a mean score hides a small changed region (one changed line on a white slide scores ~0.97) and the build-up check needs a pixel mask anyway; PySceneDetect - detects cuts, not settled slides.
- **Consequences:** Thresholds are tuned on synthetic clips and one keynote so far; tune on the lecture. A moving speaker in front of or beside a slide prevents it from settling (keynote missed "large language model" at ~3:22) - region masking is future work (D7).
- **Evidence / source:** `pytest` 10 passed (synthetic clips); keynote run 2026-10-17 in WORKLOG.

## D11. Revisited slides are kept as separate pages (2026-10-17; status: accepted)
- **Context:** The plan said to dedupe a slide shown again later. With transcripts (D2), a revisit carries different speech.
- **Decision:** Only *consecutive* duplicates are merged; a slide shown again after another slide gets its own page.
- **Alternatives:** Global dedupe - loses the time order of the transcript.
- **Consequences:** Some repeated pages in talks that flip back and forth.
- **Evidence / source:** Reasoning, 2026-10-17 (plausible, untested on a real lecture).

## D12. Prototype replaced by the `videotopdf` package; inputs are never modified (2026-10-17; status: accepted)
- **Context:** `main.py` converted non-mp4 inputs and deleted the originals, and wiped `frames/` (D5). Plan step 1.
- **Decision:** `main.py` is removed (it remains in git history, commit a8b314e). The package reads any ffmpeg-decodable file directly, keeps keyframes in memory as JPEG, writes only to the output directory and creates it. Media is still never committed. `frames/` is no longer used.
- **Alternatives:** Keep `main.py` alongside - two diverging pipelines.
- **Consequences:** READMEs inside `videos/` would now be safe; not added (the layout is documented in AGENTS.md).
- **Evidence / source:** `tests/test_cli.py` checks the input clip and a non-video file survive a run.

## D13. STT engine: whisper.cpp via pywhispercpp, large-v3-turbo q5_0, Silero VAD (2026-10-17; status: accepted)
- **Context:** D3 left the library open between `mlx-whisper` and a whisper.cpp binding; plan step 3 compared them on a 5-minute clip (keynote 2:00-7:00) on the owner's M2 Max.
- **Decision:** Use `pywhispercpp` 1.5.1 (whisper.cpp with Metal) with `ggml-large-v3-turbo-q5_0.bin` and VAD (`ggml-silero-v6.2.0.bin`), model files in `models/`, never auto-downloaded (D4). Consecutive identical segments are dropped as a safeguard.
- **Alternatives:** `mlx-whisper` - same quality on speech (same weights) but ~1.5-2x slower on turbo (11.5-23 s vs 6.6-9.9 s per 5 min), ~250 MB of dependencies (torch, numba, scipy) vs 4 MB, run-to-run differences without extra options, and no built-in VAD; `small` model - 2x faster again but misspells names ("chat.gbt"); no VAD - both engines invent text over music (14x repeated sentence, dozens of "The").
- **Consequences:** VAD can merge across pauses, giving segments up to ~30 s long; the join in plan step 4 must handle segments that span a slide change. MacWhisper's existing `ggml-model-whisper-small.bin` works as a `--model` fallback.
- **Evidence / source:** Benchmarks in WORKLOG 2026-10-17 (measured; quality judged by reading, no reference transcript - plausible, not established).

## D14. Transcript-to-slide join by estimated speech midpoint (2026-10-17; status: accepted)
- **Context:** Plan step 4 said "assign each segment to the slide interval containing its midpoint". With VAD, a segment's end often stretches over the pause after it (up to ~30 s, D13), which pushes the midpoint late, possibly onto the next slide.
- **Decision:** Anchor each segment at the middle of its *likely* speech: from `start` to `start + min(duration, words / 2.5 words per second)`; assign it to the slide whose interval contains the anchor. Segments are never split; paragraphs break after a ≥ 2 s pause measured the same way.
- **Alternatives:** Plain midpoint - drifts late on VAD segments; word-level timestamps - more precise but slower and splits sentences across pages; start time only - biased early for long sentences.
- **Consequences:** A sentence spoken across a slide change goes wholly to one page. 2.5 words/s is a typical rate, not measured per speaker.
- **Evidence / source:** `tests/test_join.py`; keynote PDF read 2026-10-17 (speech lands on the matching screens; plausible, not measured against ground truth).

## D15. PDF written with reportlab: real text, Unicode font, flowing pages (2026-10-17; status: accepted)
- **Context:** The Pillow renderer rasterised text into the page image: transcripts would not be searchable or copyable, long ones could not flow, and the built-in font lacked characters (the en dash rendered as a box).
- **Decision:** `render.py` uses reportlab platypus: A4 portrait, header line, slide image (JPEG embedded as-is, at most 60% of page height), transcript paragraphs that flow onto continuation pages. Font: macOS Arial Unicode if present, else Helvetica (Latin-1 only).
- **Alternatives:** Keep Pillow - not searchable; HTML → PDF (weasyprint) - heavier dependencies.
- **Consequences:** Adds `reportlab` (conda-forge). Text extraction from the PDF works (verified by reading the keynote PDF).
- **Evidence / source:** `tests/test_render.py`; keynote run 2026-10-17 in WORKLOG.
