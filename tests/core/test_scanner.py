import pytest
from src.core.scanner import WifiScanner

class TestScanner:
    @pytest.fixture
    def scanner(self):
        return WifiScanner(interface="wlan0")

    def test_parse_iw_output(self, scanner):
        mock_output = """
BSS 00:11:22:33:44:55(on wlan0)
    TSF: 123456789 usec
    freq: 2412
    beacon interval: 100 TUs
    capability: ESS Privacy ShortPreamble (0x0411)
    signal: -50.00 dBm
    last seen: 0 ms ago
    SSID: TestNetwork
BSS 66:77:88:99:AA:BB(on wlan0)
    freq: 5180
    signal: -70.00 dBm
    SSID: 5G_Network
"""
        networks = scanner._parse_scan_results(mock_output)
        
        assert len(networks) == 2
        assert networks[0]["ssid"] == "TestNetwork"
        assert networks[0]["bssid"] == "00:11:22:33:44:55"
        assert networks[0]["signal"] == -50
        assert networks[0]["channel"] == 1
        
        assert networks[1]["ssid"] == "5G_Network"
        assert networks[1]["channel"] == 36

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__]))
