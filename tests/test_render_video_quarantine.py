"""Tests for Video Rendering quarantine and procedural fallback rejection."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from src.render_pilot_video import render_single_clip


def test_render_single_clip_missing_footage_raises_runtime_error(tmp_path):
    """When video footage is missing and allow_procedural_fallback is False, must raise RuntimeError and quarantine."""
    output_mp4 = tmp_path / "output.mp4"
    nonexistent_clips = [tmp_path / "missing1.mp4", tmp_path / "missing2.mp4"]
    nonexistent_imgs = [tmp_path / "missing1.jpg"]

    with patch("src.render_pilot_video.DATA_DIR", tmp_path):
        with pytest.raises(RuntimeError) as exc_info:
            render_single_clip(
                ffmpeg_bin="ffmpeg",
                clip_candidates=nonexistent_clips,
                fallback_img_candidates=nonexistent_imgs,
                scene_id=99,
                duration=5.0,
                output_mp4=output_mp4,
                allow_procedural_fallback=False,
            )
        assert "CRITICAL: Scene 99 has no real AI video footage" in str(exc_info.value)
        quarantine_report = tmp_path / "quarantine" / "scene_99_missing_footage" / "quarantine_report.json"
        assert quarantine_report.exists()
        data = json.loads(quarantine_report.read_text(encoding="utf-8"))
        assert data["scene_id"] == 99
        assert "Procedural fallback is permanently disabled" in data["error"]


def test_render_single_clip_allows_procedural_when_flagged(tmp_path):
    """When allow_procedural_fallback=True (test mode), procedural broll is permitted."""
    output_mp4 = tmp_path / "output.mp4"
    nonexistent_clips = [tmp_path / "missing1.mp4"]
    nonexistent_imgs = [tmp_path / "missing1.jpg"]

    with patch("src.render_pilot_video.BROLL_DIR", tmp_path), \
         patch("src.render_pilot_video.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        ok = render_single_clip(
            ffmpeg_bin="ffmpeg",
            clip_candidates=nonexistent_clips,
            fallback_img_candidates=nonexistent_imgs,
            scene_id=42,
            duration=3.0,
            output_mp4=output_mp4,
            allow_procedural_fallback=True,
        )
        assert ok is True
        assert (tmp_path / "scene_42.jpg").exists()
