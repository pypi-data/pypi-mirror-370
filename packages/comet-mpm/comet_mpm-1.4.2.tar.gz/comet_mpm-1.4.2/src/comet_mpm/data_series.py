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
import json
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import pandas.api.types as types
from typing_extensions import TypedDict

from ._json.numpy_encoder import NumpyEncoder
from .logging_messages import ERROR_QUANTILES_INVALID_VALUE, ERROR_QUANTILES_LIST_EMPTY

"""This module holds utilities to process data series and data frames"""


class CategoricalSeriesSummary(TypedDict, total=False):
    """The summary of the categorical series"""

    missing_values: int
    count_distribution: Sequence[Tuple[Union[int, float, str, bool], int]]


class NumericalDistributionStats(TypedDict):
    """Represents statistics about numerical distribution in series"""

    quantiles: List[float]
    values: List[float]


class NumericalSeriesSummary(TypedDict, total=False):
    """The summary of the numerical series"""

    missing_values: int
    numerical_distribution: NumericalDistributionStats


class DataFrameDistribution(TypedDict):
    """The summary of the data series distributions in the DataFrame"""

    general_distribution: Dict[
        str, Union[CategoricalSeriesSummary, NumericalSeriesSummary]
    ]


def to_json(
    distribution: Union[
        DataFrameDistribution, NumericalSeriesSummary, CategoricalSeriesSummary
    ]
) -> str:
    """Dumps provided distribution to JSON
    Args:
        distribution: Union[DataFrameDistribution, NumericalSeriesSummary, CategoricalSeriesSummary]
            The distribution to be dumped to JSON
    """
    return json.dumps(distribution, cls=NumpyEncoder)


def categorical_series_summary(
    series: pd.Series, max_distinct_values: int = 100, sort: bool = True
) -> CategoricalSeriesSummary:
    """Computes summary of categorical values from specified series.
    Args:
        series : pandas.core.series.Series
            The series to be evaluated
        max_distinct_values : int, default 100
            The maximal allowed number of distinct values per series.
        sort : bool, default True
            Sort by frequencies.
    Raises:
        TypeError : if provided series has wrong data type. Only int, float, str, bool categorical values are supported.
        ValueError : if there are more than max_distinct_values distinct values per series
    """
    # count all missing values
    missing_values = series.isna().sum()

    # check that maximal distinct values within range (including None)
    unique = series.nunique(dropna=False)
    if unique > max_distinct_values:
        raise ValueError(
            "The series has too many distinct values: %d. Max %d of distinct values are allowed."
            % (unique, max_distinct_values)
        )

    # drop missing values and check that dtype of remaining values are supported
    series = series.dropna(axis="rows")
    if not (
        series.apply(lambda x: types.is_number(x) or types.is_bool(x)).all()
        or types.is_string_dtype(series)
    ):
        raise TypeError("Unsupported series data type: %s" % series.dtype)

    # count all categories
    counts = series.value_counts(dropna=True, sort=sort)
    count_distribution = [(k, v) for k, v in counts.items()]

    return CategoricalSeriesSummary(
        missing_values=missing_values, count_distribution=count_distribution
    )


def numerical_series_summary(
    series: pd.Series, quantiles: List[float]
) -> NumericalSeriesSummary:
    """Computes summary of the provided numerical series
    Args:
        series: pandas.core.series.Series
            The series to be evaluated
        quantiles: List[float]
            The list of quantiles to compute
    Raises:
        TypeError : if provided series has wrong data type. Only numerical data types are supported.
    """
    if not types.is_numeric_dtype(series) or types.is_bool_dtype(series):
        raise TypeError("Unsupported series data type: %s" % series.dtype)

    # check that quantile values are valid
    _validate_quantiles(quantiles)

    # count all missing values
    na_positions = series.isna()
    missing_values = na_positions.sum()

    # calculate statistics if appropriate
    if not na_positions.all():
        values_raw = series.dropna().quantile(quantiles)
        values = [v for i, v in values_raw.items()]
        stats = NumericalDistributionStats(
            quantiles=quantiles,
            values=values,
        )

        return NumericalSeriesSummary(
            missing_values=missing_values, numerical_distribution=stats
        )
    else:
        return NumericalSeriesSummary(missing_values=missing_values)


def _compute_distribution(
    df: pd.DataFrame,
    numerical_features: Optional[List[str]] = None,
    numerical_quantiles: Optional[List[float]] = None,
    categorical_features: Optional[List[str]] = None,
) -> DataFrameDistribution:
    """Computes data series distribution along the columns in the provided data frame.

    Args:
        df: pandas.DataFrame
            The DataFrame to be evaluated.
        numerical_features: Optional[List[str]]
            The list with column names to calculate numerical distribution summary
        numerical_quantiles: Optional[List[float]]
            The list of quantiles to be calculated from numerical features. It must be present if numerical_features
            columns are present.
        categorical_features: Optional[List[str]]
            The list with column names to calculate categorical distribution summary
    Raises:
        TypeError: if when summary requested for specific column with wrong data type, e.g. numerical for column
            holding string data type series.
        ValueError: if requested summary for the column which doesn't exists in the data frame or if numerical_quantiles
            has wrong values. For details see: numerical_series_summary()
    """
    # check that all requested features are present in the data frame
    cols: List[str] = []
    if numerical_features is not None:
        cols = cols + numerical_features
        _validate_quantiles(numerical_quantiles)
    if categorical_features is not None:
        cols = cols + categorical_features

    for col in cols:
        if col not in df.columns:
            raise ValueError(
                "The requested feature column: %s is not found in the DataFrame" % col
            )

    # check that all requested features exactly match the number of feature columns in the data frame
    if len(cols) != len(df.columns):
        raise ValueError(
            "The DataFrame has more feature columns than number of features requested"
        )

    distributions: Dict[
        str, Union[CategoricalSeriesSummary, NumericalSeriesSummary]
    ] = {}
    # calculate numerical distributions
    if numerical_features is not None:
        assert numerical_quantiles is not None  # it must not be None at this stage
        for feature in numerical_features:
            distributions[feature] = numerical_series_summary(
                df[feature], quantiles=numerical_quantiles
            )

    # calculate categorical distributions
    if categorical_features is not None:
        for feature in categorical_features:
            distributions[feature] = categorical_series_summary(df[feature])

    return DataFrameDistribution(general_distribution=distributions)


def _validate_quantiles(quantiles: Optional[List[float]]) -> None:
    """Validates if provides list of quantile values is correct"""
    if quantiles is None or len(quantiles) == 0:
        raise ValueError(ERROR_QUANTILES_LIST_EMPTY)
    arr = np.array(quantiles)
    min_quantile, max_quantile = np.amin(arr), np.amax(arr)
    if min_quantile < 0 or max_quantile > 1:
        raise ValueError(ERROR_QUANTILES_INVALID_VALUE % (min_quantile, max_quantile))
