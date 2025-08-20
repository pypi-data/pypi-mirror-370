# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021-2023 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
import abc
import calendar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from comet_mpm.constants import (
    EVENT_MODEL_NAME,
    EVENT_MODEL_VERSION,
    EVENT_PREDICTION_ID,
    EVENT_TIMESTAMP,
    EVENT_WORKSPACE_NAME,
)


class BaseEvent(abc.ABC):
    def __init__(
        self,
        workspace: str,
        model_name: str,
        model_version: str,
        prediction_id: str,
        timestamp: Optional[float] = None,
    ):
        self.workspace = workspace
        self.model_name = model_name
        self.model_version = model_version
        self.prediction_id = prediction_id

        self.timestamp = local_timestamp(timestamp)

    def create_event_dict(self) -> Dict[str, Any]:
        base_dict = {
            EVENT_MODEL_NAME: self.model_name,
            EVENT_MODEL_VERSION: self.model_version,
            EVENT_WORKSPACE_NAME: self.workspace,
            EVENT_PREDICTION_ID: self.prediction_id,
            EVENT_TIMESTAMP: self.timestamp,
        }
        base_dict.update(self._get_event_dict())
        return base_dict

    @abc.abstractmethod
    def _get_event_dict(self) -> Dict[str, Any]:
        ...


def local_timestamp(timestamp: Optional[float] = None) -> int:
    """Return a timestamp in a format expected by the backend (milliseconds)"""
    if timestamp is None:
        now = datetime.now(timezone.utc)
        timestamp_in_seconds = calendar.timegm(now.timetuple()) + (
            now.microsecond / 1e6
        )
    else:
        timestamp_in_seconds = timestamp
    timestamp_in_milliseconds = int(timestamp_in_seconds * 1000)
    return timestamp_in_milliseconds
