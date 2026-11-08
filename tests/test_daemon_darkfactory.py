#!/usr/bin/env python3
"""Unit tests for DarkFactory 24/7 Autonomous Supervisor Daemon."""
import json
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

from daemon_darkfactory import DarkFactoryDaemon


def test_daemon_initialization_and_state(tmp_path):
    state_file = tmp_path / "daemon_state.json"
    daemon = DarkFactoryDaemon(state_file=state_file, dry_run=True)

    state = daemon.load_state()
    assert state["status"] == "idle"
    assert state["total_productions"] == 0

    state["status"] = "testing"
    daemon.save_state(state)

    assert state_file.exists()
    reloaded = daemon.load_state()
    assert reloaded["status"] == "testing"
    assert reloaded["last_heartbeat"] is not None


@patch("subprocess.run")
def test_execute_pipeline_cycle_mocked(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0)

    state_file = tmp_path / "daemon_state.json"
    daemon = DarkFactoryDaemon(state_file=state_file, dry_run=True)

    success = daemon.execute_pipeline_cycle("1983 Soviet nuclear false alarm incident")

    assert success is True
    assert mock_run.call_count >= 5  # director, audio, flow, video, shorts, youtube

    state = daemon.load_state()
    assert state["status"] == "awaiting_approval"
    assert state["total_productions"] == 1
    assert len(state["completed_episodes"]) == 1
    assert len(state["pending_approval_queue"]) == 1
    assert state["pending_approval_queue"][0]["approval_status"] == "pending_one_click"
    assert state["current_topic_index"] == 1
