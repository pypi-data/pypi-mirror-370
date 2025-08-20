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
import queue
from threading import Lock, Thread
from typing import Any, Optional, Tuple

from .._logging import ErrorStore
from ..batch_utils import ThreadSafeBatch, split_batch
from ..connection import (
    get_comet_http_session,
    get_retry_strategy,
    send_batch_requests,
    send_is_alive,
)
from ..logging_messages import (
    BATCH_SENDING_EXCEPTION,
    MPM_ALREADY_CLOSED_LOG_DATA_WARNING,
)
from ..server_address import ServerAddress
from ..utils import wait_for_done
from .base import CLOSE_MESSAGE, BaseSender

LOGGER = logging.getLogger(__name__)


class ThreadBackgroundSender:
    def __init__(
        self,
        api_key: str,
        server_address: ServerAddress,
        sender_queue: "queue.Queue[Any]",
        max_batch_size: int,
        max_batch_time: int,
        batch_sending_timeout: int,
        error_store: Optional[ErrorStore] = None,
    ):
        self.api_key = api_key
        self.server_address = server_address
        self.sender_queue = sender_queue
        self.max_batch_time = max_batch_time
        self.batch = ThreadSafeBatch(max_batch_size, self.max_batch_time)
        self.session = get_comet_http_session(
            api_key=self.api_key, retry_strategy=get_retry_strategy()
        )
        self.batch_sending_timeout = batch_sending_timeout
        self.error_store = error_store

        self.stop_processing = False

        # Pre-compute URLs
        self.batch_endpoint = self.server_address.batch_endpoint_url()
        self.labels_endpoint = self.server_address.labels_endpoint_url()

    def run(self) -> None:
        """This is meant to be run in an independent Thread"""
        while self.stop_processing is False:
            stop = self._loop()

            if stop is True:
                break

        # We force stop the processing of the queue
        self._check_batch_sending()
        return

    def _loop(self) -> bool:
        try:
            data = self.sender_queue.get(block=True, timeout=self.max_batch_time)
            if data is None:
                return False

            if data is CLOSE_MESSAGE:
                self.stop_processing = True
                return True

            self.batch.append(data)
        except queue.Empty:
            pass

        self._check_batch_sending()

        return False

    def _check_batch_sending(self) -> None:
        try:
            if self.batch.should_be_uploaded(self.stop_processing):
                batch_to_send = self.batch.get_and_clear()

                predictions_batch, labels_batch = split_batch(batch_to_send)

                if predictions_batch:
                    send_batch_requests(
                        self.session,
                        self.batch_endpoint,
                        api_key=self.api_key,
                        batch=predictions_batch,
                        batch_sending_timeout=self.batch_sending_timeout,
                        error_store=self.error_store,
                    )

                if labels_batch:
                    send_batch_requests(
                        self.session,
                        self.labels_endpoint,
                        api_key=self.api_key,
                        batch=labels_batch,
                        batch_sending_timeout=self.batch_sending_timeout,
                        error_store=self.error_store,
                    )
        except Exception as e:
            # Log to console for immediate user visibility
            error_message = f"{BATCH_SENDING_EXCEPTION}. Error: {str(e)}"
            LOGGER.error(error_message)

            # Store in error store for programmatic access
            if self.error_store is not None:
                import traceback

                self.error_store.add_error(
                    message=error_message,
                    logger_name="comet_mpm.sender.thread_sender",
                    data_affected=None,
                    traceback_info=traceback.format_exc(),
                )

    def close(self) -> None:
        """For the BackgroundSender to stop processing messages"""
        self.stop_processing = True
        # This shouldn't happen outside of the background sender thread
        self._check_batch_sending()

        self.session.close()


class ThreadSender(BaseSender):
    def __init__(
        self,
        api_key: str,
        server_address: ServerAddress,
        max_batch_size: int,
        max_batch_time: int,
        batch_sending_timeout: int,
        error_store: Optional[ErrorStore] = None,
    ) -> None:
        self.lock = Lock()
        self.sender_queue: Optional["queue.Queue[Any]"] = None
        self.background_sender: Optional[ThreadBackgroundSender] = None
        self.background_thread: Optional[Thread] = None
        self.drain = False

        self.api_key = api_key
        self.server_address = server_address
        self.max_batch_time = max_batch_time
        self.max_batch_size = max_batch_size
        self.batch_sending_timeout = batch_sending_timeout
        self.error_store = error_store

    def _prepare(self) -> "queue.Queue[Any]":
        """We need to create the background thread on the first request to support application
        pre-loading.
        """
        if self.sender_queue is None:
            sender_queue: "queue.Queue[Any]" = queue.Queue()
            self.sender_queue = sender_queue
            self.background_sender = ThreadBackgroundSender(
                api_key=self.api_key,
                server_address=self.server_address,
                sender_queue=self.sender_queue,
                max_batch_size=self.max_batch_size,
                max_batch_time=self.max_batch_time,
                batch_sending_timeout=self.batch_sending_timeout,
                error_store=self.error_store,
            )

        if self.background_thread is None:
            assert self.background_sender is not None
            self.background_thread = Thread(
                target=self.background_sender.run, daemon=True, name="ThreadSender"
            )
            self.background_thread.start()

        assert self.sender_queue is not None
        return self.sender_queue

    def put(self, item: Any) -> None:
        with self.lock:
            if not self.drain:

                if self.sender_queue is None:
                    sender_queue = self._prepare()
                else:
                    sender_queue = self.sender_queue

                sender_queue.put(item)
            else:
                LOGGER.error(MPM_ALREADY_CLOSED_LOG_DATA_WARNING)
                # Store warning for programmatic access
                if self.error_store is not None:
                    self.error_store.add_error(
                        message=MPM_ALREADY_CLOSED_LOG_DATA_WARNING,
                        logger_name="comet_mpm.sender.thread_sender",
                        data_affected=[item.create_event_dict()],
                        traceback_info=None,
                    )

    def close(self, timeout: int = 10) -> None:
        with self.lock:
            self.drain = True

        if self.sender_queue is not None:
            self.sender_queue.put(CLOSE_MESSAGE)

        if self.background_thread is not None:

            def is_thread_done() -> bool:
                if (
                    self.background_sender is not None
                    and self.background_thread is not None
                ):
                    return not self.background_thread.is_alive()
                return True

            def show_progress() -> None:
                remaining_events = self.sender_queue.qsize() if self.sender_queue else 0
                LOGGER.info(
                    f"Uploading MPM events, {remaining_events} events remaining."
                )

            # Adjust sleep_time and progress callback based on timeout
            # Always use responsive checking, but only show progress for longer timeouts
            sleep_time = min(
                10, max(timeout / 3, 1)
            )  # Responsive checking for all timeouts
            progress_callback = (
                show_progress if timeout >= 15 else None
            )  # Progress only for long timeouts

            wait_for_done(
                check_function=is_thread_done,
                timeout=timeout,
                progress_callback=progress_callback,
                sleep_time=sleep_time,
            )

        if self.background_sender is not None:
            self.background_sender.close()

    def join(self, timeout: int) -> None:
        """There is no easy way to plug a shutdown callback with Flask, the "normal" cleaning
        process for Flask is to use the close method"""
        return None

    def connect(self) -> None:
        """There is no easy way nor need to plug a startup callback as we can create everything and
        do the handshake during Python import"""
        self.ping_backend()

    def ping_backend(self) -> None:
        if self.background_sender is None:
            session = get_comet_http_session(
                api_key=self.api_key, retry_strategy=get_retry_strategy()
            )
        else:
            session = self.background_sender.session
        send_is_alive(
            session=session,
            url_endpoint=self.server_address.is_alive_endpoint_url(),
            api_key=self.api_key,
        )


def get_thread_sender(
    api_key: str,
    server_address: ServerAddress,
    max_batch_size: int,
    max_batch_time: int,
    batch_sending_timeout: int,
    error_store: Optional[ErrorStore] = None,
) -> "ThreadSender":
    sender = ThreadSender(
        api_key=api_key,
        server_address=server_address,
        max_batch_size=max_batch_size,
        max_batch_time=max_batch_time,
        batch_sending_timeout=batch_sending_timeout,
        error_store=error_store,
    )

    return sender


def _get_thread_background_sender(
    api_key: str,
    server_address: ServerAddress,
    max_batch_size: int,
    max_batch_time: int,
    batch_sending_timeout: int,
) -> Tuple["queue.Queue[Any]", "ThreadBackgroundSender"]:
    sender_queue: queue.Queue[Any] = queue.Queue()
    background_sender = ThreadBackgroundSender(
        api_key=api_key,
        server_address=server_address,
        sender_queue=sender_queue,
        max_batch_size=max_batch_size,
        max_batch_time=max_batch_time,
        batch_sending_timeout=batch_sending_timeout,
    )

    return sender_queue, background_sender
