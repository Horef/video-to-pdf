"""Read sampled frames from a video with ffmpeg (any container/codec ffmpeg can decode)."""
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


@dataclass(frozen=True)
class VideoInfo:
    width: int
    height: int
    duration: float  # seconds


def probe(path: Path) -> VideoInfo:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    stream = data["streams"][0]
    return VideoInfo(int(stream["width"]), int(stream["height"]), float(data["format"]["duration"]))


def iter_frames(path: Path, sample_fps: float, info: VideoInfo | None = None) -> Iterator[tuple[float, np.ndarray]]:
    """Yield (time in seconds, BGR frame) at `sample_fps` frames per second, in order."""
    info = info or probe(path)
    frame_bytes = info.width * info.height * 3
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", f"fps={sample_fps}",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
        stdout=subprocess.PIPE,
    )
    try:
        index = 0
        while True:
            buf = proc.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            yield index / sample_fps, np.frombuffer(buf, np.uint8).reshape(info.height, info.width, 3)
            index += 1
    finally:
        proc.stdout.close()
        proc.kill()
        proc.wait()
