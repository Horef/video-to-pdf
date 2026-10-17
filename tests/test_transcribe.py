"""Transcription helpers. The real-model test is opt-in: `python -m pytest -m model`."""
import shutil
import subprocess
import wave

import pytest

from videotopdf.transcribe import (DEFAULT_MODEL, DEFAULT_VAD_MODEL, Segment, drop_repeats, extract_audio,
                                   srt_time, to_srt, transcribe)


def test_extract_audio_gives_16khz_mono_wav(tmp_path):
    src = tmp_path / "tone.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=1:sample_rate=44100",
                    "-ac", "2", "-c:a", "aac", str(src)], check=True)
    wav = tmp_path / "out.wav"
    extract_audio(src, wav)
    with wave.open(str(wav)) as w:
        assert (w.getframerate(), w.getnchannels()) == (16000, 1)
        assert w.getnframes() == pytest.approx(16000, rel=0.1)
    assert src.exists()


def test_drop_repeats_removes_loops_and_empties():
    segs = [Segment(0, 1, "Hello."), Segment(1, 2, ""), Segment(2, 3, "Loop."), Segment(3, 4, "Loop."),
            Segment(4, 5, "Loop."), Segment(5, 6, "Bye."), Segment(6, 7, "Loop.")]
    assert [s.text for s in drop_repeats(segs)] == ["Hello.", "Loop.", "Bye.", "Loop."]


def test_srt_format():
    assert srt_time(3725.5) == "01:02:05,500"
    assert to_srt([Segment(0, 1.25, "Hi.")]) == "1\n00:00:00,000 --> 00:00:01,250\nHi.\n\n"


def test_missing_model_fails_without_downloading(tmp_path):
    with pytest.raises(FileNotFoundError, match="model file not found"):
        transcribe(tmp_path / "x.mp4", model=tmp_path / "missing.bin")


@pytest.mark.model
@pytest.mark.skipif(not (DEFAULT_MODEL.is_file() and DEFAULT_VAD_MODEL.is_file()) or not shutil.which("say"),
                    reason="needs local whisper models and macOS `say`")
def test_real_model_transcribes_synthetic_speech(tmp_path):
    speech = tmp_path / "speech.aiff"
    subprocess.run(["say", "-o", str(speech), "The quick brown fox jumps over the lazy dog."], check=True)
    text = " ".join(s.text for s in transcribe(speech)).lower()
    assert "fox" in text and "lazy dog" in text
