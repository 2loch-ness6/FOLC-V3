import pytest
import os
import json
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_config_data():
    return {
        "gemini": {
            "enabled": True,
            "model": "gemini-pro",
            "cli_path": "/usr/local/bin/gemini"
        },
        "claude": {
            "enabled": True,
            "model": "claude-3-sonnet",
            "cli_path": "/usr/local/bin/claude"
        },
        "preferred_provider": "gemini",
        "max_retries": 3,
        "timeout": 30
    }

@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run

@pytest.fixture
def mock_http_conn():
    with patch("http.client.HTTPConnection") as mock_conn:
        yield mock_conn

@pytest.fixture
def temp_config_file(tmp_path):
    config_dir = tmp_path / "etc" / "sos"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "ai_config.json"
    return str(config_file)
