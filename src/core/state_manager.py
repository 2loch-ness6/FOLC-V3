"""
Centralized State Manager for Orbic Field Operator
Manages UI state, scan results, and device configuration.
"""
import json
import os

STATE_FILE = "/tmp/orbic_state.json"

def get_state():
    """Returns the current system state"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"status": "idle", "menu": "root"}

def update_state(new_state):
    """Updates the current system state"""
    state = get_state()
    state.update(new_state)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        return True
    except:
        return False
