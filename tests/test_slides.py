"""Slide detection on synthetic clips (tests/conftest.py)."""
import cv2
import numpy as np
import pytest

from conftest import SLIDE_A, SLIDE_B, SLIDE_C, black, fade, hold, noise, slide, write_clip
from videotopdf.frames import iter_frames, probe
from videotopdf.slides import Params, changed_fraction, detect_slides, is_buildup, thumbnail

P = Params()


def detect(path, params=P):
    info = probe(path)
    return detect_slides(iter_frames(path, params.sample_fps, info), info.duration, params)


def page_matches(slide_obj, expected: np.ndarray) -> bool:
    frame = cv2.imdecode(np.frombuffer(slide_obj.jpeg, np.uint8), cv2.IMREAD_COLOR)
    a, b = thumbnail(frame, P.thumb_width), thumbnail(expected, P.thumb_width)
    return changed_fraction(a, b, P.pixel_threshold) < 0.01


def test_three_slides_with_fades_and_black_lead_in(three_slide_clip):
    d = detect(three_slide_clip)
    assert len(d.slides) == 3
    for s, expected in zip(d.slides, [SLIDE_A, SLIDE_B, SLIDE_C]):
        assert page_matches(s, expected)
    assert d.looks_like_slides and not d.fallback


def test_intervals_tile_the_video(three_slide_clip):
    d = detect(three_slide_clip)
    assert d.slides[0].start == 0.0
    assert d.slides[-1].end == pytest.approx(d.duration)
    for prev, nxt in zip(d.slides, d.slides[1:]):
        assert prev.end == nxt.start
    # B is on screen from ~5.0 s (1 s black + 0.5 fade + 3 s A + 0.5 fade); sampling is every 0.5 s
    assert d.slides[1].start == pytest.approx(5.0, abs=0.6)


def test_bullet_buildup_becomes_one_page_with_all_bullets(tmp_path):
    steps = [slide("Plan", ["One"]), slide("Plan", ["One", "Two"]), slide("Plan", ["One", "Two", "Three"])]
    frames = sum((hold(s, 2) for s in steps), []) + hold(SLIDE_B, 2)
    d = detect(write_clip(tmp_path / "build.mp4", frames))
    assert len(d.slides) == 2
    assert page_matches(d.slides[0], steps[-1])
    assert page_matches(d.slides[1], SLIDE_B)


def test_short_interruption_does_not_split_a_slide(tmp_path):
    frames = hold(SLIDE_A, 3) + hold(SLIDE_C, 0.3) + hold(SLIDE_A, 3)
    d = detect(write_clip(tmp_path / "glitch.mp4", frames))
    assert len(d.slides) == 1


def test_same_template_different_text_stays_separate(tmp_path):
    a = slide("Part 1", ["Alpha beta", "Gamma"])
    b = slide("Part 2", ["Delta", "Epsilon zeta"])
    d = detect(write_clip(tmp_path / "template.mp4", hold(a, 2) + hold(b, 2)))
    assert len(d.slides) == 2


def test_no_stable_picture_falls_back_and_warns(tmp_path):
    d = detect(write_clip(tmp_path / "noise.mp4", noise(4)))
    assert d.fallback and not d.looks_like_slides
    assert len(d.slides) >= 1


def test_is_buildup_unit():
    t = lambda img: thumbnail(img, P.thumb_width)
    one, two = slide("Plan", ["One"]), slide("Plan", ["One", "Two"])
    assert is_buildup(t(one), t(two), P.pixel_threshold)
    assert not is_buildup(t(two), t(one), P.pixel_threshold)        # content removed
    assert not is_buildup(t(SLIDE_A), t(SLIDE_B), P.pixel_threshold)
    assert not is_buildup(t(black()), t(SLIDE_A), P.pixel_threshold)  # nothing to build on
