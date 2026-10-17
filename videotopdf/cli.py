"""Command line: python -m videotopdf VIDEO_OR_DIR... [-o OUTDIR]"""
import argparse
import sys
import time
from pathlib import Path

from tqdm import tqdm

from videotopdf.frames import VIDEO_SUFFIXES, iter_frames, probe
from videotopdf.render import write_pdf
from videotopdf.slides import Detection, Params, detect_slides

NO_SLIDES_WARNING = "Warning: this video does not look slide-based; pages are whatever stable frames were found."
FALLBACK_WARNING = "Warning: no slides found; pages are frames taken every {interval:.0f} s."


def collect_videos(inputs: list[Path]) -> list[Path]:
    videos = []
    for item in inputs:
        if item.is_dir():
            videos += sorted(p for p in item.iterdir() if p.suffix.lower() in VIDEO_SUFFIXES)
        elif item.is_file():
            videos.append(item)
        else:
            raise FileNotFoundError(item)
    return videos


def warning_for(detection: Detection, params: Params) -> str | None:
    if detection.fallback:
        return FALLBACK_WARNING.format(interval=params.fallback_interval)
    if not detection.looks_like_slides:
        return NO_SLIDES_WARNING
    return None


def process(video: Path, out_dir: Path, params: Params, quiet: bool = False) -> tuple[Path, Detection]:
    info = probe(video)
    frames = iter_frames(video, params.sample_fps, info)
    if not quiet:
        frames = tqdm(frames, total=int(info.duration * params.sample_fps), unit="frame", desc=video.name)
    detection = detect_slides(frames, info.duration, params)
    out = out_dir / f"{video.stem}.pdf"
    write_pdf(detection.slides, out, video.stem, warning_for(detection, params))
    return out, detection


def main(argv: list[str] | None = None) -> int:
    defaults = Params()
    parser = argparse.ArgumentParser(prog="videotopdf", description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="video files or directories of videos")
    parser.add_argument("-o", "--out-dir", type=Path, default=Path("pdfs"), help="output directory (default: pdfs)")
    parser.add_argument("--sample-fps", type=float, default=defaults.sample_fps)
    parser.add_argument("--min-stable", type=float, default=defaults.min_stable,
                        help="seconds a picture must hold still to count as a slide")
    parser.add_argument("--run-tolerance", type=float, default=defaults.run_tolerance,
                        help="max fraction of changed pixels for two frames to count as the same picture")
    parser.add_argument("-q", "--quiet", action="store_true", help="no progress bar")
    args = parser.parse_args(argv)
    params = Params(sample_fps=args.sample_fps, min_stable=args.min_stable, run_tolerance=args.run_tolerance)

    videos = collect_videos(args.inputs)
    if not videos:
        print("No videos found.", file=sys.stderr)
        return 1
    for video in videos:
        started = time.monotonic()
        out, detection = process(video, args.out_dir, params, args.quiet)
        print(f"{video.name}: {len(detection.slides)} pages, {detection.duration:.0f} s video, "
              f"{detection.coverage:.0%} stable, {time.monotonic() - started:.1f} s -> {out}")
        warning = warning_for(detection, params)
        if warning:
            print(f"  {warning}", file=sys.stderr)
    return 0
