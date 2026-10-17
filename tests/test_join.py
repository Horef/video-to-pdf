"""Joining transcript segments to slide pages (D14)."""
import numpy as np
import pytest

from videotopdf.join import anchor_time, assign_segments, speech_end
from videotopdf.render import paragraphs
from videotopdf.slides import Slide
from videotopdf.transcribe import Segment


def slides_at(*starts, end=100.0):
    out = [Slide(s, 0, s, b"", np.zeros((1, 1), np.uint8)) for s in starts]
    for a, b in zip(out, out[1:] + [None]):
        a.end = b.start if b else end
    return out


def test_anchor_ignores_trailing_pause():
    # 5 words ≈ 2 s of speech; the 30 s timestamp span is mostly a pause after it
    seg = Segment(10.0, 40.0, "one two three four five")
    assert speech_end(seg) == pytest.approx(12.0)
    assert anchor_time(seg) == pytest.approx(11.0)


def test_anchor_is_midpoint_for_dense_speech():
    seg = Segment(10.0, 12.0, " ".join(["w"] * 20))   # faster than 2.5 words/s
    assert anchor_time(seg) == pytest.approx(11.0)


def test_every_segment_lands_on_the_slide_it_was_said_during():
    slides = slides_at(0.0, 20.0, 50.0)
    segs = [Segment(1, 3, "a b c"), Segment(18, 45, "said just before slide two"),
            Segment(21, 23, "on two"), Segment(49.5, 52, "x y z w v u t"), Segment(80, 90, "last")]
    pages = assign_segments(slides, segs)
    assert [[s.text for s in p] for p in pages] == [
        ["a b c", "said just before slide two"], ["on two"], ["x y z w v u t", "last"]]
    assert sum(map(len, pages)) == len(segs)


def test_paragraph_breaks_on_pauses():
    segs = [Segment(0, 2, "One two."), Segment(2.2, 4, "Three four."), Segment(10, 12, "After a pause."),
            Segment(12, 30, "Long tail."), Segment(13.5, 14, "Still same paragraph.")]
    assert paragraphs(segs) == ["One two. Three four.", "After a pause. Long tail. Still same paragraph."]
