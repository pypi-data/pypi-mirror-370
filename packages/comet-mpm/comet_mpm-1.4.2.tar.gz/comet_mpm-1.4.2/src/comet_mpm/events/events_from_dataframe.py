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
from typing import Any, Dict, List, Optional

from .. import constants, logging_messages
from .prediction_event import PredictionEvent

LOGGER = logging.getLogger(__name__)


def generate(  # type: ignore[no-untyped-def]
    workspace: str,
    model_name: str,
    model_version: str,
    dataframe,
    prediction_id_column: str,
    feature_columns: Optional[List[str]] = None,
    output_features_columns: Optional[List[str]] = None,
    output_value_column: Optional[str] = None,
    output_probability_column: Optional[str] = None,
    labels_columns: Optional[List[str]] = None,
    timestamp_column: Optional[str] = None,
):
    return (
        _event(
            workspace=workspace,
            model_name=model_name,
            model_version=model_version,
            row=row,
            prediction_id_column=prediction_id_column,
            feature_columns=feature_columns,
            output_features_columns=output_features_columns,
            output_value_column=output_value_column,
            output_probability_column=output_probability_column,
            labels_columns=labels_columns,
            timestamp_column=timestamp_column,
        )
        for row in dataframe.to_dict(orient="records")
    )


def _event(  # type: ignore[no-untyped-def]
    workspace: str,
    model_name: str,
    model_version: str,
    row,
    prediction_id_column,
    feature_columns,
    output_features_columns,
    output_value_column,
    output_probability_column,
    labels_columns: Optional[List[str]] = None,
    timestamp_column: Optional[str] = None,
) -> PredictionEvent:
    prediction_id = str(row[prediction_id_column])
    input_features = None
    if feature_columns is not None:
        input_features = {key: row[key] for key in feature_columns}

    output_value = None
    if output_value_column is not None:
        output_value = row[output_value_column]

    output_probability = None
    if output_probability_column is not None:
        output_probability = row[output_probability_column]

    output_features = None
    if output_features_columns is not None:
        output_features = {key: row[key] for key in output_features_columns}
    output_features = _handle_dataframe_output_features(
        output_value, output_probability, output_features
    )

    labels = None
    if labels_columns is not None:
        labels = {key: row[key] for key in labels_columns}

    timestamp = None
    if timestamp_column is not None:
        timestamp = row[timestamp_column]

    return PredictionEvent(
        workspace=workspace,
        model_name=model_name,
        model_version=model_version,
        prediction_id=prediction_id,
        input_features=input_features,
        output_features=output_features,
        labels=labels,
        timestamp=timestamp,
    )


def _handle_dataframe_output_features(
    output_value: Any,
    output_probability: Any,
    output_features: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    event_output_features: Optional[Dict[str, Any]]

    if (
        output_value is not None or output_probability is not None
    ) and output_features is None:
        LOGGER.warning(
            logging_messages.DEPRECATED_DATAFRAME_OUTPUT_VALUE_AND_PROBABILITY
        )
        event_output_features = {}
        if output_value is not None:
            event_output_features[constants.EVENT_PREDICTION_VALUE] = output_value

        if output_probability is not None:
            event_output_features[
                constants.EVENT_PREDICTION_PROBABILITY
            ] = output_probability
    elif (
        output_value is not None and output_probability is not None
    ) and output_features is not None:
        LOGGER.warning(
            logging_messages.DEPRECATED_DATAFRAME_OUTPUT_VALUE_AND_PROBABILITY
        )

        event_output_features = {
            constants.EVENT_PREDICTION_VALUE: output_value,
            constants.EVENT_PREDICTION_PROBABILITY: output_probability,
        }
        for key in output_features:
            event_output_features[key] = output_features[key]
    else:
        event_output_features = output_features

    return event_output_features
