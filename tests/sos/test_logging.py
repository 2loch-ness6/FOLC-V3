from tests.sos.base_test import SOSBaseTest
from unittest.mock import patch, MagicMock
import json

class TestSOSLogging(SOSBaseTest):
    """Test structured logging in SOS AI Orchestrator"""
    
    def test_logging_api_call(self, mock_http_conn):
        """Verify that API calls are logged with structure"""
        self.set_mock_api_response(mock_http_conn, {"status": "success"})
        
        with patch("src.sos.ai.ai_orchestrator.logger") as mock_logger:
            self.orchestrator.api_client.call_api("GET", "/api/test")
            
            # Verify logger.info was called
            # We expect a log message containing the endpoint
            found_log = False
            for call in mock_logger.info.call_args_list:
                if "/api/test" in call[0][0]:
                    found_log = True
                    break
            assert found_log, "API call was not logged"

    def test_logging_ai_query(self, mock_subprocess_run):
        """Verify that AI queries are logged"""
        self.set_mock_subprocess_response(mock_subprocess_run, stdout="AI Response")
        
        with patch("src.sos.ai.ai_orchestrator.logger") as mock_logger:
            self.orchestrator.process_natural_language("Hello")
            
            found_log = False
            for call in mock_logger.info.call_args_list:
                if "Processing query: Hello" in call[0][0]:
                    found_log = True
                    break
            assert found_log, "AI query start was not logged"
