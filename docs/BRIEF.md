# Brief
Updated 2026-10-17.

## Goal
Watching a video is slow because speech is slow; reading slides is fast. VideoToPDF takes a slide-based video and produces a PDF with exactly one page per distinct slide (the slide in its final, fully built state) and, below each slide, the transcript of what was said while it was on screen. Everything runs locally on the owner's Mac.

## Non-goals
- **Not a video summarizer.** It condenses a video into slides plus the spoken text; it does not write an overall summary. (An optional per-page LLM condensation may come after v1, see open questions.)
- **No cloud services.** Video, audio and transcripts never leave the machine. Speech-to-text runs locally (D4).

## Users / stakeholders
The owner (Sergiy), for personal use. No other users or approvers.

## Success criteria
- On a slide-based lecture/talk, every distinct slide appears exactly once, in its final state; no blank, fade or transition frames.
- Each page's transcript covers exactly the time the slide was on screen, with a timestamp.
- One command processes a video end to end, offline, on the Mac, in less time than the video's length, at ≲ 6 GB RAM.

## Constraints
- macOS on Apple Silicon; conda env `vid_to_pdf`; `ffmpeg` from Homebrew.
- Sample videos are third-party content and are never committed.

## Open questions (for the owner)
- [ ] Which test videos represent the target? The only sample (`Introducing_r1.mp4`) is a product keynote with camera cuts, the hardest case. A real slide lecture is needed to tune against.
- [ ] Videos with no slides (talking head, camera-only) - skip, warn, or just output sparse frames? Blocks defining "done" for those inputs.
- [ ] After v1: add an optional LLM step that condenses each page's transcript into notes? Would need a local model to respect D4.
- [ ] Should Copilot/Windows be supported for this repo? Currently only Claude Code on the Mac is assumed (D1).
