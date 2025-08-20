# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2024 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
from urllib.parse import urljoin

from .connection_helpers import sanitize_url


class ServerAddress:
    """
    Encapsulates information about server API address and endpoints
    Args:
        base_url: the base URL (https://ww.comet.com/mpm/)
        api_version: the current API version (v2)
    """

    def __init__(self, base_url: str, api_version: str):
        self.base_url = base_url
        self.api_version = api_version
        self._api_full_path = sanitize_url(urljoin(base_url, api_version))

    @property
    def api_path(self) -> str:
        return self._api_full_path

    def __str__(self) -> str:
        return self.api_path

    def __repr__(self) -> str:
        return self.api_path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServerAddress):
            return NotImplemented
        return self.api_path == other.api_path

    def batch_endpoint_url(self) -> str:
        return urljoin(self._api_full_path, "events/batch")

    def labels_endpoint_url(self) -> str:
        return urljoin(self._api_full_path, "labels/batch")

    def is_alive_endpoint_url(self) -> str:
        return urljoin(self.base_url, "isAlive/ping")
