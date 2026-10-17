# Work log
Newest first. Each entry: what changed, how it was verified, what's next. Never edit or delete past entries.

## 2026-10-17 - Plan step 3: STT engine comparison and transcribe.py
Changed: compared mlx-whisper 0.4.3 and pywhispercpp 1.5.1 (whisper.cpp, Metal) on a 5-minute clip (keynote 2:00-7:00, 16 kHz mono) on an M2 Max; chose whisper.cpp + large-v3-turbo q5_0 + Silero VAD (D13). Added `videotopdf/transcribe.py` (standalone SRT output) and tests. Owner-approved downloads into `models/`: mlx small (481 MB), mlx turbo (1.6 GB), ggml turbo q5_0 (574 MB), Silero VAD v6.2.0 (0.9 MB); whisper.cpp small reused from MacWhisper. Env rebuilt from `environment.yml` (pip: pywhispercpp only; mlx/torch gone). Decisions: D13 (resolves D3's library choice).

Benchmarks (warm runs, `/usr/bin/time -l` on the env's python; RSS likely excludes GPU memory):

| Engine, model, options | Wall time per 5 min | Max RSS | Output on music tail (276-300 s) |
|---|---|---|---|
| whisper.cpp small (MacWhisper file) | 4.1-4.6 s | 1.0 GB | "Thanks for watching." |
| mlx small | 5.4 s (cold first run 40.6 s) | 1.0 GB | clean |
| whisper.cpp turbo q5_0 | 8.1-8.6 s | 1.0 GB | one sentence x14 |
| mlx turbo | 16.3-23.3 s; 766 vs 655 words across runs | 1.9 GB | "The" x dozens |
| whisper.cpp turbo, no_context + suppress_nst | 9.0-9.9 s | - | 2 invented segments |
| mlx turbo, no conditioning + hallucination_silence_threshold 2 | 11.5-13.3 s | - | "Bye." |
| whisper.cpp turbo + VAD (± no_context) | 6.6-7.0 s, identical across 4 runs | - | "Yeah." |

Speech quality: same across engines for the same model; turbo fixes names small gets wrong ("chat.gbt" → "ChatGPT").

| Verification command | Result |
|---|---|
| `conda env remove -n vid_to_pdf` + `conda env create -f environment.yml` | done; opencv/numpy from conda, pywhispercpp/requests from pip |
| `conda run -n vid_to_pdf python -m pytest -q` | 14 passed, 1 deselected |
| `conda run -n vid_to_pdf python -m pytest -q -m model` | 1 passed (macOS `say` sentence transcribed) |
| `/usr/bin/time -l … python -m videotopdf.transcribe videos/Introducing_r1.mp4 -o transcripts/Introducing_r1.srt` | 35.5 s, 1.32 GB max RSS, 280 segments, 3055 words, max repeat "Sure." x3 (genuine demo dialogue) |

Next: plan step 4 (join segments to slide intervals, render transcript under each slide).

## 2026-10-17 - Plan steps 1-2: videotopdf package and new slide detection
Changed: replaced `main.py` with the `videotopdf` package (ffmpeg frame reader, settle-then-capture slide detection with build-up merging, PDF pages with a timestamp header band, CLI) and pytest tests on synthetic clips. Removed unused pandas, added pytest. The GitHub repo was still empty and the lecture was not on this machine at session start. Decisions: D10, D11, D12 (supersedes D5).

| Verification command | Result |
|---|---|
| `gh api repos/Horef/video-to-pdf/commits` (session start) | "Git Repository is empty" |
| `conda run -n vid_to_pdf python -m pytest -q` | 10 passed in 4.67 s (synthetic clips) |
| `/usr/bin/time -l … python -m videotopdf videos/Introducing_r1.mp4 -o pdfs/v1 -q` | 48 pages, 16% stable, warning printed, 6.6 s, 404 MB max RSS |
| Contact sheet of the 48 keynote pages (scratch script, inspected by eye) | all pages are real content (screens, product shots, price slides); no blank/fade frames; near-duplicates during demos; "large language model (LLM)" slide (~3:22, speaker in front) missed |

Next: run on the lecture once downloaded; plan step 3 (transcription).

## 2026-10-17 - Owner answers; switch remote to video-to-pdf
Changed: remote is now `git@github.com:Horef/video-to-pdf.git` (owner created it). Recorded owner answers: lecture test video YouTube `KV37KIh2ZAk`; keynotes a later goal (D7); no-slide videos warn and output frames (D8); post-v1 LLM notes deferred, likely Gemini API (D9); D1 and D6 confirmed.

| Verification command | Result |
|---|---|
| `yt-dlp --print … KV37KIh2ZAk` (metadata only) | ERROR "The page needs to be reloaded"; installed yt-dlp 2025.06.12 is too old for YouTube |
| `git push -u origin main` | see commit message / STATUS |

Next: owner updates yt-dlp and downloads the lecture; start plan step 1.

## 2026-10-17 - Set up project foundations
Changed: revived the Feb 2025 prototype as a git repo. Added `AGENTS.md`, `CLAUDE.md`, `docs/` (BRIEF, STATUS, WORKLOG, DECISIONS, plans/v1-slides-transcript), `environment.yml`, `.gitignore`. Recreated the missing conda env `vid_to_pdf`. Assessed the prototype's output on the sample keynote (7 pages from 25.5 min, 3 blank). Owner chose: v1 = slides + transcript (D2), built-in local Whisper (D3), no cloud (D4), not a summarizer, GitHub remote `Horef/VideoToPDF`. Decisions: D1-D6.

| Verification command | Result |
|---|---|
| `ffprobe … videos/Introducing_r1.mp4` | 1529.87 s |
| Read `pdfs/Introducing_r1.pdf` | 7 pages: black frame 0.00 s, 3 content frames, 2 blank white frames, 1 talking head |
| `conda env create -f environment.yml` | done; Python 3.12.15, OpenCV 5.0.0, Pillow 12.3.0 import OK |
| `conda run -n vid_to_pdf python main.py` in scratch copy with a 60 s clip (190-250 s) | 2 frames, PDF written, 10.33 s real, 293 MB max RSS |
| Step 5 checks of the project-foundations checklist | see commit; no placeholders, no media or secrets tracked |

Next: owner supplies a slide-lecture test video; start plan step 1.
