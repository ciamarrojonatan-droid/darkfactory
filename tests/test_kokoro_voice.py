"""Test suite for Kokoro-82M ONNX local TTS engine."""

import os
from pathlib import Path
import pytest


def test_kokoro_model_files_exist():
    """Verify Kokoro ONNX model and voices bin exist when local weights are installed."""
    base_dir = Path(__file__).resolve().parent.parent
    model_dir = base_dir / "data" / "models" / "kokoro"
    onnx_file = model_dir / "kokoro-v0_19.onnx"
    voices_file = model_dir / "voices.bin"

    if not onnx_file.exists() or not voices_file.exists():
        pytest.skip("Optional Kokoro ONNX weights not present locally")

    assert onnx_file.stat().st_size > 10_000_000, "ONNX model too small"
    assert voices_file.exists(), f"Missing voices at {voices_file}"


def test_kokoro_synthesis_output():
    """Verify kokoro generated voice file exists and is valid WAV when generated."""
    base_dir = Path(__file__).resolve().parent.parent
    staging_file = base_dir / "data" / "staging" / "kokoro_pilot_voice.wav"

    if not staging_file.exists():
        pytest.skip("Optional staging WAV not generated yet")

    assert staging_file.stat().st_size > 50_000, "Audio file too small"


def test_kokoro_default_voice_bm_george():
    """Verify default voice is bm_george in DarkFactory Kokoro fallback."""
    import sys
    base_dir = Path(__file__).resolve().parent.parent
    df_src = base_dir / "src"
    added = False
    if str(df_src) not in sys.path:
        sys.path.append(str(df_src))
        added = True

    try:
        from kokoro_fallback import DEFAULT_VOICE, KokoroNarrator
        assert DEFAULT_VOICE == "bm_george", f"Expected bm_george, got {DEFAULT_VOICE}"

        profile = KokoroNarrator.map_instruct_to_voice_profile("")
        assert profile["voice"] == "bm_george"
    finally:
        if added and str(df_src) in sys.path:
            sys.path.remove(str(df_src))


def test_kokoro_mastered_audio_assets_exist():
    """Verify mastered pilot assets for bm_george and bm_lewis exist in DarkFactory."""
    base_dir = Path(__file__).resolve().parent.parent
    df_audio = base_dir / "data" / "audio"
    df_subs = base_dir / "data" / "subtitles"

    george_mp3 = df_audio / "pilot_bm_george_mastered.mp3"
    george_wav = df_audio / "pilot_bm_george_mastered.wav"
    george_srt = df_subs / "pilot_bm_george_full.srt"

    assert george_mp3.exists(), f"Missing {george_mp3}"
    assert george_mp3.stat().st_size > 100_000, "George MP3 too small"
    if george_wav.exists():
        assert george_wav.stat().st_size > 100_000, "George WAV too small"
    assert george_srt.exists(), f"Missing {george_srt}"

    lewis_mp3 = df_audio / "pilot_bm_lewis_mastered.mp3"
    assert lewis_mp3.exists(), f"Missing {lewis_mp3}"
    assert lewis_mp3.stat().st_size > 100_000, "Lewis MP3 too small"
