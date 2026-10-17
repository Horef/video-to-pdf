"""Local speech-to-text with whisper.cpp (pywhispercpp) and Silero VAD (D13).

Models are never downloaded here (D4); see AGENTS.md for the one-time download commands.
Standalone use: python -m videotopdf.transcribe VIDEO [-o OUT.srt]
"""
import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
DEFAULT_MODEL = MODELS_DIR / "ggml-large-v3-turbo-q5_0.bin"
DEFAULT_VAD_MODEL = MODELS_DIR / "ggml-silero-v6.2.0.bin"


@dataclass(frozen=True)
class Segment:
    start: float  # seconds
    end: float
    text: str


def extract_audio(video: Path, wav: Path) -> None:
    """16 kHz mono WAV, the format whisper.cpp expects."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
                   check=True)


def drop_repeats(segments: list[Segment]) -> list[Segment]:
    """Drop empty segments and consecutive exact repeats (Whisper's looping failure mode)."""
    kept: list[Segment] = []
    for seg in segments:
        if not seg.text or (kept and seg.text == kept[-1].text):
            continue
        kept.append(seg)
    return kept


def transcribe(video: Path, model: Path = DEFAULT_MODEL, vad_model: Path | None = DEFAULT_VAD_MODEL,
               threads: int = 8) -> list[Segment]:
    for path in (model, vad_model):
        if path is not None and not Path(path).is_file():
            raise FileNotFoundError(f"model file not found: {path} (see AGENTS.md > Environment for downloads)")
    from pywhispercpp.model import Model  # imported lazily: slide-only runs and tests don't need it

    params = {"n_threads": threads, "print_realtime": False, "print_progress": False}
    if vad_model is not None:
        params |= {"vad": True, "vad_model_path": str(vad_model)}
    whisper = Model(str(model), redirect_whispercpp_logs_to=None, **params)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        extract_audio(video, wav)
        raw = whisper.transcribe(str(wav))
    # whisper.cpp timestamps are in units of 10 ms
    return drop_repeats([Segment(s.t0 / 100, s.t1 / 100, s.text.strip()) for s in raw])


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(segments: list[Segment]) -> str:
    return "".join(f"{i}\n{srt_time(s.start)} --> {srt_time(s.end)}\n{s.text}\n\n" for i, s in enumerate(segments, 1))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="videotopdf.transcribe", description="Transcribe a video to SRT, locally.")
    parser.add_argument("video", type=Path)
    parser.add_argument("-o", "--out", type=Path, help="output .srt (default: print to stdout)")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="whisper.cpp ggml model file")
    parser.add_argument("--no-vad", action="store_true", help="transcribe silence/music too (may hallucinate)")
    args = parser.parse_args(argv)
    segments = transcribe(args.video, args.model, None if args.no_vad else DEFAULT_VAD_MODEL)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(to_srt(segments))
    else:
        sys.stdout.write(to_srt(segments))
    return 0


if __name__ == "__main__":
    sys.exit(main())
