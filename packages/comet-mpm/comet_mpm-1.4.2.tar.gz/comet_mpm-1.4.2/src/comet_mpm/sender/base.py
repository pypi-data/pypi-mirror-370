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

import logging
from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Awaitable, Optional

if TYPE_CHECKING:
    import asyncio
    import queue

from urllib.parse import urljoin

LOGGER = logging.getLogger(__name__)


def batch_endpoint_url(server_address: str) -> str:
    # TODO: Check that server_address finishes with a "/"
    return urljoin(server_address, "events/batch")


def labels_endpoint_url(server_address: str) -> str:
    return urljoin(server_address, "labels/batch")


CLOSE_MESSAGE = object()


class BaseSender(metaclass=ABCMeta):
    # Add sender_queue attribute to satisfy mypy
    sender_queue: Optional["queue.Queue[Any] | asyncio.Queue[Any]"] = None

    def ping_backend(self) -> Optional[Awaitable[Any]]:
        """Allows to check backend status.
        Raise CometMPMBackendException if backend is not healthy.
        Raise CometMPMBackendIsNotAvailable if MPM backend is not installed."""
        ...  # pragma: no cover

    def connect(self) -> Any:
        ...  # pragma: no cover

    def put(self, item: Any) -> Optional[Awaitable[None]]:
        ...  # pragma: no cover

    def close(self, timeout: int) -> None:
        ...  # pragma: no cover

    def join(self, timeout: int) -> Optional[Awaitable[None]]:
        ...  # pragma: no cover
