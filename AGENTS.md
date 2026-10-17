# VideoToPDF - agent instructions

A personal, local command-line tool that turns a slide-based video (lecture, talk, screen recording) into a PDF you can read quickly: one page per distinct slide, with what was said during that slide printed below it.
It is **not** a video summarizer and uses **no cloud services** - video and audio never leave the machine.
Goal, scope and open questions: `docs/BRIEF.md`. Current work plan: `docs/plans/v1-slides-transcript.md`.

## Start of every session
1. `git status` and `git pull --rebase`. Do not commit, discard or overwrite changes you did not make; ask.
2. Read `docs/STATUS.md`. Skim the latest entry in `docs/WORKLOG.md`.
3. Before changing behavior covered by a decision, read it in `docs/DECISIONS.md`.

## Environment and commands
- Env: conda env `vid_to_pdf` (Python 3.12), defined in `environment.yml`. Run everything as `conda run -n vid_to_pdf python …`. Never use the base interpreter.
- Install / recreate: `conda env create -f environment.yml` (update: `conda env update -f environment.yml --prune`). Add every new dependency to `environment.yml` (conda-forge first; pip section only for what conda lacks).
- `ffmpeg` comes from Homebrew (`/opt/homebrew/bin/ffmpeg`), not from the env.
- Run: `conda run -n vid_to_pdf python -m videotopdf videos/ -o pdfs` - takes video files or directories, writes `<out>/<video stem>.pdf` (slides + transcript; needs the models below, or `--no-transcript`). `--help` lists tuning flags.
- Transcribe only: `conda run -n vid_to_pdf python -m videotopdf.transcribe VIDEO -o transcripts/NAME.srt` (whisper.cpp + VAD, D13).
- Models (one-time, git-ignored `models/`; the code never downloads them, D4):
  `curl -L -o models/ggml-large-v3-turbo-q5_0.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin` (574 MB) and
  `curl -L -o models/ggml-silero-v6.2.0.bin https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v6.2.0.bin` (0.9 MB).
- Tests (offline, ~5 s): `conda run -n vid_to_pdf python -m pytest -q`. They build tiny synthetic clips with ffmpeg; never use real videos in tests. Opt-in real-model test: `… pytest -q -m model` (needs `models/` and macOS `say`).
- Limits: keep local runs modest (≲ 6 GB RAM). Ask before downloading models or large files, or running on long videos for tuning sweeps.

## Layout
- `videotopdf/` - the package: `frames.py` (ffmpeg frame reader), `slides.py` (slide detection, D10), `transcribe.py` (whisper.cpp, D13), `join.py` (segments → slides, D14), `render.py` (reportlab PDF, D15), `cli.py`.
- `tests/` - pytest; `conftest.py` draws synthetic slide clips.
- `videos/` - input videos. Git-ignored.
- `pdfs/` - output PDFs. `transcripts/` - SRT output. `models/` - whisper/VAD model files. All git-ignored.
- `docs/` - brief, status, worklog, decisions, plans.

## Boundaries
- Never commit: videos, PDFs, frames, transcripts, model weights, `.idea/`, `.env*`. They are in `.gitignore`; never `git add -f` them. Sample videos are third-party content.
- The pipeline never modifies or deletes its inputs; it only writes into the output directory (D12).

## Conventions
- Local only (D4): no network calls at runtime other than a one-time, user-approved model download.
- Tune slide detection by looking at the produced PDF pages, not only at frame counts; record what you tried in `docs/WORKLOG.md`.

## Keeping the project maintained
Update docs in the same commit as the change that requires it:

| When you… | Update |
|---|---|
| finish a unit of work | `docs/STATUS.md` (snapshot) and a new `docs/WORKLOG.md` entry with the commands you ran and their results |
| choose between alternatives, or fill a gap the code leaves | add the next-numbered D entry to `docs/DECISIONS.md`; to reverse one, add a new entry that supersedes it |
| change the CLI, outputs or dependencies | `AGENTS.md` commands, `environment.yml` |
| work on or finish a plan step | its plan file in `docs/plans/` (Status line, checked steps) |

- Never describe planned or partial work as done. Say how something was verified; label tests on synthetic clips as such.
- Keep this file short. Project knowledge belongs in `docs/`; add a rule here only if an agent got it wrong.

## Git
- Remote `origin` = `git@github.com:Horef/video-to-pdf.git`, branch `main`, commit directly to `main`.
- Commit each logical, tested change: Conventional Commits (`feat(scope): …`, `fix: …`, `docs: …`), summary ≤72 chars, body says why; cite D ids.
- Before committing: tests green (code changes), `git diff --check` clean, `git status` and staged diff reviewed for never-commit files.
- After committing: `git push origin main`. If the SSH key prompts for a passphrase, run the push unpiped so the user can type it; never ask for or store it. If you can't push, say so.
- Never force-push, rewrite pushed history or amend pushed commits. Ask before anything destructive.
