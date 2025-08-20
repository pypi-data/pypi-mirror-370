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

from typing import Any, Dict, Optional

from comet_mpm.constants import LABELS
from comet_mpm.events.base_event import BaseEvent


class LabelsEvent(BaseEvent):
    """
    This class represents a single ground truth label.
    Args:
        workspace: The project workspace.
        model_name: The name of model
        model_version: The version of model
        prediction_id: The unique prediction ID, could be provided by the
            framework, you or a random unique value could be provided like
            str(uuid4())
        label: the ground truth value for a prediction
    """

    def __init__(
        self,
        workspace: str,
        model_name: str,
        model_version: str,
        prediction_id: str,
        labels: Dict[str, Any],
        timestamp: Optional[float] = None,
    ):
        super(LabelsEvent, self).__init__(
            workspace=workspace,
            model_name=model_name,
            model_version=model_version,
            prediction_id=prediction_id,
            timestamp=timestamp,
        )
        self.labels = labels

    def _get_event_dict(self) -> Dict[str, Any]:
        return {LABELS: self.labels}
