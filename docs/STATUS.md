# Status
Updated 2026-10-17. Snapshot only - overwrite each session; history is in `docs/WORKLOG.md`.

## Works (verified)
| Capability | How verified |
|---|---|
| Env `vid_to_pdf` builds from `environment.yml` | recreated from file earlier today; `conda env update -f environment.yml` after adding reportlab → done, 2026-10-17 |
| Test suite (synthetic clips; transcriber stubbed): slide detection, transcription helpers, join, PDF render, CLI | `python -m pytest -q` → 23 passed, 1 deselected, 2026-10-17 |
| Real Whisper model on synthetic speech | `python -m pytest -q -m model` → 1 passed (macOS `say`), 2026-10-17 |
| End to end on the keynote (`python -m videotopdf videos/Introducing_r1.mp4 -o pdfs/v1`) | 48 slides → 48-page PDF, 4.8 MB, 43.9 s, 1.45 GB peak RSS; every page read: transcript is real text and lands on the matching screen; slideless warning shown, 2026-10-17 |
| Standalone SRT (`python -m videotopdf.transcribe`) | keynote → 280 segments, 35.5 s, 2026-10-17 |

## Doesn't work yet / known issues
- Not yet run on a real slide lecture - the main use case is untested (plan verification step).
- Keynote: 15 of 48 pages are near-duplicate demo screens with "(no speech)"; slides with a moving speaker in front are missed (D7, D10).
- Long VAD segments: a sentence spoken across a slide change goes wholly to one page (D14).
- Non-Latin transcripts need macOS Arial Unicode; elsewhere the Helvetica fallback cannot show them (D15).

## Next actions
1. Owner: download the lecture (YouTube `KV37KIh2ZAk`) into `videos/`; run `python -m videotopdf videos/<file> -o pdfs`, read every page, tune D10 thresholds if needed. That closes the v1 plan.
2. Keynote polish (D7): merge "(no speech)" near-duplicate pages into their neighbour; consider region masking for speakers in front of slides.

## Blockers
- Lecture test video not on this machine (checked 2026-10-17) - owner.
