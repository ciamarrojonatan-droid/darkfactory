#!/usr/bin/env python3
"""Unit tests for DarkFactory Google Flow RPA Bot."""
import json
import sys
from pathlib import Path
import pytest

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from google_flow_bot import GoogleFlowBot


def test_bot_initialization(tmp_path):
    broll = tmp_path / "broll"
    session = tmp_path / "session"
    bot = GoogleFlowBot(broll_dir=broll, session_dir=session)
    assert bot.broll_dir == broll
    assert bot.session_dir == session
    assert broll.exists()
    assert session.exists()


def test_dispatch_missing_queues(tmp_path):
    bot = GoogleFlowBot(broll_dir=tmp_path / "broll")
    with pytest.raises(FileNotFoundError):
        bot.dispatch_flow_queues(
            omni_queue_file=tmp_path / "missing_omni.json",
            veo3_queue_file=tmp_path / "missing_veo3.json",
        )


def test_dispatch_dry_run(tmp_path):
    broll_dir = tmp_path / "broll"
    bot = GoogleFlowBot(broll_dir=broll_dir)

    omni_q = tmp_path / "omni.json"
    veo3_q = tmp_path / "veo3.json"

    omni_data = {
        "model_id": "gemini-omni-flash-1.2",
        "scenes": [
            {"scene_id": 1, "shot_name": "Panic Close-Up", "prompt": "Officer face", "target_duration_sec": 14.5},
            {"scene_id": 2, "shot_name": "Telephone Drift", "prompt": "Bakelite phone", "target_duration_sec": 15.0},
        ],
    }
    veo3_data = {
        "model_id": "veo-3.1-generate-4k",
        "scenes": [
            {"scene_id": 1, "shot_name": "Tactical Radar Macro", "prompt": "CRT screen", "target_duration_sec": 8.0},
        ],
    }

    omni_q.write_text(json.dumps(omni_data), encoding="utf-8")
    veo3_q.write_text(json.dumps(veo3_data), encoding="utf-8")

    res = bot.dispatch_flow_queues(omni_queue_file=omni_q, veo3_queue_file=veo3_q, dry_run=True)

    assert res["status"] == "completed"
    assert len(res["omni_flash_renders"]) == 2
    assert len(res["veo3_renders"]) == 1
    assert (broll_dir / "cena 1.mp4").exists()
    assert (broll_dir / "scene_2.mp4").exists()
    assert (broll_dir / "cena 1b.mp4").exists()


def test_fallback_procedural_plate(tmp_path):
    broll_dir = tmp_path / "broll"
    bot = GoogleFlowBot(broll_dir=broll_dir)
    target_video = broll_dir / "scene_99.mp4"

    res_path = bot.fallback_to_runninghub_or_procedural(scene_id=99, shot_type="shot_b", target_file=target_video)
    assert res_path.exists()
    assert res_path.suffix == ".jpg"
