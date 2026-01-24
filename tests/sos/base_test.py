import pytest
import json
from unittest.mock import MagicMock, patch
from src.sos.ai.ai_orchestrator import AIOrchestrator, AIConfig

class SOSBaseTest:
    """Base class for SOS AI Orchestrator tests"""
    
    @pytest.fixture(autouse=True)
    def setup_orchestrator(self, temp_config_file, mock_config_data):
        self.config_file = temp_config_file
        with open(self.config_file, 'w') as f:
            json.dump(mock_config_data, f)
        
        # Patch the global CONFIG_FILE in the module
        with patch("src.sos.ai.ai_orchestrator.CONFIG_FILE", self.config_file):
            # Patch logging to avoid polluting test output
            with patch("src.sos.ai.ai_orchestrator.logger"):
                self.orchestrator = AIOrchestrator()
    
    def set_mock_subprocess_response(self, mock_run, stdout="", stderr="", returncode=0):
        """Helper to set subprocess mock response"""
        mock_run.return_value = MagicMock(
            stdout=stdout,
            stderr=stderr,
            returncode=returncode
        )

    def set_mock_api_response(self, mock_conn, response_data, status=200):
        """Helper to set API gateway mock response"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(response_data).encode('utf-8')
        mock_response.status = status
        
        instance = mock_conn.return_value
        instance.getresponse.return_value = mock_response
