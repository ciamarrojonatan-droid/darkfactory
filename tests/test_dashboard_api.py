"""Automated Test Suite for the DarkFactory Cinema Dashboard API."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

DARKFACTORY_ROOT = Path(__file__).resolve().parent.parent
if str(DARKFACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(DARKFACTORY_ROOT))

from src.dashboard.app import app
from src.dashboard import readers, runner, schemas


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_index_spa_serves_html(client):
    """Verifies that the SPA root endpoint serves HTML with DarkFactory Cinema branding."""
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "DarkFactory" in res.text
    assert "Cinema" in res.text
    assert "Sound Lab" in res.text


def test_status_endpoint(client):
    """Verifies that /api/status returns valid KPIs and telemetry."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "active_tasks" in data
    assert "stockcont_dashboard_url" in data
    k = data["kpis"]
    assert "total_productions" in k
    assert "completed_episodes" in k
    assert "pending_approvals" in k
    assert "green_dollar_rate" in k
    assert "google_flow_quota" in k


def test_screenplays_endpoint(client):
    """Verifies that /api/screenplays returns structured script dossiers."""
    res = client.get("/api/screenplays")
    assert res.status_code == 200
    scripts = res.json()
    assert isinstance(scripts, list)
    if len(scripts) > 0:
        first = scripts[0]
        assert "title" in first
        assert "logline" in first
        assert "timelines" in first


def test_visual_queues_endpoint(client):
    """Verifies that /api/visual-queues aggregates Veo 3.1 and Omni Flash prompts."""
    res = client.get("/api/visual-queues")
    assert res.status_code == 200
    data = res.json()
    assert "veo3_4k" in data
    assert "omni_flash" in data
    assert "runninghub_foley" in data


def test_audio_library_endpoint(client):
    """Verifies that /api/audio-library groups 4 audio stems."""
    res = client.get("/api/audio-library")
    assert res.status_code == 200
    data = res.json()
    assert "voice" in data
    assert "ost" in data
    assert "foley" in data
    assert "master" in data


def test_approval_queue_and_actions(client):
    """Verifies that /api/approval-queue and /api/approval-action handle publication gates."""
    res = client.get("/api/approval-queue")
    assert res.status_code == 200
    queue = res.json()
    assert isinstance(queue, list)

    # Test approval action (publish_unlisted)
    action_payload = {
        "video_id": "test_video_pilot_01",
        "action": "publish_unlisted",
        "selected_thumbnail": "variant_a"
    }
    action_res = client.post("/api/approval-action", json=action_payload)
    assert action_res.status_code == 200
    assert action_res.json()["status"] == "success"
    assert action_res.json()["action"] == "published_unlisted"

    # Test rejection to quarantine
    reject_payload = {
        "video_id": "test_video_glitch_02",
        "action": "reject_quarantine",
        "quarantine_notes": "Audio clipped at 03:15, Veo artifacting."
    }
    reject_res = client.post("/api/approval-action", json=reject_payload)
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "quarantined"


def test_download_package_endpoint(client):
    """Verifies that /api/download-package produces a valid zip archive stream."""
    res = client.get("/api/download-package/sample_pilot")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert len(res.content) > 0


def test_quarantine_endpoint(client):
    """Verifies that /api/quarantine lists quarantine diagnostics."""
    res = client.get("/api/quarantine")
    assert res.status_code == 200
    reports = res.json()
    assert isinstance(reports, list)


def test_daemon_control_validation(client):
    """Verifies that /api/daemon-control rejects invalid actions."""
    res = client.post("/api/daemon-control", json={"action": "invalid_action"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"
