#!/usr/bin/env python3
"""Unit tests for DarkFactory Master Audio Mixer (4-Stem Architecture)."""
import sys
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from audio_mixer_master import (
    AudioMixerMaster,
    create_procedural_foley_stem,
    create_procedural_ost_drone,
    get_ffmpeg_binary,
)


def test_get_ffmpeg_binary():
    bin_path = get_ffmpeg_binary()
    assert bin_path is not None
    assert Path(bin_path).exists() or "ffmpeg" in bin_path.lower()


def test_create_procedural_ost_drone(tmp_path):
    out_wav = tmp_path / "test_ost.wav"
    create_procedural_ost_drone(out_wav, duration=0.5)
    assert out_wav.exists()
    assert out_wav.stat().st_size > 0

    with wave.open(str(out_wav), "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 44100


def test_create_procedural_foley_stem(tmp_path):
    out_wav = tmp_path / "test_foley.wav"
    create_procedural_foley_stem(out_wav, duration=0.5)
    assert out_wav.exists()
    assert out_wav.stat().st_size > 0

    with wave.open(str(out_wav), "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 44100


def test_discover_stems():
    mixer = AudioMixerMaster()
    stems = mixer.discover_stems()
    assert "voice" in stems
    assert "ost" in stems
    assert "foley" in stems
    assert "sub_bass" in stems


@patch("subprocess.run")
def test_mix_4stems_mocked(mock_run, tmp_path):
    mixer = AudioMixerMaster(ffmpeg_bin="ffmpeg")
    voice = tmp_path / "voice.mp3"
    ost = tmp_path / "ost.wav"
    foley = tmp_path / "foley.wav"
    sub = tmp_path / "sub.wav"
    out = tmp_path / "out.mp3"

    voice.write_bytes(b"dummy")
    ost.write_bytes(b"dummy")
    foley.write_bytes(b"dummy")
    sub.write_bytes(b"dummy")

    # Mock subprocess success
    mock_run.return_value = MagicMock(returncode=0)

    # Simulate tmp target output created during command
    def side_effect(cmd, *args, **kwargs):
        # The last arg is tmp target
        target = Path(cmd[-1])
        target.write_bytes(b"mixed_audio")
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect

    success = mixer.mix_4stems(
        voice_stem=voice,
        ost_stem=ost,
        foley_stem=foley,
        sub_bass_stem=sub,
        output_file=out,
    )
    assert success is True
    assert out.exists()
