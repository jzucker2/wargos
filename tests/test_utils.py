import unittest
import logging
import os
from unittest.mock import patch
from app.utils import LogHelper


class TestUtils(unittest.TestCase):
    def test_foo(self):
        self.assertTrue(True)

    def test_log_helper_debug_env_flag_is_default_false(self):
        expected = False
        actual = LogHelper.get_debug_env_flag()
        self.assertEqual(actual, expected)
        self.assertIsInstance(actual, bool)
        self.assertFalse(actual)

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_log_helper_debug_env_flag_true(self):
        """Test that DEBUG=true returns True"""
        self.assertTrue(LogHelper.get_debug_env_flag())

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_log_helper_debug_env_flag_false(self):
        """Test that DEBUG=false returns False"""
        self.assertFalse(LogHelper.get_debug_env_flag())

    @patch.dict(os.environ, {"DEBUG": "TRUE"})
    def test_log_helper_debug_env_flag_case_insensitive(self):
        """Test that DEBUG=TRUE returns True (case insensitive)"""
        self.assertTrue(LogHelper.get_debug_env_flag())

    def test_log_helper_debug_env_flag_no_env_var(self):
        """Test that missing DEBUG env var returns False"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(LogHelper.get_debug_env_flag())

    def test_get_fast_api_logger(self):
        """Test that get_fast_api_logger returns a logger with correct configuration"""
        logger = LogHelper.get_fast_api_logger("test_logger")

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.DEBUG)

        # Check that it has a handler
        self.assertGreater(len(logger.handlers), 0)

        # Check that the handler is a StreamHandler
        handler = logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)

    def test_get_fast_api_logger_with_custom_level(self):
        """Test that get_fast_api_logger accepts custom log level"""
        logger = LogHelper.get_fast_api_logger(
            "test_logger", log_level=logging.INFO
        )
        self.assertEqual(logger.level, logging.INFO)

    def test_get_debug_logger(self):
        """Test that get_debug_logger returns a debug level logger"""
        logger = LogHelper.get_debug_logger("test_debug")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_get_info_logger(self):
        """Test that get_info_logger returns an info level logger"""
        logger = LogHelper.get_info_logger("test_info")
        self.assertEqual(logger.level, logging.INFO)

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_get_env_logger_debug_mode(self):
        """Test that get_env_logger returns debug logger when DEBUG=true"""
        logger = LogHelper.get_env_logger("test_env_debug")
        self.assertEqual(logger.level, logging.DEBUG)

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_get_env_logger_info_mode(self):
        """Test that get_env_logger returns info logger when DEBUG=false"""
        logger = LogHelper.get_env_logger("test_env_info")
        self.assertEqual(logger.level, logging.INFO)

    def test_get_env_logger_no_debug_env(self):
        """Test that get_env_logger returns info logger when DEBUG env var is not set"""
        with patch.dict(os.environ, {}, clear=True):
            logger = LogHelper.get_env_logger("test_env_no_debug")
            self.assertEqual(logger.level, logging.INFO)


if __name__ == "__main__":
    unittest.main()
