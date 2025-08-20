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

import asyncio
import logging
import traceback
from typing import Any, Optional, Tuple

import aiohttp

from .._logging import ErrorStore
from ..batch_utils import Batch, split_batch
from ..connection import send_asyncio_batch_requests, send_asyncio_is_alive
from ..exceptions import AsyncioSenderNoConnected
from ..logging_messages import (
    ASYNCIO_SENDER_HARD_SHUTDOWN,
    BATCH_SENDING_EXCEPTION,
    MPM_ALREADY_CLOSED_LOG_DATA_WARNING,
)
from ..server_address import ServerAddress
from ..utils import async_wait_for_done
from .base import CLOSE_MESSAGE, BaseSender

LOGGER = logging.getLogger(__name__)


def get_asyncio_sender(
    api_key: str,
    server_address: ServerAddress,
    max_batch_size: int,
    max_batch_time: int,
    batch_sending_timeout: int,
    error_store: Optional[ErrorStore] = None,
) -> "AsyncioSender":
    sender = AsyncioSender(
        api_key=api_key,
        server_address=server_address,
        max_batch_size=max_batch_size,
        max_batch_time=max_batch_time,
        batch_sending_timeout=batch_sending_timeout,
        error_store=error_store,
    )

    return sender


class AsyncioBackgroundSender:
    def __init__(
        self,
        api_key: str,
        server_address: ServerAddress,
        queue: "asyncio.Queue[Any]",
        max_batch_size: int,
        max_batch_time: int,
        batch_sending_timeout: int,
        error_store: Optional[ErrorStore] = None,
    ):
        """A background coroutine that reads from the queue, add the items to the batch and sends
        them whenever the batch is ready to be sent. Can only be created only when an event loop is running.
        """
        self.api_key = api_key
        self.server_address = server_address
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.queue: "asyncio.Queue[Any]" = queue
        self.max_batch_time = max_batch_time
        self.batch = Batch(max_batch_size, self.max_batch_time)
        self.batch_sending_timeout = batch_sending_timeout
        self.error_store = error_store

        self.stop_processing = False

        # Pre-compute URLs
        self.batch_endpoint = self.server_address.batch_endpoint_url()
        self.labels_endpoint = self.server_address.batch_endpoint_url()

    async def run(self) -> None:
        while True:
            stop = await self._loop()

            if stop is True:
                break

        # We force stop the processing of the queue
        await self._check_batch_sending()
        return

    async def _loop(self) -> bool:
        try:
            data = await asyncio.wait_for(self.queue.get(), timeout=self.max_batch_time)
            if data is None:
                return False

            if data is CLOSE_MESSAGE:
                self.stop_processing = True
                return True

            self.batch.append(data)
        except asyncio.TimeoutError:
            pass

        await self._check_batch_sending()

        return False

    async def _send_batch(self, batch_to_send: Any) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                predictions_batch, labels_batch = split_batch(batch_to_send)

                if predictions_batch:
                    await send_asyncio_batch_requests(
                        session=session,
                        url_endpoint=self.batch_endpoint,
                        api_key=self.api_key,
                        batch_sending_timeout=self.batch_sending_timeout,
                        batch=predictions_batch,
                        error_store=self.error_store,
                    )

                if labels_batch:
                    await send_asyncio_batch_requests(
                        session=session,
                        url_endpoint=self.labels_endpoint,
                        api_key=self.api_key,
                        batch_sending_timeout=self.batch_sending_timeout,
                        batch=labels_batch,
                        error_store=self.error_store,
                    )
        except Exception as e:
            # Log to console for immediate user visibility
            error_message = f"{BATCH_SENDING_EXCEPTION}. Error: {str(e)}"
            LOGGER.error(error_message)

            # Store in error store for programmatic access
            if self.error_store is not None:
                self.error_store.add_error(
                    message=error_message,
                    logger_name="comet_mpm.sender.asyncio_sender",
                    data_affected=batch_to_send,
                    traceback_info=traceback.format_exc(),
                )

    async def _check_batch_sending(self) -> None:
        # This should only be called by the background sender coroutine, if not the batch could
        # become corrupted as its access not protected by a lock
        try:
            if self.batch.should_be_uploaded(self.stop_processing):
                batch_to_send = self.batch.get_and_clear()

                predictions_batch, labels_batch = split_batch(batch_to_send)

                if predictions_batch:
                    await send_asyncio_batch_requests(
                        session=self.session,
                        url_endpoint=self.batch_endpoint,
                        api_key=self.api_key,
                        batch_sending_timeout=self.batch_sending_timeout,
                        batch=predictions_batch,
                        error_store=self.error_store,
                    )

                if labels_batch:
                    await send_asyncio_batch_requests(
                        session=self.session,
                        url_endpoint=self.labels_endpoint,
                        api_key=self.api_key,
                        batch_sending_timeout=self.batch_sending_timeout,
                        batch=labels_batch,
                        error_store=self.error_store,
                    )
        except Exception as e:
            # Log to console for immediate user visibility
            error_message = f"{BATCH_SENDING_EXCEPTION}. Error: {str(e)}"
            LOGGER.error(error_message)

            # Store in error store for programmatic access
            if self.error_store is not None:
                self.error_store.add_error(
                    message=error_message,
                    logger_name="comet_mpm.sender.asyncio_sender",
                    data_affected=batch_to_send,
                    traceback_info=traceback.format_exc(),
                )

    def close(self, timeout: int = 10) -> None:
        """Force the AsyncioBackgroundSender to stop processing messages"""
        #
        self.stop_processing = True

        async def flush_queue() -> None:
            while True:
                try:
                    data = self.queue.get_nowait()
                    if data is not None and data is not CLOSE_MESSAGE:
                        self.batch.append(data)
                except asyncio.QueueEmpty:
                    break

            batch = self.batch.get_and_clear()
            await asyncio.wait_for(self._send_batch(batch), timeout)
            await self.session.close()

        asyncio.run(flush_queue())


class AsyncioSender(BaseSender):
    def __init__(
        self,
        api_key: str,
        server_address: ServerAddress,
        max_batch_size: int,
        max_batch_time: int,
        batch_sending_timeout: int,
        error_store: Optional[ErrorStore] = None,
    ) -> None:
        self.sender_queue: Optional["asyncio.Queue[Any]"] = None
        # We need to wait for the asyncio event loop to be created
        self.background_sender: Optional[AsyncioBackgroundSender] = None
        self.background_task: Optional[asyncio.Task[None]] = None
        self.lock: Optional[asyncio.Lock] = None
        self.drain = False

        self.api_key = api_key
        self.server_address = server_address
        self.max_batch_time = max_batch_time
        self.max_batch_size = max_batch_size
        self.batch_sending_timeout = batch_sending_timeout
        self.error_store = error_store

    async def connect(self) -> None:
        if self.sender_queue is None:
            sender_queue: "asyncio.Queue[Any]" = asyncio.Queue()
            self.sender_queue = sender_queue
            self.background_sender = AsyncioBackgroundSender(
                api_key=self.api_key,
                server_address=self.server_address,
                queue=self.sender_queue,
                max_batch_size=self.max_batch_size,
                max_batch_time=self.max_batch_time,
                batch_sending_timeout=self.batch_sending_timeout,
                error_store=self.error_store,
            )
            self.background_sender.queue = self.sender_queue

        if self.background_task is None:
            assert self.background_sender is not None
            self.background_task = asyncio.create_task(self.background_sender.run())

        if self.lock is None:
            self.lock = asyncio.Lock()

        await self.ping_backend()

    async def ping_backend(self) -> None:
        assert self.background_sender is not None
        await send_asyncio_is_alive(
            session=self.background_sender.session,
            url_endpoint=self.server_address.is_alive_endpoint_url(),
            api_key=self.api_key,
        )

    def _check_connected(self) -> Tuple[asyncio.Lock, "asyncio.Queue[Any]"]:
        if self.lock is None or self.sender_queue is None:
            raise AsyncioSenderNoConnected()

        return self.lock, self.sender_queue

    async def put(self, item: Any) -> None:
        lock, queue = self._check_connected()
        async with lock:
            if not self.drain:
                await queue.put(item)
            else:
                LOGGER.error(MPM_ALREADY_CLOSED_LOG_DATA_WARNING)
                # Store warning for programmatic access
                if self.error_store is not None:
                    self.error_store.add_error(
                        message=MPM_ALREADY_CLOSED_LOG_DATA_WARNING,
                        logger_name="comet_mpm.sender.asyncio_sender",
                        data_affected=[item.create_event_dict()],
                        traceback_info=None,
                    )

    def close(self, timeout: int = 10) -> None:
        """Called during atexit but users should call join manually. In last resort, synchronously
        deque items and send it by recreating an asyncio Event Loop
        """
        if self.drain is True:
            return None
        else:
            self.drain = True

            need_to_clean = False

            if self.sender_queue is not None and self.sender_queue.qsize() > 0:
                need_to_clean = True

            if (
                self.background_sender is not None
                and len(self.background_sender.batch) > 0
            ):
                need_to_clean = True

            if need_to_clean:
                LOGGER.warning(
                    ASYNCIO_SENDER_HARD_SHUTDOWN
                )  # TODO: Add link to documentation page
                self.drain = True

                # If the sender_queue is not None, the background sender shouldn't be None either
                assert self.background_sender is not None
                self.background_sender.close(timeout)

    async def join(self, timeout: int) -> None:
        """Inform the background sender to stops processing after receiving the sentinel object and
        wait for the background sender to stop
        """
        try:
            lock, queue = self._check_connected()
        except AsyncioSenderNoConnected:
            # The AsyncioSender was not properly initialized, ignore
            return

        async with lock:
            if self.drain is False:
                self.drain = True

                queue.put_nowait(CLOSE_MESSAGE)

                if self.background_task is not None:

                    def is_task_done() -> bool:
                        if (
                            self.background_sender is not None
                            and self.background_task is not None
                        ):
                            return self.background_task.done()
                        return True

                    async def show_progress() -> None:
                        remaining_events = queue.qsize() if queue else 0
                        batch_size = (
                            len(self.background_sender.batch)
                            if self.background_sender
                            else 0
                        )
                        total_remaining = remaining_events + batch_size
                        LOGGER.info(
                            f"Uploading MPM events, {total_remaining} events remaining."
                        )

                    # Adjust sleep_time and progress callback based on timeout
                    # Always use responsive checking, but only show progress for longer timeouts
                    sleep_time = min(
                        10, max(timeout / 3, 1)
                    )  # Responsive checking for all timeouts
                    progress_callback = (
                        show_progress if timeout >= 15 else None
                    )  # Progress only for long timeouts

                    await async_wait_for_done(
                        check_function=is_task_done,
                        timeout=timeout,
                        progress_callback=progress_callback,
                        sleep_time=sleep_time,
                    )
