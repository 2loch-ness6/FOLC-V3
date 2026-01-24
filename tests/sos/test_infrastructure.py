from tests.sos.base_test import SOSBaseTest
import json

class TestInfrastructure(SOSBaseTest):
    """Verify that the testing infrastructure itself works"""
    
    def test_orchestrator_initialization(self):
        """Verify orchestrator is initialized with mocked config"""
        assert self.orchestrator is not None
        assert "gemini" in self.orchestrator.providers
        assert "claude" in self.orchestrator.providers
    
    def test_mock_subprocess(self, mock_subprocess_run):
        """Verify subprocess mock helper"""
        self.set_mock_subprocess_response(mock_subprocess_run, stdout="mocked response")
        provider = self.orchestrator.providers["gemini"]
        result = provider.query("test prompt")
        
        assert result["status"] == "success"
        assert result["response"] == "mocked response"
        mock_subprocess_run.assert_called()

    def test_mock_api(self, mock_http_conn):
        """Verify API mock helper"""
        expected_response = {"status": "success", "data": "mock_data"}
        self.set_mock_api_response(mock_http_conn, expected_response)
        
        result = self.orchestrator.api_client.call_api("GET", "/test")
        assert result == expected_response
