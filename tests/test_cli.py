"""End-to-end CLI run on a synthetic clip."""
import re

import videotopdf.cli as cli
from conftest import noise, write_clip
from videotopdf.cli import main
from videotopdf.render import format_time
from videotopdf.transcribe import Segment


def pdf_pages(path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?!s)", path.read_bytes()))


def test_cli_writes_one_page_per_slide_and_keeps_input(three_slide_clip, tmp_path):
    out_dir = tmp_path / "out" / "nested"
    assert main([str(three_slide_clip), "-o", str(out_dir), "-q", "--no-transcript"]) == 0
    pdf = out_dir / "three.pdf"
    assert pdf.exists() and pdf_pages(pdf) == 3
    assert three_slide_clip.exists()


def test_cli_accepts_a_directory_and_warns_on_slideless_video(tmp_path, capsys):
    videos = tmp_path / "videos"
    videos.mkdir()
    write_clip(videos / "noise.mp4", noise(3))
    (videos / "notes.txt").write_text("not a video")
    assert main([str(videos), "-o", str(tmp_path / "pdfs"), "-q", "--no-transcript"]) == 0
    assert (tmp_path / "pdfs" / "noise.pdf").exists()
    assert "Warning" in capsys.readouterr().err
    assert (videos / "notes.txt").exists()


def test_cli_puts_transcript_under_slides(three_slide_clip, tmp_path, monkeypatch):
    # Real transcription is covered by the opt-in model test; here a canned transcript stands in.
    calls = []
    def fake_transcribe(video, model, vad_model):
        calls.append(video)
        return [Segment(6.0, 7.0, "About the method."), Segment(9.0, 10.0, "word " * 900)]
    monkeypatch.setattr(cli, "transcribe", fake_transcribe)
    model = tmp_path / "fake.bin"
    model.write_bytes(b"")
    monkeypatch.setattr(cli, "DEFAULT_VAD_MODEL", model)
    assert main([str(three_slide_clip), "-o", str(tmp_path), "-q", "--model", str(model)]) == 0
    assert calls == [three_slide_clip]
    assert pdf_pages(tmp_path / "three.pdf") > 3      # the 900-word transcript flows onto an extra page


def test_cli_missing_model_exits_before_work(three_slide_clip, tmp_path, capsys):
    assert main([str(three_slide_clip), "-o", str(tmp_path), "-q", "--model", str(tmp_path / "none.bin")]) == 2
    assert "--no-transcript" in capsys.readouterr().err
    assert not (tmp_path / "three.pdf").exists()


def test_format_time():
    assert format_time(0) == "0:00"
    assert format_time(75.4) == "1:15"
    assert format_time(3725) == "1:02:05"
