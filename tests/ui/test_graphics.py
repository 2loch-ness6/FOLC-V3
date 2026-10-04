import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock hardware before imports
sys.modules["evdev"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["PIL.ImageDraw"] = MagicMock()
sys.modules["PIL.ImageFont"] = MagicMock()

from src.ui.folc_ui import UI

class TestGraphicsEngine:
    @pytest.fixture
    def ui(self):
        with patch("src.ui.folc_ui.draw_fb"):
            return UI()

    def test_sparkline_buffer_limit(self, ui):
        # We want to maintain a 60s history
        for i in range(100):
            ui.add_metric_point("packet_rate", i)
        
        assert len(ui.metrics["packet_rate"]) == 60

    def test_sparkline_rendering_coords(self, ui):
        # Verify that sparkline logic correctly scales data to screen height (10px per graph)
        ui.metrics["packet_rate"] = [0, 50, 100]
        # Signature: _generate_sparkline_coords(metric_name, width, height, x_offset, y_offset)
        coords = ui._generate_sparkline_coords("packet_rate", 100, 10, 0, 0)
        
        # Max value (100) should be at Y=0 (relative to graph base)
        # Min value (0) should be at Y=10
        assert coords[0][1] == 10
        assert coords[2][1] == 0

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))