"""Render detected slides into a PDF: one page per slide, timestamp in a header band."""
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from videotopdf.slides import Slide

MAX_PAGE_WIDTH = 1600
HEADER_COLOR = (238, 238, 238)
TEXT_COLOR = (30, 30, 30)
WARN_COLOR = (170, 40, 20)


def format_time(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def render_page(slide: Slide, number: int, total: int, title: str, warning: str | None = None) -> Image.Image:
    image = Image.open(io.BytesIO(slide.jpeg)).convert("RGB")
    if image.width > MAX_PAGE_WIDTH:
        image = image.resize((MAX_PAGE_WIDTH, round(image.height * MAX_PAGE_WIDTH / image.width)), Image.LANCZOS)
    font_size = max(14, image.width // 60)
    font = ImageFont.load_default(size=font_size)
    lines = [(f"{format_time(slide.start)} - {format_time(slide.end)}    {title}    {number}/{total}", TEXT_COLOR)]
    if warning:
        lines.append((warning, WARN_COLOR))
    line_height = round(font_size * 1.5)
    header = line_height * len(lines) + font_size // 2
    page = Image.new("RGB", (image.width, image.height + header), HEADER_COLOR)
    draw = ImageDraw.Draw(page)
    for i, (text, color) in enumerate(lines):
        draw.text((font_size // 2, font_size // 4 + i * line_height), text, fill=color, font=font)
    page.paste(image, (0, header))
    return page


def write_pdf(slides: list[Slide], path: Path, title: str, warning: str | None = None) -> None:
    if not slides:
        raise ValueError("no slides to write")
    path.parent.mkdir(parents=True, exist_ok=True)
    pages = [render_page(s, i + 1, len(slides), title, warning if i == 0 else None) for i, s in enumerate(slides)]
    pages[0].save(path, save_all=True, append_images=pages[1:], resolution=150)
