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

from typing import Dict, Optional, Tuple


def get_request_data(
    base_url: Optional[str],
    workspace_name: str,
    model_name: str,
    model_version: str,
    dataset_type: str,
    dataset_name: Optional[str] = None,
    na_values: Optional[str] = None,
    keep_default_na_values: Optional[str] = None,
) -> Tuple[Dict[str, str], str]:
    data = {
        "workspaceName": workspace_name,
        "modelName": model_name,
        "modelVersion": model_version,
    }
    url = set_model_name_and_get_url(base_url, data, dataset_type, dataset_name)
    if na_values is not None:
        data["NAValues"] = na_values
    if keep_default_na_values is not None:
        data["keepDefaultNAValues"] = keep_default_na_values
    return data, url


def set_model_name_and_get_url(
    base_url: Optional[str],
    data: Dict[str, str],
    dataset_type: str,
    dataset_name: Optional[str] = None,
) -> str:
    if dataset_type == "TRAINING_EVENTS":
        if dataset_name is None:
            raise ValueError(
                "dataset_name must be set when dataset_type is 'TRAINING_EVENTS'."
            )
        data["datasetName"] = dataset_name
        url = f"{base_url}v2/dataset/events/csv"
    elif dataset_type == "EVENTS":
        if dataset_name is not None:
            data["modelName"] = dataset_name
        url = f"{base_url}v2/data/events/csv"
    elif dataset_type == "LATE_LABELS":
        if dataset_name is not None:
            data["modelName"] = dataset_name
        url = f"{base_url}v2/data/labels/csv"
    else:
        raise ValueError(
            "Invalid dataset_type. Allowed values are 'EVENTS', 'LATE_LABELS' or 'TRAINING_EVENTS'."
        )
    return url
