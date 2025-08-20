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
import logging
import os
import platform
import time
import traceback
from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from ._logging import ErrorStore

import aiohttp
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import authhook
from .authhook import aws_sagemaker
from .connection_helpers import is_alive_raise_for_status_code, make_request_headers
from .dataset_upload_helpers import get_request_data
from .logging_messages import BATCH_SENDING_ERROR, UPLOAD_CSV_DATASET_ERROR
from .utils import get_comet_version

LOGGER = logging.getLogger(__name__)

MPM_BASE_PATH = os.environ.get("COMET_MPM_BASE_PATH", "/mpm/")

API_KEY_HEADER = "Authorization"


def setup_http_session_authentication(session: Session) -> None:
    """
    Sets up HTTP session authentication for accessing APIs.

    Args:
        session (Session): The HTTP session object that requires authentication setup.

    This function ensures authentication for accessing AWS SageMaker and integrates authentication hooks into the session.
    It checks if the environment is within AWS SageMaker and performs login operations specific to AWS SageMaker if True.

    Steps:
        1. Checks and performs late login to AWS SageMaker to read environment configuration values that might be set post-import.
        2. Integrates authentication hooks into the provided HTTP session.
    """
    if aws_sagemaker.is_in_aws_sagemaker():
        aws_sagemaker.login_aws_sagemaker()

    authhook.http_session_hook(session=session)


def get_retry_strategy() -> Retry:
    # The total backoff sleeping time is computed like that:
    # backoff = 2
    # total = 3
    # s = lambda b, i: b * (2 ** (i - 1))
    # sleep = sum(s(backoff, i) for i in range(1, total + 1))

    return Retry(total=3, backoff_factor=2, allowed_methods=None)  # Will wait up to 24s


def get_comet_http_session(
    api_key: Optional[str], retry_strategy: Optional[Retry] = None
) -> Session:
    # TODO: Check if config is needed
    # """Creates http session with Comet related headers set and authentication hook enabled."""
    # if config is None:
    #     config = get_config()  # This can be slow if called for every new session

    session = get_http_session(
        retry_strategy=retry_strategy,
        # config=config,
        # TODO: Check if verify_tls is needed
        # TODO: Check if tcp_keep_alive is needed
    )

    session.headers.update(
        {
            "X-COMET-DEBUG-SDK-VERSION": get_comet_version(),
            "X-COMET-DEBUG-PY-VERSION": platform.python_version(),
        }
    )

    # Add authorization header
    if api_key is not None:
        session.headers.update({API_KEY_HEADER: api_key})

    # Setup HTTP allow header if configured
    # TODO: Check if config is needed
    # allow_header_name = config["comet.allow_header.name"]
    # allow_header_value = config["comet.allow_header.value"]

    # if allow_header_name and allow_header_value:
    #     session.headers[allow_header_name] = allow_header_value

    setup_http_session_authentication(session)

    return session


def get_api_http_session(api_key: str) -> requests.Session:
    """
    Get a Request Session for MPM SDK API.
    """
    # The total backoff sleeping time is computed like that:
    # backoff = 2
    # total = 3
    # s = lambda b, i: b * (2 ** (i - 1))
    # sleep = sum(s(backoff, i) for i in range(1, total + 1))

    status_codes = [429, 500, 502, 503, 504]
    retry_strategy = Retry(
        total=3,
        status_forcelist=status_codes,
        backoff_factor=2,
        raise_on_status=False,
    )
    session = get_http_session(retry_strategy)
    # Add authorization header
    if api_key is not None:
        session.headers.update(
            {
                API_KEY_HEADER: api_key,
                "Accept": "application/json",
            }
        )
    return session


def get_http_session(retry_strategy: Optional[Retry] = None) -> Session:
    session = Session()

    # Setup retry strategy if asked
    if retry_strategy is not None:
        session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    return session


def stream_dataset_file(
    api_key: str,
    file_path: str,
    base_url: Optional[str],
    workspace_name: str,
    model_name: str,
    model_version: str,
    dataset_type: str,
    dataset_name: Optional[str] = None,
    na_values: Optional[str] = None,
    keep_default_na_values: Optional[str] = None,
) -> None:
    """Streams a file to a server with additional parameters and prints the response progress_message
    by progress_message using a requests.Session."""
    start_time = time.time()  # Start timing
    response = None
    try:
        # Open the file in binary mode for streaming
        with open(file_path, "rb") as file:
            files = {"file": (file_path, file, "text/csv")}
            data, url = get_request_data(
                base_url,
                workspace_name,
                model_name,
                model_version,
                dataset_type,
                dataset_name,
                na_values,
                keep_default_na_values,
            )

            headers = {"Authorization": api_key}
            # Stream the file to the server with additional data
            response = requests.post(
                headers=headers,
                url=url,
                files=files,
                data=data,
                stream=True,
            )

            response.raise_for_status()
            for progress_message in response.iter_lines():
                LOGGER.info(progress_message.decode("utf-8"))

            end_time = time.time()  # End timing
            duration = end_time - start_time
            LOGGER.info(f"Finished upload in: {duration:.2f} seconds")
    except requests.exceptions.RequestException as e:
        if response is None:
            LOGGER.error(f"{UPLOAD_CSV_DATASET_ERROR}. Error: {str(e)}")
        else:
            LOGGER.error(
                f"{UPLOAD_CSV_DATASET_ERROR}. Error: {response.status_code}, {response.text}. {str(e)}",
                exc_info=True,
            )
    except Exception as e:
        LOGGER.error(f"{UPLOAD_CSV_DATASET_ERROR}. Error: {str(e)}")


def send_batch_requests(
    session: Session,
    url_endpoint: str,
    api_key: str,
    batch_sending_timeout: int,
    batch: Any,
    error_store: Optional["ErrorStore"] = None,
) -> None:
    response: Union[requests.Response, None] = None
    try:
        headers = make_request_headers(api_key)
        json = {"data": batch}
        response = session.post(
            url_endpoint, headers=headers, json=json, timeout=batch_sending_timeout
        )
        response.raise_for_status()
        # TODO: Process response
    except requests.exceptions.RequestException as e:
        if response is not None:
            error_message = (
                f"{BATCH_SENDING_ERROR}. Error: {response.status_code}, {response.text}"
            )
            LOGGER.error(error_message)

            if error_store is not None:
                error_store.add_error(
                    message=error_message,
                    logger_name="comet_mpm.connection",
                    data_affected=batch,
                    traceback_info=traceback.format_exc(),
                )
        else:
            error_message = f"{BATCH_SENDING_ERROR}. Error: {str(e)}"
            LOGGER.error(error_message)
            if error_store is not None:
                error_store.add_error(
                    message=error_message,
                    logger_name="comet_mpm.connection",
                    data_affected=batch,
                    traceback_info=traceback.format_exc(),
                )

    except Exception as e:
        error_message = f"{BATCH_SENDING_ERROR}. Error: {str(e)}"
        LOGGER.error(error_message)

        if error_store is not None:
            error_store.add_error(
                message=error_message,
                logger_name="comet_mpm.connection",
                data_affected=batch,
                traceback_info=traceback.format_exc(),
            )


def send_is_alive(
    session: Session,
    url_endpoint: str,
    api_key: str,
) -> None:
    """Raise CometMPMBackendException if 500 status code received.
    Raise CometMPMBackendIsNotAvailable if any other error code received.
    According to: https://comet-ml.atlassian.net/browse/CM-9503?focusedCommentId=32968"""
    headers = make_request_headers(api_key)
    response = session.get(url_endpoint, headers=headers)
    is_alive_raise_for_status_code(status_code=response.status_code)


async def send_asyncio_batch_requests(
    session: aiohttp.ClientSession,
    url_endpoint: str,
    api_key: str,
    batch_sending_timeout: int,
    batch: Any,
    error_store: Optional["ErrorStore"] = None,
) -> None:
    try:
        headers = make_request_headers(api_key)
        json = {"data": batch}
        timeout = aiohttp.ClientTimeout(total=batch_sending_timeout)
        response = await session.post(
            url_endpoint, headers=headers, json=json, timeout=timeout
        )
        response.raise_for_status()
    except Exception as e:
        error_message = f"{BATCH_SENDING_ERROR}. Error: {str(e)}"
        LOGGER.error(error_message)

        if error_store is not None:
            error_store.add_error(
                message=error_message,
                logger_name="comet_mpm.connection",
                data_affected=batch,
                traceback_info=traceback.format_exc(),
            )


async def send_asyncio_is_alive(
    session: aiohttp.ClientSession,
    url_endpoint: str,
    api_key: str,
) -> None:
    headers = make_request_headers(api_key)
    response = await session.get(url_endpoint, headers=headers)
    is_alive_raise_for_status_code(status_code=response.status)
