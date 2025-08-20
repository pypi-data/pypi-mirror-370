# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021-2025 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import inspect
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


def find_page_name() -> Optional[str]:
    """
    This function searches the call stack to find the name of the calling
    Python Panel function. It depends on the name of the panel script.
    """
    stack = inspect.stack()
    for row in stack:
        frame, filename, line_number, function_name, lines, index = row
        basename = os.path.basename(filename)
        # NOTE: this is based on specific naming of the Python Panel files:
        if basename.startswith("edit_mpm_panel_") or basename.startswith("mpm_panel_"):
            return basename

    return None


class ConfigStrategy(ABC):
    """Abstract base class for configuration strategies."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Get a configuration value."""
        pass

    @abstractmethod
    def get_option(self, option_key: str) -> Any:
        """Get a specific option with proper fallback."""
        pass


class PythonPanelConfig(ConfigStrategy):
    """Configuration strategy for Python Panel environment."""

    def __init__(self, page_name: str, config_override: Dict[str, Any]):
        """
        Initialize with page name and config override.

        Args:
            page_name: Name of the panel page
            config_override: Configuration override dictionary
        """
        self._page_name = page_name
        self._config_override = config_override

    def get(self, key: str) -> Any:
        """
        Get the key in the config from Python Panel environment.
        """
        config = self._config_override.get(self._page_name, {})
        return config.get(key, None)

    def get_option(self, option_key: str) -> Any:
        """
        Get a specific option from COMET_PANEL_OPTIONS with proper fallback.

        This method ensures that even if the panel options are overridden
        and don't contain a specific key, we fall back to the default values.

        Args:
            option_key: The specific option key to retrieve

        Returns:
            The option value, or None if not found in either source
        """
        # First try to get from the current panel options
        panel_options = self.get("COMET_PANEL_OPTIONS")
        if panel_options is not None:
            value = panel_options.get(option_key)
            if value is not None:
                return value

        # If not found or panel_options is None, get the default
        default_options = self._get_default_panel_options()
        if default_options is not None:
            return default_options.get(option_key)

        return None

    def _get_default_panel_options(self) -> Optional[Dict[str, Any]]:
        """Get the default panel options."""
        # Get current time in local timezone
        now = datetime.now()
        # Calculate 30 days ago
        thirty_days_ago = now - timedelta(days=30)

        return {
            "filters": [],
            "intervalType": "DAILY",
            "startDate": thirty_days_ago.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "endDate": now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        }


class DefaultConfig(ConfigStrategy):
    """Configuration strategy for hard-coded defaults."""

    def get(self, key: str) -> Any:
        """
        Get configuration values from hard-coded defaults.
        """
        if key == "COMET_PANEL_OPTIONS":
            # Get current time in local timezone
            now = datetime.now()
            # Calculate 30 days ago
            thirty_days_ago = now - timedelta(days=30)

            return {
                "filters": [],
                "intervalType": "DAILY",
                "startDate": thirty_days_ago.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
                + "Z",
                "endDate": now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            }

        elif key == "comet.url_override":
            return os.environ.get("COMET_URL_OVERRIDE")

        elif key == "comet.api_key":
            return os.environ.get("COMET_API_KEY")

        elif key == "comet.workspace":
            return os.environ.get("COMET_WORKSPACE")

        elif key == "COMET_PANEL_WIDTH":
            return 901

        elif key == "COMET_PANEL_HEIGHT":
            return 248

        else:
            return None

    def get_option(self, option_key: str) -> Any:
        """
        Get a specific option from COMET_PANEL_OPTIONS.

        Args:
            option_key: The specific option key to retrieve

        Returns:
            The option value, or None if not found
        """
        panel_options = self.get("COMET_PANEL_OPTIONS")
        if panel_options is not None:
            return panel_options.get(option_key)
        return None


def get_config() -> ConfigStrategy:
    """
    Factory function that returns the appropriate config strategy.

    Returns:
        ConfigStrategy: The appropriate configuration strategy based on the environment
    """
    try:
        import streamlit as st
    except ImportError:
        return DefaultConfig()

    page_name = find_page_name()
    if page_name is None:
        return DefaultConfig()

    config_override = st.session_state.get("comet_config_override")
    if not isinstance(config_override, dict):
        return DefaultConfig()

    return PythonPanelConfig(page_name, config_override)
