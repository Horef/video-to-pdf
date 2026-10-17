Status: proposed (2026-10-17)

# v1: slides + transcript PDF

## Objective
One command turns a slide-based video into a PDF: one page per distinct slide (final state), with the transcript of that slide's time interval below it (D2), fully local (D3, D4).

## Non-goals
- Overall video summaries; LLM condensation (post-v1).
- Handling videos without slides well: v1 only warns and outputs what it finds (D8).
- Tuning for product keynotes: later goal, but don't design them out (D7).

## Why the prototype fails (evidence)
On `Introducing_r1.mp4` (1529.9 s keynote) `main.py` kept 7 frames: a black frame at 0.00 s, two blank white frames (1210.50 s, 1276.36 s) and only a few real scenes. Causes, from reading `main.py`:
- The threshold is `mean_diff / frame_percentage` = 100 × the average frame-to-frame difference, so only hard cuts pass.
- It captures the *first* frame after a change, i.e. mid-fade, not the settled slide.
- Every full-resolution frame is decoded and compared twice (two passes).
- Timestamps are drawn in white and vanish on white slides.

## Steps
1. **Restructure** into a small package (`videotopdf/`: `frames.py`, `slides.py`, `transcribe.py`, `render.py`, `cli.py`) with a CLI taking an input path and output path. Never delete inputs; create output dirs (D5 follow-up). Keep `main.py` until the new CLI matches it, then remove it.
2. **Slide detection** (`slides.py`), outputting `(start_s, end_s, frame)` intervals:
   - Sample ~2 fps via ffmpeg/OpenCV at reduced resolution, grayscale.
   - Compare to the last *stable* frame with SSIM or a perceptual hash, not raw mean difference.
   - Capture a slide only after the picture has been stable for ~1-2 s; keep the last frame of a stable run so incremental builds end up complete.
   - Drop frames that are near-uniform (black/white fades).
   - Merge consecutive slides where the later one contains the earlier (bullet build-ups); dedupe revisited slides.
   - Flag videos that don't look slide-based and warn (D8).
3. **Transcription** (`transcribe.py`): compare `mlx-whisper` vs a `whisper.cpp` binding on a 5-minute clip (speed, RAM, quality); record choice as a new D entry; output timestamped segments. Ask before downloading models.
4. **Join + render** (`render.py`): assign each segment to the slide interval containing its midpoint; render pages (slide image on top, timestamp, wrapped transcript below) with Pillow or reportlab.
5. **Tests**: tiny synthetic clips generated in the test (solid-color "slides" with fades and a build-up) for slide detection; a canned segment list for the join; no real videos, no model in the default test run.

## Verification
- `pytest` green on synthetic clips.
- Manual: run on the slide lecture (YouTube `KV37KIh2ZAk`, owner downloads into `videos/`) and on `Introducing_r1.mp4` (keynote stress test, D7); inspect every page; record page counts and observations in `docs/WORKLOG.md`.
- Runtime < video length and peak RAM ≲ 6 GB (`/usr/bin/time -l`).

## Risks
- Camera-cut videos (keynotes) produce many near-duplicate shots; may need a "slide-likeness" filter.
- Speaker picture-in-picture over slides defeats whole-frame comparison; may need masking or region-based comparison.
