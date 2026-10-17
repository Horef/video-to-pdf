"""Render slide pages into a PDF: header line, slide image, transcript as real text below (D15)."""
import functools
import io
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from videotopdf.join import speech_end
from videotopdf.slides import Slide
from videotopdf.transcribe import Segment

# Unicode TTF so non-Latin transcripts render; reportlab's built-in Helvetica is Latin-1 only.
FONT_CANDIDATES = ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"]
PARAGRAPH_GAP = 2.0       # seconds of silence that start a new transcript paragraph
MAX_IMAGE_SHARE = 0.6     # slide image takes at most this share of the page height
GREY, RED = Color(0.35, 0.35, 0.35), Color(0.65, 0.15, 0.08)


@functools.cache
def body_font() -> str:
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            pdfmetrics.registerFont(TTFont("Body", path))
            return "Body"
    return "Helvetica"


def format_time(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def paragraphs(segments: list[Segment], gap: float = PARAGRAPH_GAP) -> list[str]:
    """Join segments into paragraphs, starting a new one after a pause of `gap` seconds."""
    paras: list[list[str]] = []
    prev = None
    for seg in segments:
        if prev is None or seg.start - speech_end(prev) >= gap:
            paras.append([])
        paras[-1].append(seg.text)
        prev = seg
    return [" ".join(p) for p in paras]


def write_pdf(slides: list[Slide], path: Path, title: str, transcripts: list[list[Segment]] | None = None,
              warning: str | None = None) -> None:
    """One section per slide; a long transcript flows onto continuation pages."""
    if not slides:
        raise ValueError("no slides to write")
    if transcripts is not None and len(transcripts) != len(slides):
        raise ValueError("need one transcript list per slide")
    path.parent.mkdir(parents=True, exist_ok=True)
    font = body_font()
    header = ParagraphStyle("header", fontName=font, fontSize=9, leading=12, textColor=GREY, spaceAfter=2 * mm)
    warn = ParagraphStyle("warn", parent=header, textColor=RED)
    body = ParagraphStyle("body", fontName=font, fontSize=10.5, leading=14.5, spaceAfter=2.5 * mm)
    muted = ParagraphStyle("muted", parent=body, textColor=GREY)

    margin = 12 * mm
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=margin, title=title)
    story = []
    for i, slide in enumerate(slides):
        if i:
            story.append(PageBreak())
        story.append(Paragraph(escape(f"{format_time(slide.start)} - {format_time(slide.end)}   ·   {title}"
                                      f"   ·   {i + 1}/{len(slides)}"), header))
        if warning and i == 0:
            story.append(Paragraph(escape(warning), warn))
        iw, ih = ImageReader(io.BytesIO(slide.jpeg)).getSize()
        width = doc.width
        height = width * ih / iw
        if height > doc.height * MAX_IMAGE_SHARE:
            height = doc.height * MAX_IMAGE_SHARE
            width = height * iw / ih
        story += [Image(io.BytesIO(slide.jpeg), width=width, height=height), Spacer(1, 4 * mm)]
        if transcripts is not None:
            texts = paragraphs(transcripts[i])
            story += [Paragraph(escape(t), body) for t in texts] or [Paragraph("(no speech)", muted)]
    doc.build(story)
