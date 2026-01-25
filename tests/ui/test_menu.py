import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Mock hardware before imports
sys.modules["evdev"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["PIL.ImageDraw"] = MagicMock()
sys.modules["PIL.ImageFont"] = MagicMock()

# Import UI and State Manager
from src.ui.folc_ui import UI
from src.core import state_manager

class TestMenuState:
    @pytest.fixture(autouse=True)
    def setup_state(self):
        # Reset state for each test
        state_manager.STATE_FILE = "/tmp/orbic_test_state.json"
        if os.path.exists(state_manager.STATE_FILE):
            os.remove(state_manager.STATE_FILE)
        # Mock draw_fb to prevent actual hardware writes
        with patch("src.ui.folc_ui.draw_fb"):
            self.ui = UI()
            yield

    def test_menu_to_autoiot_state(self):
        # 1. Verify initial state
        assert self.ui.state == "MENU"
        
        # 2. Navigate to AutoIOT (Last item in Root)
        while self.ui.menu_items[self.ui.current_idx] != "AutoIOT":
            self.ui.next()
        
        # 3. Select AutoIOT
        self.ui.select()
        
        # 4. Verify logic transition
        assert self.ui.state == "AUTO_IOT"
        assert self.ui.menu_items == self.ui.autoiot_items
        
        # 5. Verify persistent state if we implemented it (Bonus check)
        # Note: We haven't explicitly added state_manager calls to folc_ui yet,
        # but let's check if the UI class state reflects the change.
        assert "ANALYSIS" in self.ui.menu_items

    def test_back_button_logic(self):
        self.ui.state = "AUTO_IOT"
        self.ui.menu_items = self.ui.autoiot_items
        
        self.ui.back()
        
        assert self.ui.state == "MENU"
        assert self.ui.menu_items == self.ui.root_items

if __name__ == "__main__":
    # Custom test reporter
    import pytest
    class MyPlugin:
        def pytest_sessionfinish(self, exitstatus):
            with open("/root/test_summary.txt", "w") as f:
                f.write(f"EXIT_STATUS: {exitstatus}")

    print("--- RUNNING TESTS ---")
    ret = pytest.main([__file__], plugins=[MyPlugin()])
    print(f"--- FINISHED: {ret} ---")
