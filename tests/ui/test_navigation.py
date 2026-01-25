import pytest
import time
from unittest.mock import MagicMock
from src.core.input_manager import InputManager, InputEvent

class MockEvent:
    def __init__(self, type, code, value):
        self.type = type
        self.code = code
        self.value = value

class TestNavigationFilter:
    @pytest.fixture
    def manager(self):
        callback = MagicMock()
        mgr = InputManager(callback=callback)
        # Mock evdev constants
        import evdev
        mgr.EV_KEY = evdev.ecodes.EV_KEY
        return mgr

    def test_basic_select(self, manager):
        # Press DOWN
        manager._handle_key(MockEvent(1, 116, 1), True, False)
        # Release UP after 0.2s
        time.sleep(0.2)
        manager._handle_key(MockEvent(1, 116, 0), True, False)
        
        manager.callback.assert_called_once()
        assert manager.callback.call_args[0][0].action == "SELECT"

    def test_long_press_context(self, manager):
        # Press DOWN
        manager._handle_key(MockEvent(1, 116, 1), True, False)
        # Wait for long press threshold
        manager.power_down_time = time.time() - 1.0 
        # Release UP
        manager._handle_key(MockEvent(1, 116, 0), True, False)
        
        manager.callback.assert_called_once()
        assert manager.callback.call_args[0][0].action == "CONTEXT"

    def test_debounce_double_click(self, manager):
        # First click
        manager._handle_key(MockEvent(1, 116, 1), True, False)
        time.sleep(0.1) # Longer than glitch filter
        manager._handle_key(MockEvent(1, 116, 0), True, False)
        
        # Immediate second click (within debounce window)
        manager._handle_key(MockEvent(1, 116, 1), True, False)
        time.sleep(0.1)
        manager._handle_key(MockEvent(1, 116, 0), True, False)
        
        # Should only emit once
        assert manager.callback.call_count == 1

    def test_glitch_filter(self, manager):
        # Extremely short press (< 0.05s)
        manager._handle_key(MockEvent(1, 116, 1), True, False)
        manager.power_down_time = time.time() - 0.01
        manager._handle_key(MockEvent(1, 116, 0), True, False)
        
        # Should NOT emit
        manager.callback.assert_not_called()
