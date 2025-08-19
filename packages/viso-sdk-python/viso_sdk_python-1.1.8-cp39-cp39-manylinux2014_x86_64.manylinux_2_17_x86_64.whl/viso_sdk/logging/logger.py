"""
Viso Logging Module
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from viso_sdk.constants import NODE_TYPE, LOG_DIR


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    def __init__(self) -> None:
        super().__init__()

        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31a;1m"
        reset = "\x1b[0m"
        _format = "%(asctime)s:: %(name)-15s :: %(levelname)-4s :: %(message)s [%(filename)s:%(lineno)d]"

        self.formats = {
            logging.DEBUG: grey + _format + reset,
            logging.INFO: grey + _format + reset,
            logging.WARNING: yellow + _format + reset,
            logging.ERROR: red + _format + reset,
            logging.CRITICAL: bold_red + _format + reset,
        }

    def format(self, record):  # type: ignore
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class VisoLogger:
    """Viso Logger Class

    Args:
        info_file: File name of info level logs.
            Using `/viso/<NODE_TYPE>_<NODE_ID>/logs/<NODE_TYPE>.log` if not defined.
        error_file: File name of error level logs.
    """

    def __init__(
            self, info_file: Optional[str] = None, error_file: Optional[str] = None
    ) -> None:

        self._info_file = info_file or os.path.join(LOG_DIR, f"{NODE_TYPE}.log")
        self._error_file = error_file

    def init_logger(self, name: str) -> logging.Logger:
        """Initialize a logger instance.

        Args:
            name(str): Logger name
        """
        # Note: Loggers are never instantiated directly, but always through the module-level function
        # logging.getLogger(name). Multiple calls to getLogger() with the same name will always
        # return a reference to the same Logger object.
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
        logger.handlers = []
        formatter = CustomFormatter()

        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Add file handlers
        f_info_handler = RotatingFileHandler(
            self._info_file, maxBytes=5 * 1024 * 1024, backupCount=4
        )
        f_info_handler.setLevel(logging.INFO)
        f_info_handler.setFormatter(formatter)
        logger.addHandler(f_info_handler)

        if self._error_file is not None:
            f_err_handler = RotatingFileHandler(
                self._error_file, maxBytes=5 * 1024 * 1024, backupCount=4
            )
            f_err_handler.setLevel(logging.ERROR)
            f_err_handler.setFormatter(formatter)
            logger.addHandler(f_err_handler)

        return logger


def get_logger(
        name: str = "main",
        info_file: Optional[str] = None,
        error_file: Optional[str] = None,
) -> logging.Logger:
    """Generate a Viso logger instance

    Args:
        name(str): Name of the target logger
        info_file(str): Info file path(optional)
        error_file(str): Error file path(optional)
    """
    return VisoLogger(info_file, error_file).init_logger(name)
