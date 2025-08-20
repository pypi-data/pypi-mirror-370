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

from typing import Optional, Tuple, cast

from ..config import get_config
from ..connection import get_api_http_session
from ..exceptions import CometMPMException
from ..settings_helper import extract_comet_api_url
from . import rest_client
from .model import Model


class API:
    """
    Main entry point for interacting with the Comet MPM API.

    Provides high-level methods for working with models and workspaces.

    Args:
        api_key: The Comet API key for authentication
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the Comet MPM API client.

        Args:
            api_key: The Comet API key for authentication
        """
        self._config = get_config()
        api_key = self._get_api_key(api_key)

        base_url = extract_comet_api_url(
            api_key, self._config.get("comet.url_override")
        )
        requests_session = get_api_http_session(api_key)
        self._client = rest_client.Client(requests_session, base_url)

    def _get_api_key(self, api_key: Optional[str]) -> str:
        """
        Makes sure that the API key is available.
        """
        api_key = api_key or self._config.get("comet.api_key")

        if api_key is None:
            raise CometMPMException(
                "COMET_API_KEY is not defined in environment, and api_key is not given"
            )

        return api_key

    def get_model_by_name(
        self, workspace_name: str, model_name: str
    ) -> Optional[Model]:
        """
        Get a model instance by workspace name and model name.

        Args:
            workspace_name: Name of the workspace containing the model
            model_name: Name of the model to retrieve

        Returns:
            Model: A Model instance for the specified model, if it exists, otherwise None
        """
        model_id = self.get_model_id(workspace_name, model_name)
        if model_id is not None:
            return Model(client=self._client, model_id=model_id)
        else:
            return None

    def get_model(self) -> Optional[Model]:
        """
        Get the default model for this dashboard in a Python Panel environment.

        Returns:
            Model: A Model instance for the model
        """
        model_id = self._config.get_option("modelId")
        if model_id:
            return Model(client=self._client, model_id=model_id)
        else:
            return None

    def get_model_id(self, workspace_name: str, model_name: str) -> Optional[str]:
        """
        Get the model ID for a given workspace and model name.

        Args:
            workspace_name: Name of the workspace containing the model
            model_name: Name of the model to retrieve

        Returns:
            Optional[str]: The model ID if found, None otherwise
        """
        return self._client.get_model_id(workspace_name, model_name)

    def get_panel_workspace(self) -> Optional[str]:
        """
        Get the workspace name from panel options.

        Returns:
            Optional[str]: The workspace name from panel options, or None if not found
        """
        return cast(Optional[str], self._config.get("comet.workspace"))

    def get_panel_width(self) -> int:
        """
        Get the panel width from configuration.

        Returns:
            int: The panel width
        """
        return cast(int, self._config.get("COMET_PANEL_WIDTH"))

    def get_panel_height(self) -> int:
        """
        Get the panel height from configuration.

        Returns:
            int: The panel height
        """
        return cast(int, self._config.get("COMET_PANEL_HEIGHT"))

    def get_panel_size(self) -> Tuple[int, int]:
        """
        Get the panel size (width, height) from configuration.

        Returns:
            Tuple[int, int]: The panel size as (width, height)
        """
        width: int = cast(int, self._config.get("COMET_PANEL_WIDTH"))
        height: int = cast(int, self._config.get("COMET_PANEL_HEIGHT"))
        return (width, height)
