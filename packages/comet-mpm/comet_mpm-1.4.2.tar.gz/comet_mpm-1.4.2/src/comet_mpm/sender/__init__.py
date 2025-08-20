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

"""
Event sending utilities for Comet MPM.

This package provides sender classes for asynchronously sending events
to the Comet MPM backend, including both thread-based and asyncio-based implementations.
"""

import logging
import sys
from typing import TYPE_CHECKING, Optional

from ..logging_messages import GEVENT_NOT_SUPPORTED
from ..server_address import ServerAddress
from .asyncio_sender import get_asyncio_sender
from .base import BaseSender
from .thread_sender import get_thread_sender

if TYPE_CHECKING:
    from .._logging import ErrorStore

LOGGER = logging.getLogger(__name__)


def get_sender(
    api_key: str,
    server_address: ServerAddress,
    max_batch_size: int,
    max_batch_time: int,
    batch_sending_timeout: int,
    asyncio: bool = False,
    error_store: Optional["ErrorStore"] = None,
) -> "BaseSender":

    if "gevent" in sys.modules:
        import gevent.monkey

        # Inspired by gevent.monkey.is_anything_patched
        is_gevent_active = bool(gevent.monkey.saved)

        if is_gevent_active:
            LOGGER.warning(GEVENT_NOT_SUPPORTED)

    if asyncio is True:
        return get_asyncio_sender(
            api_key=api_key,
            server_address=server_address,
            max_batch_size=max_batch_size,
            max_batch_time=max_batch_time,
            batch_sending_timeout=batch_sending_timeout,
            error_store=error_store,
        )
    else:
        return get_thread_sender(
            api_key=api_key,
            server_address=server_address,
            max_batch_size=max_batch_size,
            max_batch_time=max_batch_time,
            batch_sending_timeout=batch_sending_timeout,
            error_store=error_store,
        )
