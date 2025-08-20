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

from typing import Optional


def remove_prefix(name: str) -> str:
    """
    Remove the prefix from a prefixed name.

    Args:
        name: A string with a prefix separated by underscore (e.g., "feature_age")

    Returns:
        str: The name without the prefix (e.g., "age")

    Raises:
        ValueError: If the name doesn't contain an underscore
    """
    prefix, rest = name.split("_", 1)
    return rest


def source_type_to_prefix(source_type: Optional[str]) -> str:
    """
    Convert a source type to its corresponding prefix.

    Args:
        source_type: The source type string or None

    Returns:
        str: The corresponding prefix ("label", "prediction", or "feature")

    Raises:
        Exception: If the source type is unknown
    """
    if source_type is None:
        return "label"
    elif source_type == "model_output_features":
        return "prediction"
    elif source_type == "model_input_features":
        return "feature"
    else:
        raise ValueError("unknown source type: %r" % source_type)
