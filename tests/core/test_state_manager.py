import pytest
import json
import os
from src.core import state_manager

class TestStateManager:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Use a test-specific state file
        state_manager.STATE_FILE = "/tmp/orbic_test_state.json"
        if os.path.exists(state_manager.STATE_FILE):
            os.remove(state_manager.STATE_FILE)
        yield
        if os.path.exists(state_manager.STATE_FILE):
            os.remove(state_manager.STATE_FILE)

    def test_default_state(self):
        state = state_manager.get_state()
        assert state["status"] == "idle"
        assert state["menu"] == "root"

    def test_update_simple(self):
        state_manager.update_state({"status": "scanning"})
        state = state_manager.get_state()
        assert state["status"] == "scanning"
        assert state["menu"] == "root"

    def test_update_nested(self):
        # We want to support nested updates for complex state
        initial_state = {
            "ui": {
                "active_menu": "root",
                "metrics": {"signal": -50}
            }
        }
        state_manager.update_state(initial_state)
        
        # Partial update to nested dict
        state_manager.update_state({"ui": {"active_menu": "auto_iot"}})
        
        state = state_manager.get_state()
        assert state["ui"]["active_menu"] == "auto_iot"
        # Check if deep merge worked (metrics should still be there)
        assert state["ui"]["metrics"]["signal"] == -50

    def test_scan_results_persistence(self):
        results = [
            {"ssid": "Network1", "signal": -40},
            {"ssid": "Network2", "signal": -60}
        ]
        state_manager.update_state({"last_scan": results})
        state = state_manager.get_state()
        assert len(state["last_scan"]) == 2
        assert state["last_scan"][0]["ssid"] == "Network1"
