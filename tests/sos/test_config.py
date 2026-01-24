from tests.sos.base_test import SOSBaseTest
from src.sos.ai.ai_orchestrator import AIConfig
import os
import json
from unittest.mock import patch

class TestAIConfig(SOSBaseTest):
    """Test configuration management in SOS"""
    
    def test_config_load_default_when_missing(self, tmp_path):
        """Verify that default config is used when file is missing"""
        missing_file = str(tmp_path / "nonexistent.json")
        config_mgr = AIConfig(missing_file)
        
        assert config_mgr.config["gemini"]["enabled"] is True
        assert config_mgr.config["preferred_provider"] == "gemini"
    
    def test_config_load_corrupt_file(self, tmp_path):
        """Verify that defaults are used and error is handled when file is corrupt"""
        corrupt_file = tmp_path / "corrupt.json"
        with open(corrupt_file, 'w') as f:
            f.write("this is not json {")
        
        with patch("src.sos.ai.ai_orchestrator.logger") as mock_logger:
            config_mgr = AIConfig(str(corrupt_file))
            # Should have logged an error
            mock_logger.error.assert_called()
            # Should still have default config
            assert config_mgr.config["preferred_provider"] == "gemini"

    def test_config_save_creates_directory(self, tmp_path):
        """Verify that save_config creates the config directory if it doesn't exist"""
        new_config_dir = tmp_path / "new_etc" / "sos"
        new_config_file = new_config_dir / "ai_config.json"
        
        config_mgr = AIConfig(str(new_config_file))
        config_mgr.save_config()
        
        assert os.path.exists(str(new_config_file))
        assert os.path.exists(str(new_config_dir))

    def test_config_deep_merge(self, tmp_path):
        """Verify that nested config keys are merged correctly"""
        config_file = tmp_path / "deep_merge.json"
        # Only override one nested key
        partial_config = {
            "gemini": {
                "model": "custom-model"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(partial_config, f)
            
        config_mgr = AIConfig(str(config_file))
        
        # Overridden key
        assert config_mgr.config["gemini"]["model"] == "custom-model"
        # Original default keys should still exist in the nested dict
        assert config_mgr.config["gemini"]["enabled"] is True
        assert config_mgr.config["gemini"]["cli_path"] == "/usr/local/bin/gemini"
