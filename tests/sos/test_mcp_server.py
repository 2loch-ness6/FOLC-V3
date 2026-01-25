import pytest
import json
from unittest.mock import MagicMock, patch
from src.sos.ai.mcp_server import execute_command, read_ui_state, write_ui_state, configure_network

class TestMCPServerTools:
    def test_execute_command_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="test output",
                stderr="",
                returncode=0
            )
            result = execute_command("ls -l")
            assert "test output" in result
            mock_run.assert_called_once()

    def test_execute_command_failure(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",
                stderr="error message",
                returncode=1
            )
            result = execute_command("invalid_cmd")
            assert "error message" in result

    @patch("src.core.state_manager.get_state")
    def test_read_ui_state(self, mock_get_state):
        expected_state = {"menu": "root", "selection": 0}
        mock_get_state.return_value = expected_state
        result_json = read_ui_state()
        assert json.loads(result_json) == expected_state

    @patch("src.core.state_manager.update_state")
    def test_write_ui_state(self, mock_update_state):
        new_state = {"menu": "auto_iot"}
        mock_update_state.return_value = True
        result = write_ui_state(json.dumps(new_state))
        assert result is True
        mock_update_state.assert_called_with(new_state)

    def test_configure_network_monitor(self):
        with patch("src.sos.ai.mcp_server.execute_command") as mock_exec:
            mock_exec.return_value = "success"
            result = configure_network("wlan0", "monitor")
            assert result == "success"
            mock_exec.assert_called_with("ifconfig wlan0 down && iw dev wlan0 set type monitor && ifconfig wlan0 up")