"""PDF rendering with transcripts."""
import re

import cv2
import numpy as np
import pytest

from conftest import SLIDE_A, SLIDE_B
from videotopdf.render import write_pdf
from videotopdf.slides import Slide
from videotopdf.transcribe import Segment


def slide_from(img, start, end):
    ok, buf = cv2.imencode(".jpg", img)
    return Slide(start, end, start, buf.tobytes(), np.zeros((1, 1), np.uint8))


def pages(path):
    return len(re.findall(rb"/Type\s*/Page(?!s)", path.read_bytes()))


def test_one_page_per_slide_with_short_transcripts(tmp_path):
    slides = [slide_from(SLIDE_A, 0, 10), slide_from(SLIDE_B, 10, 20)]
    out = tmp_path / "x" / "talk.pdf"
    write_pdf(slides, out, "talk", [[Segment(1, 2, "Hello <b>&</b> ünïcødé — 你好")], []], warning="Heads up")
    assert pages(out) == 2


def test_long_transcript_flows_onto_more_pages(tmp_path):
    out = tmp_path / "long.pdf"
    write_pdf([slide_from(SLIDE_A, 0, 600)], out, "long", [[Segment(i, i + 1, "lorem ipsum " * 20) for i in range(60)]])
    assert pages(out) >= 3


def test_transcript_count_must_match_slides(tmp_path):
    with pytest.raises(ValueError):
        write_pdf([slide_from(SLIDE_A, 0, 1)], tmp_path / "bad.pdf", "bad", [[], []])
