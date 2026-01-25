"""
Centralized State Manager for Orbic Field Operator
Manages UI state, scan results, and device configuration.
"""
import json
import os

STATE_FILE = "/tmp/orbic_state.json"

def get_state():
    """Returns the current system state"""
    default_state = {
        "status": "idle", 
        "menu": "root",
        "ui": {
            "active_menu": "root",
            "metrics": {
                "packet_rate": [],
                "signal_strength": []
            }
        },
        "last_scan": []
    }
    
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                # Ensure defaults are present if missing in file
                _deep_update(default_state, state)
                return default_state
        except:
            pass
    return default_state

def _deep_update(base_dict, update_dict):
    """Recursively updates a dictionary"""
    for k, v in update_dict.items():
        if k in base_dict and isinstance(base_dict[k], dict) and isinstance(v, dict):
            _deep_update(base_dict[k], v)
        else:
            base_dict[k] = v

def update_state(new_state):
    """Updates the current system state using deep merge"""
    state = get_state()
    _deep_update(state, new_state)
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except:
        return False
