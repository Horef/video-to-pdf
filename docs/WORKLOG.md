# Work log
Newest first. Each entry: what changed, how it was verified, what's next. Never edit or delete past entries.

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
