"""Slide detection: find stretches where the picture holds still, keep the settled frame.

Frames are compared as small, blurred grayscale thumbnails by the fraction of pixels
that changed (see D10). A "run" is a sequence of sampled frames that all match the
run's first frame; a run that lasts at least `min_stable` seconds is a slide candidate,
represented by its *last* frame (so fades are skipped and builds are complete).
Consecutive candidates that are the same slide, or a build-up of it, are merged.
"""
from dataclasses import dataclass, field
from typing import Iterable

import cv2
import numpy as np


@dataclass(frozen=True)
class Params:
    sample_fps: float = 2.0
    min_stable: float = 1.5        # seconds a picture must hold still to count as a slide
    thumb_width: int = 320         # comparison resolution
    pixel_threshold: int = 20      # gray-level change that counts as "changed" (0-255)
    run_tolerance: float = 0.005   # max fraction of changed pixels within one run
    blank_std: float = 5.0         # thumbnails with lower gray std are blank (fades, black frames)
    slide_coverage: float = 0.4    # below this fraction of time in slides, warn (D8)
    fallback_interval: float = 60.0  # seconds between fallback frames when no slide is found


@dataclass
class Slide:
    start: float        # page interval start (s); intervals tile the whole video
    end: float          # page interval end (s)
    frame_time: float   # time of the frame shown on the page
    jpeg: bytes         # the frame shown on the page, full resolution
    thumb: np.ndarray = field(repr=False)


@dataclass
class Detection:
    slides: list[Slide]
    duration: float
    coverage: float     # fraction of the video spent on stable pictures
    fallback: bool      # True if no slide was found and evenly spaced frames were used
    looks_like_slides: bool


def thumbnail(frame: np.ndarray, width: int) -> np.ndarray:
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (width, max(1, round(h * width / w))), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)


def changed_fraction(a: np.ndarray, b: np.ndarray, pixel_threshold: int) -> float:
    return float((cv2.absdiff(a, b) > pixel_threshold).mean())


def is_blank(thumb: np.ndarray, blank_std: float) -> bool:
    return float(thumb.std()) < blank_std


def is_buildup(a: np.ndarray, b: np.ndarray, pixel_threshold: int) -> bool:
    """True if `b` is `a` with content added on `a`'s empty background (e.g. a new bullet)."""
    background = np.median(a)
    content_a = np.abs(a.astype(np.int16) - background) > pixel_threshold
    if content_a.mean() < 0.002:
        return False
    changed = cv2.absdiff(a, b) > pixel_threshold
    preserved = 1.0 - changed[content_a].mean()          # a's content is still there in b
    on_background = 1.0 - content_a[changed].mean() if changed.any() else 1.0
    return preserved >= 0.9 and on_background >= 0.85


def _encode(frame: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    assert ok
    return buf.tobytes()


def detect_slides(frames: Iterable[tuple[float, np.ndarray]], duration: float, params: Params = Params()) -> Detection:
    step = 1.0 / params.sample_fps
    candidates: list[Slide] = []
    fallback: list[Slide] = []
    stable_time = 0.0

    anchor = None                      # thumbnail of the run's first frame
    run_start = run_last_time = 0.0
    run_last_frame = run_last_thumb = None

    def close_run():
        nonlocal stable_time
        if anchor is None or is_blank(run_last_thumb, params.blank_std):
            return
        length = run_last_time - run_start + step
        if length < params.min_stable:
            return
        stable_time += length
        slide = Slide(run_start, run_last_time + step, run_last_time, _encode(run_last_frame), run_last_thumb)
        if candidates and _same_slide(candidates[-1], slide, params):
            prev = candidates[-1]
            prev.end, prev.frame_time, prev.jpeg, prev.thumb = slide.end, slide.frame_time, slide.jpeg, slide.thumb
        else:
            candidates.append(slide)

    next_fallback = 0.0
    for t, frame in frames:
        thumb = thumbnail(frame, params.thumb_width)
        if t >= next_fallback:
            fallback.append(Slide(t, t, t, _encode(frame), thumb))
            next_fallback += params.fallback_interval
        if anchor is not None and changed_fraction(anchor, thumb, params.pixel_threshold) <= params.run_tolerance:
            run_last_time, run_last_frame, run_last_thumb = t, frame, thumb
            continue
        close_run()
        anchor, run_start = thumb, t
        run_last_time, run_last_frame, run_last_thumb = t, frame, thumb
    close_run()

    used_fallback = not candidates
    slides = candidates or fallback
    _tile_intervals(slides, duration)
    coverage = stable_time / duration if duration > 0 else 0.0
    coverage = min(coverage, 1.0)
    return Detection(slides, duration, coverage, used_fallback,
                     looks_like_slides=not used_fallback and coverage >= params.slide_coverage)


def _same_slide(a: Slide, b: Slide, params: Params) -> bool:
    if changed_fraction(a.thumb, b.thumb, params.pixel_threshold) <= 2 * params.run_tolerance:
        return True
    return is_buildup(a.thumb, b.thumb, params.pixel_threshold)


def _tile_intervals(slides: list[Slide], duration: float) -> None:
    """Make page intervals cover the whole video: each runs until the next slide starts."""
    for i, slide in enumerate(slides):
        slide.start = 0.0 if i == 0 else slide.start
        slide.end = slides[i + 1].start if i + 1 < len(slides) else max(duration, slide.end)
