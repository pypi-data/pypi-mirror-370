# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021-2024 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import logging
from typing import Optional, Union

from .api_key.comet_api_key import parse_api_key
from .connection_helpers import get_root_url, sanitize_url
from .logging_messages import BASE_URL_MISMATCH_CONFIG_API_KEY
from .settings import AnyHttpUrl, MPMSettings

LOGGER = logging.getLogger(__name__)
DEFAULT_COMET_BASE_URL = "https://www.comet.com/"


def extract_comet_url(settings: MPMSettings) -> str:
    """Extracts Comet base url from settings or API key and sanitizes it (appends / at the end)"""
    api_key = parse_api_key(settings.api_key)
    if api_key is None:
        return DEFAULT_COMET_BASE_URL

    if settings.url is not None:
        settings_base_url = sanitize_url(get_root_url(str(settings.url)))
        if (
            api_key.base_url is not None
            and sanitize_url(api_key.base_url) != settings_base_url
        ):
            LOGGER.warning(
                BASE_URL_MISMATCH_CONFIG_API_KEY,
                settings_base_url,
                sanitize_url(api_key.base_url),
            )
        # do not change base url but add trailing slash if not there
        return sanitize_url(str(settings.url))

    if api_key.base_url is not None:
        return sanitize_url(api_key.base_url)

    return DEFAULT_COMET_BASE_URL


def extract_comet_api_url(
    settings_api_key: Optional[str], settings_url: Optional[Union[str, AnyHttpUrl]]
) -> str:
    """
    Determines the Comet base URL based on the provided API key and URL.

    Args:
        settings_api_key (Optional[str]): The API key for Comet, which may contain a base URL.
        settings_url (Optional[Union[str, AnyHttpUrl]]): The URL explicitly set in the settings.

    Returns:
        str: The sanitized Comet base URL, with a trailing slash if not already present.
    """
    if settings_api_key is None:
        return DEFAULT_COMET_BASE_URL

    api_key = parse_api_key(settings_api_key)
    if api_key is None:
        return DEFAULT_COMET_BASE_URL

    if settings_url is not None:
        settings_base_url = sanitize_url(get_root_url(str(settings_url)))
        if (
            api_key.base_url is not None
            and sanitize_url(api_key.base_url) != settings_base_url
        ):
            LOGGER.warning(
                BASE_URL_MISMATCH_CONFIG_API_KEY,
                settings_base_url,
                sanitize_url(api_key.base_url),
            )
        # do not change base url but add trailing slash if not there
        return settings_base_url

    if api_key.base_url is not None:
        return sanitize_url(api_key.base_url)

    return DEFAULT_COMET_BASE_URL
