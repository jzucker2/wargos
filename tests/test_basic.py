import unittest
import os
from unittest.mock import patch
from app.utils import LogHelper
from app.version import version


class TestBasicFunctionality(unittest.TestCase):
    """Basic tests that should always pass"""

    def test_version_is_string(self):
        """Test that version is a string"""
        self.assertIsInstance(version, str)
        self.assertGreater(len(version), 0)

    def test_log_helper_debug_env_flag_default(self):
        """Test that debug env flag defaults to False"""
        # Clear any existing DEBUG env var
        with patch.dict(os.environ, {}, clear=True):
            result = LogHelper.get_debug_env_flag()
            self.assertFalse(result)
            self.assertIsInstance(result, bool)

    def test_log_helper_debug_env_flag_true(self):
        """Test that debug env flag returns True when set"""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            result = LogHelper.get_debug_env_flag()
            self.assertTrue(result)

    def test_log_helper_debug_env_flag_false(self):
        """Test that debug env flag returns False when set to false"""
        with patch.dict(os.environ, {"DEBUG": "false"}):
            result = LogHelper.get_debug_env_flag()
            self.assertFalse(result)

    def test_log_helper_get_fast_api_logger(self):
        """Test that get_fast_api_logger returns a logger"""
        logger = LogHelper.get_fast_api_logger("test_logger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")

    def test_log_helper_get_debug_logger(self):
        """Test that get_debug_logger returns a debug logger"""
        logger = LogHelper.get_debug_logger("test_debug")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.level, 10)  # DEBUG level

    def test_log_helper_get_info_logger(self):
        """Test that get_info_logger returns an info logger"""
        logger = LogHelper.get_info_logger("test_info")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.level, 20)  # INFO level

    def test_log_helper_get_env_logger_debug(self):
        """Test that get_env_logger returns debug logger when DEBUG=true"""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            logger = LogHelper.get_env_logger("test_env")
            self.assertEqual(logger.level, 10)  # DEBUG level

    def test_log_helper_get_env_logger_info(self):
        """Test that get_env_logger returns info logger when DEBUG=false"""
        with patch.dict(os.environ, {"DEBUG": "false"}):
            logger = LogHelper.get_env_logger("test_env")
            self.assertEqual(logger.level, 20)  # INFO level


if __name__ == "__main__":
    unittest.main()
