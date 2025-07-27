import unittest
import os
from unittest.mock import patch, MagicMock
from app.wled_client import WLEDClient


class TestWLEDClientSimple(unittest.TestCase):
    """Simple tests for WLEDClient that don't require complex async mocking"""

    def test_get_client_without_session(self):
        """Test that get_client returns a WLEDClient instance without session"""
        client = WLEDClient.get_client()
        self.assertIsInstance(client, WLEDClient)
        self.assertIsNone(client.session)

    def test_get_client_with_session(self):
        """Test that get_client returns a WLEDClient instance with session"""
        mock_session = MagicMock()
        client = WLEDClient.get_client(session=mock_session)
        self.assertIsInstance(client, WLEDClient)
        self.assertEqual(client.session, mock_session)

    @patch.dict(os.environ, {"DEFAULT_WLED_IP": "192.168.1.100"})
    def test_default_wled_ip_from_env(self):
        """Test that default_wled_ip returns value from environment variable"""
        self.assertEqual(WLEDClient.default_wled_ip(), "192.168.1.100")

    def test_default_wled_ip_fallback(self):
        """Test that default_wled_ip returns fallback value when env var is not set"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(WLEDClient.default_wled_ip(), "10.0.1.179")

    def test_init_without_session(self):
        """Test that WLEDClient initializes correctly without session"""
        client = WLEDClient()
        self.assertIsNone(client.session)

    def test_init_with_session(self):
        """Test that WLEDClient initializes correctly with session"""
        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        self.assertEqual(client.session, mock_session)

    def test_session_property(self):
        """Test that session property returns the session"""
        mock_session = MagicMock()
        client = WLEDClient(session=mock_session)
        self.assertEqual(client.session, mock_session)


if __name__ == "__main__":
    unittest.main()
