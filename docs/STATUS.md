# Status
Updated 2026-10-17. Snapshot only - overwrite each session; history is in `docs/WORKLOG.md`.

## Works (verified)
| Capability | How verified |
|---|---|
| Env `vid_to_pdf` builds from `environment.yml` | removed and recreated with `conda env create -f environment.yml` → done, 2026-10-17 |
| Slide detection + PDF (`python -m videotopdf`) on synthetic clips: fades and black frames skipped, build-ups merged to the final state, short interruptions ignored, same-template slides kept apart, fallback + warning on slideless video, inputs untouched; transcription helpers | `python -m pytest -q` → 14 passed, 1 deselected, in an env rebuilt from `environment.yml` (synthetic clips only), 2026-10-17 |
| Transcription (`python -m videotopdf.transcribe`), whisper.cpp turbo + VAD | full keynote (1530 s) → 280 segments, 3055 words, no loops, 35.5 s, 1.3 GB peak RSS; opt-in `pytest -m model` → 1 passed (synthetic `say` speech), 2026-10-17 |
| Keynote stress test (`Introducing_r1.mp4`, 1530 s) | 48 pages, no blank/fade pages, warning "does not look slide-based" (16% stable), 6.6 s, 404 MB peak RSS, 2026-10-17 |

## Doesn't work yet / known issues
- Not yet run on a real slide lecture - the expected main use case is untested.
- Keynote: repeated pages while a demo screen changes gradually (e.g. pages 3-5, 29-36); slides with a moving speaker in front never settle and are missed (e.g. "large language model" ~3:22) (D7, D10).
- Transcript is not in the PDF yet (plan step 4); transcription runs standalone only.
- Some VAD segments span ~20-30 s across pauses (D13); matters for the join.
- Transcript quality judged by reading only; no reference transcript.
- Very long videos with hundreds of slides hold all rendered pages in memory while writing the PDF (Pillow); fine for typical talks, unmeasured beyond that.

## Next actions
1. Owner: download the lecture (YouTube `KV37KIh2ZAk`) into `videos/`; then run `python -m videotopdf` on it, inspect every page, tune D10 thresholds if needed.
2. Plan step 4: join transcript segments to page intervals and render them below each slide.
3. Owner: decide whether to delete the unused mlx models in `models/` (~2 GB: `whisper-small-mlx`, `whisper-large-v3-turbo`).

## Blockers
- Lecture test video not downloaded yet (not found on this machine 2026-10-17) - owner.
