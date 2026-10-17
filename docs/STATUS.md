# Status
Updated 2026-10-17. Snapshot only - overwrite each session; history is in `docs/WORKLOG.md`.

## Works (verified)
| Capability | How verified |
|---|---|
| Env `vid_to_pdf` builds from `environment.yml` | `conda env create -f environment.yml` → done; imports OK (Python 3.12.15, OpenCV 5.0.0, Pillow 12.3.0), 2026-10-17 |
| Prototype `main.py` runs end to end | 60 s clip of `Introducing_r1.mp4` in a scratch copy → 2 frames, `clip.pdf` written, 10.3 s, 293 MB peak RSS, 2026-10-17 |

## Doesn't work yet / known issues
- Slide detection is poor: the 1529.9 s sample produced only 7 pages, 3 of them blank/fade frames (`pdfs/Introducing_r1.pdf`, Feb 2025). Analysis in `docs/plans/v1-slides-transcript.md`.
- No transcript in the pipeline yet (D2, D3).
- No tests.
- `main.py` deletes non-`.mp4` files in `videos/` and assumes `frames/` and `pdfs/` exist (fresh clones lack them) (D5).
- Timestamp overlay is white and invisible on white slides.

## Next actions
1. Owner: download the lecture (YouTube `KV37KIh2ZAk`) into `videos/`; the installed yt-dlp (2025.06.12) is too old for YouTube and needs updating first.
2. Plan step 1: restructure into a package with a CLI.
3. Plan step 2: new slide detection with tests on synthetic clips.

## Blockers
- Lecture test video not downloaded yet - owner (see Next actions 1).
