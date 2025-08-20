# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed
#  without the express permission of Comet ML Inc.
# *******************************************************
import logging
from threading import Lock
from time import monotonic
from typing import Any, Dict, List, Tuple

from comet_mpm.events.label_event import LabelsEvent
from comet_mpm.events.prediction_event import PredictionEvent
from comet_mpm.logging_messages import UNEXPECTED_EVENT_TYPE

LOGGER = logging.getLogger(__name__)


class Batch(object):
    """
    The Batch object contains a list of anything and manage the size of the batch, isolating the
    logic about the max size and max time for a batch
    """

    def __init__(self, max_batch_size: int, max_batch_time: int) -> None:
        self.batch: List[Any] = []
        self.last_time_created = monotonic()
        self.critical = False

        self.max_batch_size = max_batch_size
        self.max_batch_time = max_batch_time

    def append(self, batch_item: Any) -> None:
        if len(self.batch) == 0:
            self.last_time_created = monotonic()

        self.batch.append(batch_item)

    def __len__(self) -> int:
        return len(self.batch)

    def should_be_uploaded(self, flush: bool) -> bool:
        """Check if the current batch should be uploaded according to both max_batch_size and
        max_batch_item. If the batch is empty. If flush is True, always return True except if the batch is
        empty.
        """
        if len(self.batch) == 0:
            return False

        if flush:
            return flush

        duration_since_last_created = monotonic() - self.last_time_created

        too_many_items = len(self.batch) >= self.max_batch_size
        too_old_batch = duration_since_last_created >= self.max_batch_time

        return too_many_items or too_old_batch

    def clear(self) -> None:
        self.batch = []

    def get_and_clear(self) -> List[Any]:
        batch = self.batch
        self.batch = []
        return batch


class ThreadSafeBatch(Batch):
    """
    The Batch object contains a list of anything and manage the size of the batch, isolating the
    logic about the max size and max time for a batch
    """

    def __init__(self, max_batch_size: int, max_batch_time: int) -> None:
        super().__init__(max_batch_size=max_batch_size, max_batch_time=max_batch_time)
        self.lock = Lock()

    def append(self, batch_item: Any) -> None:
        with self.lock:
            return super().append(batch_item=batch_item)

    def __len__(self) -> int:
        with self.lock:
            return super().__len__()

    def should_be_uploaded(self, flush: bool) -> bool:
        with self.lock:
            return super().should_be_uploaded(flush=flush)

    def clear(self) -> None:
        with self.lock:
            return super().clear()

    def get_and_clear(self) -> List[Any]:
        with self.lock:
            return super().get_and_clear()


def split_batch(
    batch_to_send: List[Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    predictions_batch: List[Dict[str, Any]] = []
    labels_batch: List[Dict[str, Any]] = []
    for event in batch_to_send:
        event_dict = event.create_event_dict()
        if isinstance(event, PredictionEvent):
            predictions_batch.append(event_dict)
        elif isinstance(event, LabelsEvent):
            labels_batch.append(event_dict)
        else:
            LOGGER.error(UNEXPECTED_EVENT_TYPE, event)
    return predictions_batch, labels_batch
