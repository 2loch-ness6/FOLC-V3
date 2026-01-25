import pytest
from unittest.mock import MagicMock, patch
from src.core.auditor import NetworkAuditor

class TestNetworkAuditor:
    @pytest.fixture
    def auditor(self):
        return NetworkAuditor()

    def test_enable_ip_forwarding(self, auditor):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert auditor.enable_ip_forwarding(True) is True
            mock_run.assert_called_with(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)

    def test_setup_arp_mitm(self, auditor):
        result = auditor.setup_arp_mitm("192.168.1.5", "192.168.1.1")
        assert result["status"] == "success"
        assert result["target"] == "192.168.1.5"

    def test_cage_target(self, auditor):
        result = auditor.cage_target("192.168.1.5")
        assert result["status"] == "success"
        assert result["caged_ip"] == "192.168.1.5"

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__]))
