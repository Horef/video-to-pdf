"""End-to-end CLI run on a synthetic clip."""
import re

from conftest import noise, write_clip
from videotopdf.cli import main
from videotopdf.render import format_time


def pdf_pages(path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?!s)", path.read_bytes()))


def test_cli_writes_one_page_per_slide_and_keeps_input(three_slide_clip, tmp_path):
    out_dir = tmp_path / "out" / "nested"
    assert main([str(three_slide_clip), "-o", str(out_dir), "-q"]) == 0
    pdf = out_dir / "three.pdf"
    assert pdf.exists() and pdf_pages(pdf) == 3
    assert three_slide_clip.exists()


def test_cli_accepts_a_directory_and_warns_on_slideless_video(tmp_path, capsys):
    videos = tmp_path / "videos"
    videos.mkdir()
    write_clip(videos / "noise.mp4", noise(3))
    (videos / "notes.txt").write_text("not a video")
    assert main([str(videos), "-o", str(tmp_path / "pdfs"), "-q"]) == 0
    assert (tmp_path / "pdfs" / "noise.pdf").exists()
    assert "Warning" in capsys.readouterr().err
    assert (videos / "notes.txt").exists()


def test_format_time():
    assert format_time(0) == "0:00"
    assert format_time(75.4) == "1:15"
    assert format_time(3725) == "1:02:05"
