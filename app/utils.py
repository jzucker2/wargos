import logging
import sys
import os


class LogHelper(object):
    @classmethod
    def get_debug_env_flag(cls):
        return bool(os.environ.get('DEBUG', 'false').lower() == 'true')

    @classmethod
    def get_fast_api_logger(cls, name, log_level=logging.DEBUG):
        """For more on logging, see the readme"""
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s'))
        # log_formatter = logging.Formatter(
        #     "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
        # stream_handler.setFormatter(log_formatter)
        # logger.addHandler(stream_handler)
        logger.addHandler(consoleHandler)
        return logger

    @classmethod
    def get_debug_logger(cls, name):
        return cls.get_fast_api_logger(name, log_level=logging.DEBUG)

    @classmethod
    def get_info_logger(cls, name):
        return cls.get_fast_api_logger(name, log_level=logging.INFO)

    @classmethod
    def get_env_logger(cls, name):
        is_debug = cls.get_debug_env_flag()
        if is_debug:
            return cls.get_debug_logger(name)
        return cls.get_info_logger(name)
