import unittest
import os
from unittest.mock import patch, MagicMock
from app.scraper import Scraper


class TestScraperSimple(unittest.TestCase):
    """Simple tests for Scraper that don't require complex async mocking"""

    def test_get_client(self):
        """Test that get_client returns a Scraper instance"""
        scraper = Scraper.get_client()
        self.assertIsInstance(scraper, Scraper)

    def test_get_default_scrape_interval_default(self):
        """Test that get_default_scrape_interval returns a value"""
        result = Scraper.get_default_scrape_interval()
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_get_default_wait_first_interval_default(self):
        """Test that get_default_wait_first_interval returns a value"""
        result = Scraper.get_default_wait_first_interval()
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    @patch.dict(os.environ, {"WLED_IP_LIST": "192.168.1.100,192.168.1.101"})
    def test_get_env_wled_ip_list_with_env(self):
        """Test that get_env_wled_ip_list returns list from environment variable"""
        result = Scraper.get_env_wled_ip_list()
        self.assertEqual(result, "192.168.1.100,192.168.1.101")

    def test_get_env_wled_ip_list_missing(self):
        """Test that get_env_wled_ip_list returns None when env var is missing"""
        with patch.dict(os.environ, {}, clear=True):
            result = Scraper.get_env_wled_ip_list()
            self.assertIsNone(result)

    @patch.dict(os.environ, {"WLED_IP_LIST": "192.168.1.100,192.168.1.101"})
    def test_parse_env_wled_ip_list(self):
        """Test that parse_env_wled_ip_list correctly parses comma-separated string"""
        result = Scraper.parse_env_wled_ip_list()
        self.assertEqual(result, ["192.168.1.100", "192.168.1.101"])

    @patch.dict(os.environ, {"WLED_IP_LIST": "192.168.1.100"})
    def test_parse_env_wled_ip_list_single_ip(self):
        """Test that parse_env_wled_ip_list handles single IP"""
        result = Scraper.parse_env_wled_ip_list()
        self.assertEqual(result, ["192.168.1.100"])

    @patch.dict(os.environ, {"WLED_IP_LIST": ""})
    def test_parse_env_wled_ip_list_empty(self):
        """Test that parse_env_wled_ip_list handles empty string"""
        result = Scraper.parse_env_wled_ip_list()
        self.assertIsNone(result)

    def test_init(self):
        """Test that Scraper initializes correctly"""
        mock_client = MagicMock()
        scraper = Scraper(mock_client)
        self.assertEqual(scraper.wled_client, mock_client)

    def test_wled_client_property(self):
        """Test that wled_client property returns the client"""
        mock_client = MagicMock()
        scraper = Scraper(mock_client)
        self.assertEqual(scraper.wled_client, mock_client)

    def test_default_wled_ip(self):
        """Test that default_wled_ip delegates to wled_client"""
        mock_client = MagicMock()
        mock_client.default_wled_ip.return_value = "192.168.1.100"
        scraper = Scraper(mock_client)
        result = scraper.default_wled_ip()
        self.assertEqual(result, "192.168.1.100")
        mock_client.default_wled_ip.assert_called_once()


if __name__ == "__main__":
    unittest.main()
