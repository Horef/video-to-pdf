"""Synthetic test clips: tiny H.264 videos built from drawn "slides" (no real videos, D5)."""
import subprocess
from pathlib import Path

import cv2
import numpy as np
import pytest

W, H, FPS = 320, 180, 10


def slide(title: str, bullets: list[str], background=(255, 255, 255)) -> np.ndarray:
    img = np.full((H, W, 3), background, np.uint8)
    cv2.putText(img, title, (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (40, 40, 160), 2, cv2.LINE_AA)
    for i, text in enumerate(bullets):
        y = 70 + 26 * i
        cv2.circle(img, (20, y - 5), 4, (0, 0, 0), -1)
        cv2.putText(img, text, (32, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    return img


def black() -> np.ndarray:
    return np.zeros((H, W, 3), np.uint8)


def hold(img: np.ndarray, seconds: float) -> list[np.ndarray]:
    return [img] * round(seconds * FPS)


def fade(a: np.ndarray, b: np.ndarray, seconds: float) -> list[np.ndarray]:
    n = round(seconds * FPS)
    return [cv2.addWeighted(a, 1 - (i + 1) / (n + 1), b, (i + 1) / (n + 1), 0) for i in range(n)]


def noise(seconds: float, seed: int = 0) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    return [rng.integers(0, 256, (H, W, 3), np.uint8) for _ in range(round(seconds * FPS))]


def write_clip(path: Path, frames: list[np.ndarray]) -> Path:
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", str(path)],
        stdin=subprocess.PIPE,
    )
    proc.communicate(b"".join(f.tobytes() for f in frames))
    assert proc.returncode == 0
    return path


SLIDE_A = slide("Intro", ["What we study", "Why it matters"])
SLIDE_B = slide("Method", ["Collect data", "Fit the model", "Check errors"])
SLIDE_C = slide("Results", ["It works", "Mostly"], background=(250, 240, 225))


@pytest.fixture
def three_slide_clip(tmp_path: Path) -> Path:
    frames = (hold(black(), 1) + fade(black(), SLIDE_A, 0.5) + hold(SLIDE_A, 3)
              + fade(SLIDE_A, SLIDE_B, 0.5) + hold(SLIDE_B, 3)
              + fade(SLIDE_B, SLIDE_C, 0.5) + hold(SLIDE_C, 3) + fade(SLIDE_C, black(), 0.5))
    return write_clip(tmp_path / "three.mp4", frames)
