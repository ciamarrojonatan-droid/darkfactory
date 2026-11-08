#!/usr/bin/env python3
"""Unit tests for DarkFactory Kokoro-82M TTS Local Fallback Engine."""
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kokoro_fallback import KokoroNarrator


def test_map_instruct_urgency():
    profile = KokoroNarrator.map_instruct_to_voice_profile(
        "Speak with controlled urgency and mounting dread, deep authoritative baritone"
    )
    assert profile["voice"] in ("am_fenrir", "am_adam")
    assert profile["speed"] >= 1.0


def test_map_instruct_somber_grim():
    profile = KokoroNarrator.map_instruct_to_voice_profile(
        "Slow down pace, speak in a grim, somber, heavy baritone, emphasizing tragic existential weight"
    )
    assert profile["voice"] == "am_onyx"
    assert profile["speed"] < 1.0


def test_map_instruct_suspense():
    profile = KokoroNarrator.map_instruct_to_voice_profile(
        "Intense cinematic suspense, hushed dramatic delivery, deliberate pause after orders"
    )
    assert profile["voice"] == "am_adam"
    assert profile["speed"] < 1.0


def test_map_instruct_default():
    profile = KokoroNarrator.map_instruct_to_voice_profile("")
    assert profile["voice"] == "am_adam"
    assert profile["speed"] == 0.92


@patch.object(KokoroNarrator, "_synthesize_edge_fallback", new_callable=AsyncMock)
def test_synthesize_scene_mocked(mock_synth, tmp_path):
    narrator = KokoroNarrator()
    out_file = tmp_path / "scene_test.mp3"

    mock_synth.return_value = True

    # Simulate output file creation by the async call
    def create_file(*args, **kwargs):
        out_file.write_bytes(b"dummy_mp3_data")
        return True

    mock_synth.side_effect = create_file

    ok = narrator.synthesize_scene(
        scene_id=1,
        tts_text="Five missiles detected.",
        instruct_text="urgent dread",
        output_file=out_file,
    )
    assert ok is True
    assert out_file.exists()


def test_process_script_missing():
    narrator = KokoroNarrator()
    fake_path = Path("non_existent_script_12345.json")
    assert narrator.process_script(fake_path) is False
