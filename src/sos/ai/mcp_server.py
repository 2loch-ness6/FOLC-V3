from mcp.server.fastmcp import FastMCP
import subprocess
import json
import logging
from typing import Dict, Any, Optional
from src.core import state_manager

# Initialize FastMCP server
mcp = FastMCP("OrbicFieldOperator")

logger = logging.getLogger("mcp_server")

@mcp.tool()
def execute_command(command: str) -> str:
    """
    Executes a shell command on the Orbic Speed device.
    Useful for running security tools like nmap, scapy, iw, etc.
    """
    logger.info(f"Executing command: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout if result.stdout else "Command executed successfully (no output)."
        else:
            return f"Error ({result.returncode}): {result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

@mcp.tool()
def read_ui_state() -> str:
    """
    Reads the current UI state and system metrics (signal strength, packet rates).
    Returns a JSON string of the state.
    """
    return json.dumps(state_manager.get_state(), indent=2)

@mcp.tool()
def write_ui_state(state_json: str) -> bool:
    """
    Updates the UI state. Can be used to change menus, update graphs, or show alerts.
    Expects a JSON string of the state updates.
    """
    try:
        new_state = json.loads(state_json)
        return state_manager.update_state(new_state)
    except Exception as e:
        logger.error(f"Failed to write UI state: {e}")
        return False

@mcp.tool()
def configure_network(interface: str, mode: str) -> str:
    """
    Configures network interfaces (e.g., setting wlan0 to monitor mode).
    """
    if mode == "monitor":
        cmd = f"ifconfig {interface} down && iw dev {interface} set type monitor && ifconfig {interface} up"
    else:
        cmd = f"ifconfig {interface} down && iw dev {interface} set type managed && ifconfig {interface} up"
    
    return execute_command(cmd)

if __name__ == "__main__":
    mcp.run()