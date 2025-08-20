# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import getpass
import logging
import logging.handlers
import os
import re
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .logging_messages import (
    LOGGING_DIRECTORY_CREATION_ERROR,
    LOGGING_LOG_FILE_OPEN_ERROR,
)
from .settings import LogLevel, LogSettings, get_model

LOGGER = logging.getLogger(__name__)

MSG_FORMAT = "COMET %(levelname)s: %(message)s"

FILE_MSG_FORMAT = "[%(process)d-%(processName)s:%(thread)d] %(relativeCreated)d COMET %(levelname)s [%(filename)s:%(lineno)d]: %(message)s"


class ErrorStore:
    """Thread-safe store for logging errors that can be retrieved programmatically."""

    def __init__(self) -> None:
        self._errors: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add_error(
        self,
        message: str,
        logger_name: str,
        data_affected: Optional[List[Dict[str, Any]]] = None,
        traceback_info: Optional[str] = None,
    ) -> None:
        """Add a structured error to the store.

        Args:
            message: The error message
            logger_name: Name of the logger that produced the error
            data_affected: Description of what data was affected (optional)
            traceback_info: Traceback information (optional)
        """
        with self._lock:
            error_entry = {
                "message": message,
                "logger_name": logger_name,
                "timestamp": datetime.now().isoformat(),
                "data_affected": data_affected,
                "traceback": traceback_info,
            }
            self._errors.append(error_entry)

    def get_errors(self, clear: bool = True) -> List[Dict[str, Any]]:
        """Get all stored errors, optionally clearing the store."""
        with self._lock:
            errors = self._errors.copy()
            if clear:
                self._errors.clear()
            return errors

    def has_errors(self) -> bool:
        """Check if there are any stored errors."""
        with self._lock:
            return len(self._errors) > 0


def get_user() -> str:
    try:
        return getpass.getuser()
    except KeyError:
        return "unknown"


def _make_valid(s: str) -> str:
    s = str(s).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-\w.]", "", s)


def expand_log_file_path(log_file_path: Optional[str]) -> Optional[str]:
    """
    Expand patterns in the file logging path.

    Allowed patterns:
        * {datetime}
        * {pid}
        * {project}
        * {user}
    """

    if log_file_path is None:
        return None

    user = _make_valid(get_user())

    patterns = {
        "datetime": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "pid": os.getpid(),
        "user": user,
    }

    try:
        return log_file_path.format(**patterns)
    except KeyError:
        LOGGER.info(
            "Invalid logging file pattern: '%s'; ignoring",
            log_file_path,
            exc_info=True,
        )
        return log_file_path


class CometLoggingConfig(object):
    def __init__(self, settings: LogSettings) -> None:
        self.root = logging.getLogger("comet_mpm")
        logger_level = logging.CRITICAL

        # Don't send comet-mpm to the application logger
        self.root.propagate = settings.mpm_logging_propagate

        # Add handler for console, basic INFO:
        self.console_handler = logging.StreamHandler()

        logging_console_level = settings.mpm_logging_console
        self.console_formatter = logging.Formatter(MSG_FORMAT)

        self.console_handler.setLevel(logging_console_level)
        self.console_handler.setFormatter(self.console_formatter)

        # Only add console handler if a StreamHandler doesn't already exist
        # (FileHandler is a subclass of StreamHandler, so we need to exclude it)
        if not any(
            isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.FileHandler)
            for h in self.root.handlers
        ):
            self.root.addHandler(self.console_handler)

        logger_level = min(logger_level, self.console_handler.level)

        # The std* logger might conflicts with the logging if a log record is
        # emitted for each WS message as it would results in an infinite loop. To
        # avoid this issue, all log records after the creation of a message should
        # be at a level lower than info as the console handler is set to info
        # level.

        # Add an additional file handler
        log_file_path = expand_log_file_path(
            settings.mpm_logging_file,
        )
        log_file_level = settings.mpm_logging_file_level
        log_file_overwrite = settings.mpm_logging_file_overwrite

        self.file_handler = None
        self.file_formatter = None

        if log_file_path is not None:

            # Create logfile path, if possible:
            try:
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            except Exception:
                LOGGER.error(
                    LOGGING_DIRECTORY_CREATION_ERROR, log_file_path, exc_info=True
                )

            try:
                # Overwrite file if comet_mpm_file_overwrite:
                if log_file_overwrite:
                    self.file_handler = logging.FileHandler(log_file_path, "w+")
                else:
                    self.file_handler = logging.FileHandler(log_file_path)

                if log_file_level is None:
                    log_file_level = LogLevel(logging.DEBUG)

                self.file_handler.setLevel(log_file_level)
                logger_level = min(logger_level, log_file_level)

                self.file_formatter = logging.Formatter(FILE_MSG_FORMAT)
                self.file_handler.setFormatter(self.file_formatter)

                # Only add file handler if one doesn't already exist for the same file
                if not any(
                    isinstance(h, logging.FileHandler)
                    and h.baseFilename == self.file_handler.baseFilename
                    for h in self.root.handlers
                ):
                    self.root.addHandler(self.file_handler)
            except Exception:
                LOGGER.error(
                    LOGGING_LOG_FILE_OPEN_ERROR,
                    log_file_path,
                    exc_info=True,
                )

        self.root.setLevel(logger_level)


COMET_LOGGING_CONFIG = None


def _setup_comet_mpm_logging() -> None:
    global COMET_LOGGING_CONFIG

    # Create a settings, read env variables if set and validate values
    settings = get_model(LogSettings)
    COMET_LOGGING_CONFIG = CometLoggingConfig(settings)
