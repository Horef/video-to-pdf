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

## D3. Speech-to-text runs locally with Whisper, built into the pipeline (2026-10-17; status: accepted; library choice provisional)
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

## D5. Media never committed; no READMEs inside videos/ or frames/ for now (2026-10-17; status: accepted)
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
