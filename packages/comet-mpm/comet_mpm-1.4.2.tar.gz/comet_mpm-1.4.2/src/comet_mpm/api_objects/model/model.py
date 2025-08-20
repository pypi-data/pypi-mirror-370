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

from typing import Any, Dict, List, Optional

import pandas as pd

from ...config import get_config
from ..rest_client import Client
from .dataframe_converters import (
    custom_metrics_to_dataframe,
    feature_category_distribution_to_dataframe,
    feature_density_to_dataframe,
    feature_drift_to_dataframe,
    feature_percentiles_to_dataframe,
)


def convert_config_filters_to_predicates(filters: List[str]) -> List[Dict[str, str]]:
    """
    Convert a list of filter strings to predicate format.

    Args:
        filters: List of filter strings to convert

    Returns:
        List[Dict[str, str]]: List of predicate dictionaries with "key" and "query" fields
    """
    return [{"key": filter, "query": filter} for filter in filters]


class Model:
    """
    A model instance for interacting with Comet MPM model-specific operations.

    This class provides high-level methods for querying model predictions, metrics,
    and feature analysis. It can be configured with panel options for default
    parameter values.

    Args:
        client: The Comet MPM client instance
        model_id: The ID of the model to work with
    """

    def __init__(
        self,
        client: Client,
        model_id: str,
    ):
        """
        Initialize a Model instance.

        Args:
            client: The Comet MPM client instance for making API calls
            model_id: The ID of the model to work with
            _config: Configuration strategy instance
        """
        self._client = client
        self.model_id = model_id
        self._config = get_config()

    def get_details(self) -> Dict[str, Any]:
        """
        Get the details of a model.

        Returns:
            Dict[str, Any]: Model details including metadata, configuration, and status
        """
        return self._client.get_model_details(self.model_id)

    def get_nb_predictions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[List[str]] = None,
        model_version: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get the number of predictions for a model within a specified time range.

        Args:
            start_date: Start date for filtering predictions (ISO format)
            end_date: End date for filtering predictions (ISO format)
            interval_type: Type of interval for aggregation ("DAILY" or "HOURLY")
            filters: List of filters to apply to predictions
            model_version: Specific model version to query

        Returns:
            pd.DataFrame: DataFrame containing the number of predictions matching the criteria
        """
        # Use SQL for now:
        df = self.get_custom_metric(
            "SELECT count(*) FROM model",
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            filters=filters,
            model_version=model_version,
        )
        return df

    def get_custom_metric(
        self,
        sql: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[List[str]] = None,
        model_version: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Execute a custom SQL query to retrieve model metrics.

        Args:
            sql: SQL query string to execute
            start_date: Start date for filtering results (ISO format)
            end_date: End date for filtering results (ISO format)
            interval_type: Type of interval for aggregation ("DAILY" or "HOURLY")
            filters: List of filters to apply to results
            model_version: Specific model version to query

        Returns:
            DataFrame: Results of the SQL query
        """
        if start_date is None:
            start_date = self._config.get_option("startDate")
        if end_date is None:
            end_date = self._config.get_option("endDate")
        if interval_type is None:
            interval_type = self._config.get_option("intervalType")
        if filters is None:
            filters = self._config.get_option("filters")
        if model_version is None:
            model_version = self._config.get_option("modelVersion")

        predicates = convert_config_filters_to_predicates(filters or [])
        data = self._client.get_custom_metrics(
            model_id=self.model_id,
            sql=sql,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            predicates=predicates,
            model_version=model_version,
        )

        df = custom_metrics_to_dataframe(data, sql)
        df.attrs.update(
            {
                "method": "get_custom_metrics",
                "sql": sql,
                "start_date": start_date,
                "end_date": end_date,
                "interval_type": interval_type,
                "filters": filters,
                "model_version": model_version,
            }
        )
        return df

    def get_feature_drift(
        self,
        feature_name: str,
        algorithm: str = "EMD",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[List[str]] = None,
        model_version: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate drift metrics for a specific feature.

        Args:
            feature_name: Name of the feature to calculate drift for
            algorithm: Drift calculation algorithm ("EMD", "PSI", or "KL")
            start_date: Start date for drift calculation (ISO format)
            end_date: End date for drift calculation (ISO format)
            interval_type: Type of interval for aggregation ("DAILY" or "HOURLY")
            filters: List of filters to apply to drift calculation
            model_version: Specific model version to query

        Returns:
            DataFrame: Drift metrics for the specified feature
        """
        if start_date is None:
            start_date = self._config.get_option("startDate")
        if end_date is None:
            end_date = self._config.get_option("endDate")
        if interval_type is None:
            interval_type = self._config.get_option("intervalType")
        if filters is None:
            filters = self._config.get_option("filters")
        if model_version is None:
            model_version = self._config.get_option("modelVersion")

        predicates = convert_config_filters_to_predicates(filters or [])
        data = self._client.get_feature_drift(
            feature_name=feature_name,
            algorithm=algorithm,
            model_id=self.model_id,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            predicates=predicates,
            model_version=model_version,
        )
        df = feature_drift_to_dataframe(data)
        df.attrs.update(
            {
                "method": "get_feature_drift",
                "feature_name": feature_name,
                "start_date": start_date,
                "end_date": end_date,
                "interval_type": interval_type,
                "filters": filters,
                "model_version": model_version,
            }
        )
        return df

    def get_feature_category_distribution(
        self,
        feature_name: str,
        normalize: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval_type: Optional[str] = None,
        filters: Optional[List[str]] = None,
        model_version: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get the distribution of categories for a categorical feature.

        Args:
            feature_name: Name of the categorical feature
            normalize: If True, returns percentages instead of counts
            start_date: Start date for distribution calculation (ISO format)
            end_date: End date for distribution calculation (ISO format)
            interval_type: Type of interval for aggregation ("DAILY" or "HOURLY")
            filters: List of filters to apply to distribution calculation
            model_version: Specific model version to query

        Returns:
            DataFrame: Distribution of feature categories
        """
        if start_date is None:
            start_date = self._config.get_option("startDate")
        if end_date is None:
            end_date = self._config.get_option("endDate")
        if interval_type is None:
            interval_type = self._config.get_option("intervalType")
        if filters is None:
            filters = self._config.get_option("filters")
        if model_version is None:
            model_version = self._config.get_option("modelVersion")

        predicates = convert_config_filters_to_predicates(filters or [])
        data = self._client.get_feature_category_distribution(
            feature_name=feature_name,
            model_id=self.model_id,
            normalize=normalize,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            predicates=predicates,
            model_version=model_version,
        )
        df = feature_category_distribution_to_dataframe(data)
        df.attrs.update(
            {
                "method": "get_feature_category_distribution",
                "feature_name": feature_name,
                "start_date": start_date,
                "end_date": end_date,
                "interval_type": interval_type,
                "filters": filters,
                "model_version": model_version,
            }
        )
        return df

    def get_feature_density(
        self,
        feature_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[List[str]] = None,
        model_version: Optional[str] = None,
        interval_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get the probability density function (PDF) of a numeric feature.

        Args:
            feature_name: Name of the numeric feature
            start_date: Start date for density calculation (ISO format)
            end_date: End date for density calculation (ISO format)
            filters: List of filters to apply to density calculation
            model_version: Specific model version to query
            interval_type: Type of interval for aggregation ("DAILY" or "HOURLY")

        Returns:
            DataFrame: Probability density function of the feature values
        """
        if start_date is None:
            start_date = self._config.get_option("startDate")
        if end_date is None:
            end_date = self._config.get_option("endDate")
        if filters is None:
            filters = self._config.get_option("filters")
        if model_version is None:
            model_version = self._config.get_option("modelVersion")
        if interval_type is None:
            interval_type = self._config.get_option("intervalType")

        predicates = convert_config_filters_to_predicates(filters or [])
        data = self._client.get_feature_density(
            model_id=self.model_id,
            feature_name=feature_name,
            start_date=start_date,
            end_date=end_date,
            predicates=predicates,
            model_version=model_version,
            interval_type=interval_type,
        )
        df = feature_density_to_dataframe(data)
        df.attrs.update(
            {
                "method": "get_feature_density",
                "feature_name": feature_name,
                "start_date": start_date,
                "end_date": end_date,
                "interval_type": interval_type,
                "filters": filters,
                "model_version": model_version,
            }
        )
        return df

    def get_feature_percentiles(
        self,
        feature_name: str,
        percentiles: Optional[List[float]] = None,  # Only these are supported
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[List[str]] = None,
        model_version: Optional[str] = None,
        interval_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get the specified percentiles for a numeric feature.

        Args:
            feature_name: Name of the numeric feature
            percentiles: List of percentiles to calculate (default: [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1])
                Only these specific percentile values are supported
            start_date: Start date for percentile calculation (ISO format)
            end_date: End date for percentile calculation (ISO format)
            filters: List of filters to apply to percentile calculation
            model_version: Specific model version to query
            interval_type: Type of interval for aggregation. Must be one of "DAILY" or "HOURLY".
                Passing any other value will raise a ValueError.

        Returns:
            DataFrame: Percentile values for the specified feature
        """
        if percentiles is None:
            percentiles = [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]
        if start_date is None:
            start_date = self._config.get_option("startDate")
        if end_date is None:
            end_date = self._config.get_option("endDate")
        if interval_type is None:
            interval_type = self._config.get_option("intervalType")
        if filters is None:
            filters = self._config.get_option("filters")
        if model_version is None:
            model_version = self._config.get_option("modelVersion")

        predicates = convert_config_filters_to_predicates(filters or [])
        data = self._client.get_feature_percentiles(
            model_id=self.model_id,
            feature_name=feature_name,
            percentiles=percentiles,
            start_date=start_date,
            end_date=end_date,
            interval_type=interval_type,
            predicates=predicates,
            model_version=model_version,
        )
        df = feature_percentiles_to_dataframe(data)
        df.attrs.update(
            {
                "method": "get_feature_percentiles",
                "feature_name": feature_name,
                "start_date": start_date,
                "end_date": end_date,
                "interval_type": interval_type,
                "filters": filters,
                "model_version": model_version,
            }
        )
        return df

    def get_numerical_features(self) -> List[str]:
        """
        Get the list of numerical features available for this model.

        Returns:
            List[str]: List of numerical feature names
        """
        return self._client.get_numerical_features(self.model_id)

    def get_categorical_features(self) -> List[str]:
        """
        Get the list of categorical features available for this model.

        Returns:
            List[str]: List of categorical feature names
        """
        return self._client.get_categorical_features(self.model_id)
