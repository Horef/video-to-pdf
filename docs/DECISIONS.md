# Decision log
Every choice between alternatives, and every gap the code leaves that we filled ourselves. IDs are permanent. To change a decision, add a new entry and set the old one's status to "superseded by D-number of the new entry"; do not rewrite it.

## D1. Agent scaffolding: AGENTS.md canonical, CLAUDE.md shim only (2026-10-17; status: provisional - confirm with owner)
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

## D6. Environment: conda env `vid_to_pdf`, Python 3.12, from environment.yml (2026-10-17; status: provisional - confirm with owner)
- **Context:** PyCharm was configured for a conda env `vid_to_pdf` that no longer exists; there was no dependency list.
- **Decision:** Recreate `vid_to_pdf` from a committed `environment.yml` (conda-forge, Python 3.12). Python 3.12 rather than the newest release so ML/STT packages added later are likely to have wheels.
- **Alternatives:** uv/venv - not installed on this Mac; owner's other projects use conda.
- **Consequences:** `ffmpeg` stays a Homebrew system dependency.
- **Evidence / source:** `.idea/misc.xml` (`project-jdk-name="vid_to_pdf"`); `conda env create -f environment.yml` succeeded 2026-10-17.
