from tests.sos.base_test import SOSBaseTest
import json
import pytest
from unittest.mock import MagicMock

class TestAIOrchestratorAPI(SOSBaseTest):
    """Test standardized API interfacing in AIOrchestrator"""
    
    def test_standardized_api_call_format(self, mock_http_conn):
        """Verify that API calls follow the new standardized format"""
        expected_response = {"status": "success", "result": "ok"}
        self.set_mock_api_response(mock_http_conn, expected_response)
        
        # We want the orchestrator to have a dedicated method for standardized hardware calls
        action_spec = {
            "action": "api_call",
            "api_endpoint": "/api/wifi/status",
            "method": "GET"
        }
        
        result = self.orchestrator.execute_ai_action(action_spec)
        
        assert result["status"] == "success"
        # Check that the call was made to the gateway
        mock_http_conn.assert_called()
    
    def test_api_error_handling_standardized(self, mock_http_conn):
        """Verify standardized error response when API call fails"""
        # Simulate a 500 error from gateway
        self.set_mock_api_response(mock_http_conn, {"message": "Internal Server Error"}, status=500)
        
        action_spec = {
            "action": "api_call",
            "api_endpoint": "/api/broken",
            "method": "GET"
        }
        
        result = self.orchestrator.execute_ai_action(action_spec)
        
        # The result should be standardized as an error even if the gateway response is messy
        assert result["status"] == "error"
        assert "message" in result

    def test_api_non_json_response(self, mock_http_conn):
        """Verify handling of non-JSON responses from API gateway"""
        # Simulate a 200 OK but with plain text response
        mock_response = MagicMock()
        mock_response.read.return_value = b"Just some plain text"
        mock_response.status = 200
        
        instance = mock_http_conn.return_value
        instance.getresponse.return_value = mock_response
        
        result = self.orchestrator.api_client.call_api("GET", "/text")
        
        assert result["status"] == "success"
        assert result["message"] == "Just some plain text"

class TestAIOrchestratorRetries(SOSBaseTest):
    """Test retry logic in AIOrchestrator"""
    
    def test_provider_retry_on_failure(self, mock_subprocess_run):
        """Verify that provider retries query on failure"""
        # Simulate 2 failures followed by a success
        mock_subprocess_run.side_effect = [
            MagicMock(stdout="", stderr="Busy", returncode=1),
            MagicMock(stdout="", stderr="Timeout", returncode=1),
            MagicMock(stdout="Success", stderr="", returncode=0)
        ]
        
        provider = self.orchestrator.providers["gemini"]
        # Note: We need to implement retry in the provider or orchestrator
        # For this test, let's assume the provider has a query_with_retry method or the query method itself handles it
        result = provider.query("test prompt")
        
        assert result["status"] == "success"
        assert mock_subprocess_run.call_count == 3
    
    def test_provider_exhaust_retries(self, mock_subprocess_run):
        """Verify that provider eventually fails after max retries"""
        # Simulate constant failures
        mock_subprocess_run.return_value = MagicMock(stdout="", stderr="Persistent Error", returncode=1)
        
        provider = self.orchestrator.providers["gemini"]
        result = provider.query("test prompt")
        
        assert result["status"] == "error"
        # max_retries is 3 in mock_config_data
        assert mock_subprocess_run.call_count == 3
