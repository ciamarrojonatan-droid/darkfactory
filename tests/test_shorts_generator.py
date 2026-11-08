#!/usr/bin/env python3
"""Unit tests for DarkFactory Vertical Shorts Generator."""
import sys
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

from shorts_generator import build_shorts_filter_chain, generate_vertical_short, get_ffmpeg_binary


def test_get_ffmpeg_binary():
    bin_path = get_ffmpeg_binary()
    assert bin_path is not None
    assert "ffmpeg" in bin_path.lower()


def test_build_shorts_filter_chain_without_subtitles():
    fc = build_shorts_filter_chain(None)
    assert "scale=1080:1920" in fc
    assert "boxblur" in fc
    assert "overlay=" in fc
    assert "[combined]copy[outv]" in fc


def test_build_shorts_filter_chain_with_subtitles(tmp_path):
    dummy_srt = tmp_path / "test.srt"
    dummy_srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nHello\n", encoding="utf-8")
    fc = build_shorts_filter_chain(dummy_srt)
    assert "scale=1080:1920" in fc
    assert "subtitles=" in fc
    assert "PrimaryColour=&H0000FFFF" in fc
    assert "MarginV=380" in fc


def test_generate_vertical_short_missing_input(tmp_path):
    missing_file = tmp_path / "non_existent.mp4"
    output_short = tmp_path / "out_short.mp4"
    result = generate_vertical_short(missing_file, output_short)
    assert result is False


@patch("subprocess.run")
def test_generate_vertical_short_mocked(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0)

    in_video = tmp_path / "master.mp4"
    in_video.write_bytes(b"dummy_video_bytes")
    out_short = tmp_path / "short_result.mp4"

    # Mock atomic file creation so replace works
    def side_effect(cmd, **kwargs):
        # The last element in cmd is the temp output file
        temp_out = Path(cmd[-1])
        temp_out.write_bytes(b"rendered_short_bytes")
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect

    res = generate_vertical_short(
        video_input=in_video,
        output_short=out_short,
        duration_sec=45.0,
        start_time=5.0,
        ffmpeg_bin="ffmpeg",
    )

    assert res is True
    assert out_short.exists()
    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert "-ss" in cmd
    assert "5.00" in cmd
    assert "-t" in cmd
    assert "45.00" in cmd
    assert "libx264" in cmd
