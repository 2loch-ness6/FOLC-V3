import pytest
from unittest.mock import MagicMock, patch
from src.sos.ai.nexus_orchestrator import NexusOrchestrator

class TestNexusOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel") as mock_model:
                return NexusOrchestrator(api_key="mock_key")

    def test_initialization(self, orchestrator):
        assert orchestrator.api_key == "mock_key"
        assert "Nexus Field Operator" in orchestrator.system_instruction

    @pytest.mark.asyncio
    async def test_run_turn(self, orchestrator):
        # Mock chat response
        mock_response = MagicMock()
        mock_response.text = "Analysis complete."
        orchestrator.chat.send_message = MagicMock(returncode=mock_response)
        orchestrator.chat.send_message.return_value = mock_response
        
        with patch("src.sos.ai.nexus_orchestrator.read_ui_state") as mock_read:
            mock_read.return_value = '{"status": "idle"}'
            result = await orchestrator.run_turn("Scan wifi")
            assert "Analysis complete" in result

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__]))
