"""Assign transcript segments to slide pages by time (D14)."""
from bisect import bisect_right

from videotopdf.slides import Slide
from videotopdf.transcribe import Segment

WORDS_PER_SECOND = 2.5   # typical speech rate, used to bound how long a segment's speech really lasts


def speech_end(seg: Segment) -> float:
    """Likely end of the actual speech in a segment (its timestamp end may include a pause)."""
    return seg.start + min(seg.end - seg.start, len(seg.text.split()) / WORDS_PER_SECOND)


def anchor_time(seg: Segment) -> float:
    """The moment a segment is "said": the middle of its likely speech, not of its timestamps.

    With VAD, a segment's end can stretch over a following pause (up to ~30 s, D13), so the
    plain midpoint drifts late. Speech starts at `start` and lasts about words / speech rate.
    """
    return (seg.start + speech_end(seg)) / 2


def assign_segments(slides: list[Slide], segments: list[Segment]) -> list[list[Segment]]:
    """One list of segments per slide, in order; every segment lands on exactly one slide."""
    starts = [s.start for s in slides]
    pages: list[list[Segment]] = [[] for _ in slides]
    for seg in segments:
        pages[max(0, bisect_right(starts, anchor_time(seg)) - 1)].append(seg)
    return pages
