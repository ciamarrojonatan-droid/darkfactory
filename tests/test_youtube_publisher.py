#!/usr/bin/env python3
"""Unit tests for DarkFactory YouTube Data API v3 Publisher."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from youtube_publisher import YouTubePublisher


def test_publisher_initialization(tmp_path):
    secrets = tmp_path / "secrets.json"
    token = tmp_path / "token.json"
    history = tmp_path / "history.json"

    pub = YouTubePublisher(credentials_file=secrets, token_file=token, history_file=history)
    assert pub.credentials_file == secrets
    assert pub.token_file == token
    assert pub.history_file == history


def test_upload_missing_video(tmp_path):
    pub = YouTubePublisher(history_file=tmp_path / "history.json")
    non_existent = tmp_path / "ghost.mp4"
    with pytest.raises(FileNotFoundError):
        pub.upload_video(video_path=non_existent, title="Ghost Video", description="Desc")


def test_upload_dry_run(tmp_path):
    history_file = tmp_path / "history.json"
    pub = YouTubePublisher(history_file=history_file)
    dummy_video = tmp_path / "sample_pilot.mp4"
    dummy_video.write_bytes(b"dummy_mp4_bytes")

    record = pub.upload_video(
        video_path=dummy_video,
        title="1983 Soviet Glitch",
        description="A Cold War documentary",
        privacy_status="unlisted",
        dry_run=True,
    )

    assert record["is_dry_run"] is True
    assert record["privacy_status"] == "unlisted"
    assert "https://youtu.be/" in record["video_url"]
    assert history_file.exists()

    with open(history_file, "r", encoding="utf-8") as f:
        hist_data = json.load(f)
    assert record["video_id"] in hist_data


def test_update_video_privacy_dry_run():
    pub = YouTubePublisher()
    assert pub.update_video_privacy("simulated_123", "public", dry_run=True) is True


def test_add_pinned_comment_dry_run():
    pub = YouTubePublisher()
    assert pub.add_pinned_comment("simulated_123", "Watch full video here: https://youtu.be/xxx", dry_run=True) is True


@patch.object(YouTubePublisher, "get_authenticated_service")
@patch("googleapiclient.http.MediaFileUpload")
def test_upload_video_mocked_service(mock_media, mock_get_service, tmp_path):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    # Mock the chunked upload response
    mock_request = MagicMock()
    mock_status = MagicMock()
    mock_status.progress.return_value = 1.0
    mock_response = {"id": "real_yt_abc123"}
    mock_request.next_chunk.return_value = (mock_status, mock_response)
    mock_service.videos().insert.return_value = mock_request

    dummy_video = tmp_path / "real_video.mp4"
    dummy_video.write_bytes(b"video_bytes")
    history_file = tmp_path / "mock_history.json"

    pub = YouTubePublisher(history_file=history_file)
    record = pub.upload_video(
        video_path=dummy_video,
        title="Oppenheimer vs Petrov",
        description="Detailed documentary.",
        privacy_status="unlisted",
        dry_run=False,
    )

    assert record["video_id"] == "real_yt_abc123"
    assert record["video_url"] == "https://youtu.be/real_yt_abc123"
    assert record["privacy_status"] == "unlisted"
    assert mock_service.videos().insert.called
