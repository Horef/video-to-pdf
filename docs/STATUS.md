# Status
Updated 2026-10-17. Snapshot only - overwrite each session; history is in `docs/WORKLOG.md`.

## Works (verified)
| Capability | How verified |
|---|---|
| Env `vid_to_pdf` builds from `environment.yml` | `conda env update -f environment.yml --prune` → done, 2026-10-17 |
| Slide detection + PDF (`python -m videotopdf`) on synthetic clips: fades and black frames skipped, build-ups merged to the final state, short interruptions ignored, same-template slides kept apart, fallback + warning on slideless video, inputs untouched | `python -m pytest -q` → 10 passed in 4.7 s (synthetic clips only), 2026-10-17 |
| Keynote stress test (`Introducing_r1.mp4`, 1530 s) | 48 pages, no blank/fade pages, warning "does not look slide-based" (16% stable), 6.6 s, 404 MB peak RSS, 2026-10-17 |

## Doesn't work yet / known issues
- Not yet run on a real slide lecture - the expected main use case is untested.
- Keynote: repeated pages while a demo screen changes gradually (e.g. pages 3-5, 29-36); slides with a moving speaker in front never settle and are missed (e.g. "large language model" ~3:22) (D7, D10).
- No transcript yet (plan steps 3-4, D2, D3).
- Very long videos with hundreds of slides hold all rendered pages in memory while writing the PDF (Pillow); fine for typical talks, unmeasured beyond that.

## Next actions
1. Owner: download the lecture (YouTube `KV37KIh2ZAk`) into `videos/`; then run `python -m videotopdf` on it, inspect every page, tune D10 thresholds if needed.
2. Plan step 3: transcription - compare `mlx-whisper` vs a `whisper.cpp` binding; ask before downloading models.
3. Plan step 4: join transcript segments to page intervals and render them below each slide.

## Blockers
- Lecture test video not downloaded yet (not found on this machine 2026-10-17) - owner.
