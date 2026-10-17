# Brief
Updated 2026-10-17.

## Goal
Watching a video is slow because speech is slow; reading slides is fast. VideoToPDF takes a slide-based video and produces a PDF with exactly one page per distinct slide (the slide in its final, fully built state) and, below each slide, the transcript of what was said while it was on screen. Everything runs locally on the owner's Mac.

## Non-goals
- **Not a video summarizer.** It condenses a video into slides plus the spoken text; it does not write an overall summary. (An optional per-page LLM condensation may come after v1, see D9.)
- **No cloud services.** Video, audio and transcripts never leave the machine. Speech-to-text runs locally (D4). Exception under consideration: an opt-in post-v1 LLM step via the Gemini API (D9).

## Users / stakeholders
The owner (Sergiy), for personal use. No other users or approvers.

## Success criteria
- On a slide-based lecture/talk, every distinct slide appears exactly once, in its final state; no blank, fade or transition frames.
- Each page's transcript covers exactly the time the slide was on screen, with a timestamp.
- On a video with no slides, the tool warns and still outputs whatever distinct frames it finds (D8).
- One command processes a video end to end, offline, on the Mac, in less time than the video's length, at ≲ 6 GB RAM.

## Constraints
- macOS on Apple Silicon; conda env `vid_to_pdf`; `ffmpeg` from Homebrew.
- Sample videos are third-party content and are never committed.

## Later goals (after v1)
- Product keynotes (camera cuts, stage shots, screen demos) work as well as lectures (D7).
- Videos without slides produce useful output, not just a warning (D8).
- Optional per-page notes from an LLM, possibly Gemini via API (D9).

## Open questions (for the owner)
- [x] Which test videos represent the target? - Lecture: YouTube `KV37KIh2ZAk` (owner, 2026-10-17; not downloaded yet). Keynote: `Introducing_r1.mp4`.
- [x] Videos with no slides? - Warn and output whatever frames are found (D8).
- [x] LLM step after v1? - Yes, later; no local models wanted, maybe Gemini API (D9).
- [x] Copilot/Windows support? - No; Claude Code on the Mac only (D1 confirmed).
