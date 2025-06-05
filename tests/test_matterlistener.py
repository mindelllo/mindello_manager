"""Unit tests for the MatterListener class in mindello_manager.matterlistener."""

import unittest
from unittest.mock import MagicMock, patch

from scapy.error import Scapy_Exception
from zeroconf import Zeroconf

from mindello_manager.matterlistener import MatterListener


class TestMatterListener(unittest.TestCase):
    """Unit tests for the MatterListener class."""

    def setUp(self) -> None:
        """Set up a MatterListener instance and mock Zeroconf for each test."""
        self.listener = MatterListener()
        self.zc = MagicMock(spec=Zeroconf)
        self.type_ = "_matter._tcp.local."
        self.name = "TestDevice._matter._tcp.local."

    def test_init_devices_empty(self) -> None:
        """Test that the devices list is initialized as empty."""
        # Use pytest-style assertion for compatibility with linter
        assert self.listener.devices == []

    def test_remove_service_does_nothing(self) -> None:
        """Test that remove_service does not alter the devices list."""
        self.listener.devices.append({"mac_address": "00:11:22:33:44:55"})
        self.listener.remove_service(self.zc, self.type_, self.name)
        assert len(self.listener.devices) == 1

    def test_update_service_does_nothing(self) -> None:
        """Test that update_service does not alter the devices list."""
        self.listener.devices.append({"mac_address": "00:11:22:33:44:55"})
        self.listener.update_service(self.zc, self.type_, self.name)
        assert len(self.listener.devices) == 1

    @patch("mindello_manager.matterlistener.requests.get")
    @patch("mindello_manager.matterlistener.srp")
    def test_add_service_successful_device(
        self,
        mock_srp: MagicMock,
        mock_requests_get: MagicMock,
    ) -> None:
        """Test add_service adds a device when all conditions are met."""
        info = MagicMock()
        info.parsed_addresses.return_value = ["192.168.1.2"]
        info.port = 80
        self.zc.get_service_info.return_value = info
        mock_srp.return_value = (
            [(None, MagicMock(sprintf=MagicMock(return_value="AA:BB:CC:DD:EE:FF")))],
            None,
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        self.listener.add_service(self.zc, self.type_, self.name)
        assert len(self.listener.devices) == 1
        device = self.listener.devices[0]
        assert device["mac_address"] == "AA:BB:CC:DD:EE:FF"
        assert device["http_auth_ok"] is True
        assert device["name"] == self.name

    @patch("mindello_manager.matterlistener.srp")
    def test_add_service_no_mac(
        self,
        mock_srp: MagicMock,
    ) -> None:
        """Test add_service does not add a device if MAC address cannot be obtained."""
        info = MagicMock()
        info.parsed_addresses.return_value = ["192.168.1.3"]
        info.port = 80
        self.zc.get_service_info.return_value = info
        mock_srp.side_effect = Scapy_Exception("No MAC")
        self.listener.add_service(self.zc, self.type_, self.name)
        assert len(self.listener.devices) == 0

    def test_add_service_no_info(self) -> None:
        """Test add_service does nothing if no service info is returned."""
        self.zc.get_service_info.return_value = None
        self.listener.add_service(self.zc, self.type_, self.name)
        assert len(self.listener.devices) == 0

    @patch("mindello_manager.matterlistener.requests.get")
    @patch("mindello_manager.matterlistener.srp")
    def test_add_service_duplicate_mac(
        self,
        mock_srp: MagicMock,
        mock_requests_get: MagicMock,
    ) -> None:
        """Test add_service does not add duplicate devices with the same MAC address."""
        info = MagicMock()
        info.parsed_addresses.return_value = ["192.168.1.4"]
        info.port = 80
        self.zc.get_service_info.return_value = info
        mock_srp.return_value = (
            [(None, MagicMock(sprintf=MagicMock(return_value="AA:BB:CC:DD:EE:FF")))],
            None,
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        self.listener.add_service(self.zc, self.type_, self.name)
        self.listener.add_service(self.zc, self.type_, self.name)
        assert len(self.listener.devices) == 1


if __name__ == "__main__":
    unittest.main()
