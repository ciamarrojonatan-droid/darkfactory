"""Tests for RunningHub execution button enforcement:
Enforces that Lite/Plus (middle button) is mandatory across all workflows
and Standard is strictly prohibited.
"""
from unittest.mock import MagicMock, patch
import pytest

from src.factory.runninghub_bot import (
    CONTA_COSYVOICE_CONFIG,
    CONTA_MINIMAX_MUSIC_CONFIG,
    CONTA_MINIMAX_H3_CONFIG,
    get_account_config,
    click_runninghub_execute,
)


class TestRunningHubExecutionModeDefaults:
    """Validate that all account configurations default to 'lite_plus'."""

    def test_conta_cosyvoice_execute_mode_is_lite_plus(self):
        assert CONTA_COSYVOICE_CONFIG.get("execute_mode") == "lite_plus"

    def test_conta_minimax_music_execute_mode_is_lite_plus(self):
        assert CONTA_MINIMAX_MUSIC_CONFIG.get("execute_mode") == "lite_plus"

    def test_conta_minimax_h3_execute_mode_is_lite_plus(self):
        assert CONTA_MINIMAX_H3_CONFIG.get("execute_mode") == "lite_plus"

    @pytest.mark.parametrize("account_id", [
        4, 5, 7,
        "cosyvoice", "narration",
        "minimax_music", "music",
        "minimax_h3", "h3", "h3_cinematic", "minimax_video"
    ])
    def test_get_account_config_always_lite_plus(self, account_id):
        cfg = get_account_config(account_id)
        assert cfg.get("execute_mode") == "lite_plus"


class TestClickRunningHubExecuteGuards:
    """Verify that click_runninghub_execute strictly guards against Standard and targets Lite/Plus."""

    def test_standard_mode_is_intercepted_and_coerced_to_lite_plus(self):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = {"success": True, "method": "segmented_order_lite_plus", "x": 100, "y": 50}

        # Passing "standard" directly should be redirected to "lite_plus"
        res = click_runninghub_execute(mock_page, mode="standard")

        assert res is True
        mock_page.evaluate.assert_called_once()
        # Verify the JS evaluate received "lite_plus" and not "standard"
        called_args = mock_page.evaluate.call_args[0]
        assert called_args[1] == "lite_plus"

    def test_default_mode_is_lite_plus(self):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = {"success": True, "method": "closest_button", "x": 100, "y": 50}

        res = click_runninghub_execute(mock_page)

        assert res is True
        mock_page.evaluate.assert_called_once()
        called_args = mock_page.evaluate.call_args[0]
        assert called_args[1] == "lite_plus"

    def test_fallback_middle_button_selection(self):
        """When DOM evaluate fails, fallback must click middle button (index 1) and never index 0."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = {"success": False}

        # Mock page.locator for plus_selectors to fail, but exec_btns to return 2 buttons
        def mock_locator(selector):
            loc = MagicMock()
            if "has-text('Executar')" in selector:
                loc.count.return_value = 2
                middle_btn = MagicMock()
                middle_btn.is_visible.return_value = True
                first_btn = MagicMock()
                first_btn.is_visible.return_value = True

                def nth_mock(idx):
                    if idx == 1:
                        return middle_btn
                    return first_btn

                loc.nth = nth_mock
            else:
                loc.count.return_value = 0
            return loc

        mock_page.locator.side_effect = mock_locator

        res = click_runninghub_execute(mock_page, mode="lite_plus")
        assert res is True


class TestExecutionModeStandardRedirect:
    """Verify runtime redirection of prohibited 'standard' mode to 'lite_plus'."""

    def test_click_execute_redirects_standard_to_lite_plus(self):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = {"success": True, "method": "closest_button", "x": 100, "y": 50}

        res = click_runninghub_execute(mock_page, mode="standard")

        assert res is True
        called_args = mock_page.evaluate.call_args[0]
        assert called_args[1] == "lite_plus"

    def test_run_factory_bot_blocks_standard_mode(self, caplog, tmp_path):
        from src.factory.runninghub_bot import resolve_execution_mode, run_factory_bot

        assert resolve_execution_mode("standard", {"execute_mode": "standard"}) == "lite_plus"
        assert resolve_execution_mode(None, {"execute_mode": "lite_plus"}) == "lite_plus"

        with (
            patch("src.factory.runninghub_bot.ensure_chrome_cdp_desktop", side_effect=RuntimeError("stop-after-mode-guard")),
            caplog.at_level("WARNING"),
        ):
            with pytest.raises(RuntimeError, match="stop-after-mode-guard"):
                run_factory_bot(
                    account=4,
                    destination_dir=tmp_path,
                    session_dir=tmp_path / "sess",
                    execute_mode="standard",
                )

        assert "Redirecionando para 'lite_plus'" in caplog.text
