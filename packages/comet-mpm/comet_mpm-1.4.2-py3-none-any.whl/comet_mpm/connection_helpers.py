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
from typing import Dict
from urllib.parse import urljoin, urlparse, urlsplit, urlunparse, urlunsplit

from comet_mpm.exceptions import CometMPMBackendException, CometMPMBackendIsNotAvailable
from comet_mpm.logging_messages import BACKEND_500_ERROR


def sanitize_url(url: str) -> str:
    """Sanitize a URL, checking that it is a valid URL and ensure it contains an ending slash /"""
    parts = urlparse(url)
    scheme, netloc, path, params, query, fragment = parts

    # TODO: Raise an exception if params, query and fragment are not empty?

    # Ensure the leading slash
    if path and not path.endswith("/"):
        path = path + "/"
    elif not path and not netloc.endswith("/"):
        netloc = netloc + "/"

    return urlunparse((scheme, netloc, path, params, query, fragment))


def url_join(base: str, *parts: str) -> str:
    """Given a base and url parts (for example [workspace, project, id]) returns a full URL"""
    # TODO: Enforce base to have a scheme and netloc?
    result = base

    for part in parts[:-1]:
        if not part.endswith("/"):
            raise ValueError("Intermediary part not ending with /")

        result = urljoin(result, part)

    result = urljoin(result, parts[-1])

    return result


def get_root_url(url: str) -> str:
    """Remove the path, params, query and fragment from a given URL"""
    parts = urlsplit(url)
    scheme, netloc, path, query, fragment = parts

    return urlunsplit((scheme, netloc, "", "", ""))


def make_request_headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": api_key}


def is_alive_raise_for_status_code(status_code: int) -> None:
    if status_code == 200:
        return
    if status_code == 500:
        raise CometMPMBackendException(BACKEND_500_ERROR)
    else:
        raise CometMPMBackendIsNotAvailable()
