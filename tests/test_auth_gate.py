"""Unit tests for DarkFactory Pre-Flight Auth & Session Gate."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.auth_gate import (
    check_google_flow_session,
    check_runninghub_session,
    enforce_production_auth_gate,
)


def test_auth_gate_dry_run_always_passes():
    """Dry-run mode should pass without requiring real browser sessions."""
    assert enforce_production_auth_gate(dry_run=True) is True


def test_auth_gate_non_interactive_unauthenticated_raises(tmp_path):
    """When sessions are unauthenticated and non-interactive is requested, must raise PermissionError."""
    with patch("src.auth_gate.check_google_flow_session", return_value=False), \
         patch("src.auth_gate.check_runninghub_session", return_value=False):
        with pytest.raises(PermissionError) as exc_info:
            enforce_production_auth_gate(interactive=False, dry_run=False)
        assert "Production Auth Gate Check Failed" in str(exc_info.value)


def test_auth_gate_passes_when_both_authenticated():
    """When both Google Flow and RunningHub are authenticated, gate returns True."""
    with patch("src.auth_gate.check_google_flow_session", return_value=True), \
         patch("src.auth_gate.check_runninghub_session", return_value=True):
        assert enforce_production_auth_gate(interactive=False, dry_run=False) is True


def test_check_google_flow_session_missing_profile(tmp_path):
    """Missing session files should return False immediately without launching browser."""
    missing_dir = tmp_path / "nonexistent_flow"
    assert check_google_flow_session(session_dir=missing_dir, headless=True) is False


def test_check_runninghub_session_missing_profile(tmp_path):
    """Missing RunningHub session files should return False immediately without launching browser."""
    missing_dir = tmp_path / "nonexistent_runninghub"
    assert check_runninghub_session(session_dir=missing_dir, headless=True) is False


def test_check_runninghub_session_valid_storage_state(tmp_path):
    """Valid storage_state.json with RunningHub cookies returns True."""
    session_dir = tmp_path / "runninghub_session"
    session_dir.mkdir(parents=True, exist_ok=True)
    storage_state_file = session_dir / "storage_state.json"
    valid_state = {
        "cookies": [
            {
                "name": "token",
                "value": "jwt_fake_token_value",
                "domain": "runninghub.ai",
                "path": "/",
                "expires": 9999999999,
            }
        ]
    }
    storage_state_file.write_text(json.dumps(valid_state), encoding="utf-8")
    assert check_runninghub_session(session_dir=session_dir, headless=True) is True
