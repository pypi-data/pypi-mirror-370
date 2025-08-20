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
from urllib.parse import urljoin

import requests

from . import prefix_helpers


class Client:
    """
    A REST client for interacting with the Comet MPM API.

    This client provides methods for making HTTP requests to the Comet MPM API endpoints,
    including model predictions, feature analysis, and custom metric queries.

    Note:
        The client automatically handles authentication for all requests.
    """

    def __init__(
        self,
        request_session: requests.Session,
        base_url: str,
    ) -> None:
        """
        Initialize the Comet MPM REST client.

        Args:
            request_session: The requests session to use for HTTP requests
            base_url: The base URL for the Comet MPM API

        Note:
            The client uses the provided session for all HTTP requests and automatically
            includes authentication headers.
        """
        self.base_url = base_url
        self.session = request_session

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the Comet MPM API.

        Args:
            endpoint: The API endpoint to request (e.g., 'api/mpm/v2/model/numberOfPredictions')
            params: Optional query parameters for the request

        Returns:
            Dict: JSON response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the server returns a non-200 status code
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return_data: Dict[str, Any] = response.json()
        return return_data

    def post(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the Comet MPM API.

        Args:
            endpoint: The API endpoint to request (e.g., 'api/mpm/v2/features/drift')
            params: Request body parameters as a dictionary

        Returns:
            Dict: JSON response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the server returns a non-200 status code
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.post(url, json=params)
        response.raise_for_status()
        return_data: Dict[str, Any] = response.json()
        return return_data

    def get_model_id(self, workspace_name: str, model_name: str) -> Optional[str]:
        """
        Retrieve the ID of a specific model within a workspace.

        Args:
            workspace_name: The name of the workspace containing the model
            model_name: The name of the model to search for

        Returns:
            Optional[str]: The ID of the model if found, otherwise None

        Raises:
            requests.exceptions.RequestException: If the request to the API fails
            requests.exceptions.HTTPError: If the server returns a non-200 status code
        """
        endpoint = "api/mpm/v3/workspaces"
        params = None
        response = self.get(endpoint, params)
        for workspace in response["workspaces"]:
            if workspace["workspaceName"] == workspace_name:
                for model in workspace["models"]:
                    if model["modelName"] == model_name:
                        return str(model["modelId"])
        return None

    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.

        Args:
            model_id: The ID of the model to retrieve details for

        Returns:
            Dict[str, Any]: Model details including metadata, configuration, and status

        Raises:
            requests.exceptions.HTTPError: If the model is not found or the request fails
        """
        endpoint = f"api/mpm/v2/model/details?modelId={model_id}"
        response = self.get(endpoint)
        return response

    def get_nb_predictions(
        self,
        model_id: str,
        start_date: str,
        end_date: str,
        interval_type: str,
        predicates: List[Dict[str, str]],
        model_version: Optional[str],
    ) -> Dict[str, Any]:
        """
        Get the number of predictions for a model within a specified time range.

        Args:
            model_id: The ID of the model
            start_date: Start date for the query (ISO format)
            end_date: End date for the query (ISO format)
            interval_type: Time interval type ("DAILY" or "HOURLY")
            predicates: List of filter predicate dictionaries with "key" and "query" fields
            model_version: Model version identifier

        Returns:
            Dict[str, Any]: Number of predictions with time series data

        Raises:
            requests.exceptions.HTTPError: If the query fails or returns invalid results
        """
        endpoint = "api/mpm/v2/model/numberOfPredictions"
        params = {
            "modelId": model_id,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "predicates": predicates,
            "version": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_custom_metrics(
        self,
        model_id: str,
        sql: str,
        start_date: str,
        end_date: str,
        interval_type: str,
        predicates: List[Dict[str, str]],
        model_version: Optional[str],
    ) -> Dict[str, Any]:
        """
        Get custom metrics using SQL query.

        Args:
            model_id: ID of the model
            sql: SQL query string (e.g., "SELECT count(*) FROM model")
            start_date: Start date for the query (ISO format)
            end_date: End date for the query (ISO format)
            interval_type: Time interval type ("DAILY" or "HOURLY")
            predicates: List of filter predicate dictionaries with "key" and "query" fields
            model_version: Model version identifier

        Returns:
            Dict[str, Any]: Metric results from the SQL query

        Raises:
            requests.exceptions.HTTPError: If the query fails or returns invalid results
        """
        endpoint = "api/mpm/v2/custom-metrics/query"
        params = {
            "modelId": model_id,
            "cometSql": sql,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "predicates": predicates,
            "version": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_feature_drift(
        self,
        model_id: str,
        feature_name: str,
        algorithm: str,
        start_date: str,
        end_date: str,
        interval_type: str,
        predicates: List[Dict[str, str]],
        model_version: Optional[str],
    ) -> Dict[str, Any]:
        """
        Get feature drift analysis between different data sources.

        Args:
            model_id: ID of the model
            feature_name: Name of the feature to analyze
            algorithm: Drift detection algorithm ("EMD", "PSI", or "KL")
            start_date: Start date for the analysis (ISO format)
            end_date: End date for the analysis (ISO format)
            interval_type: Time interval type ("DAILY" or "HOURLY")
            predicates: List of filter predicate dictionaries with "key" and "query" fields
            model_version: Model version identifier

        Returns:
            Dict[str, Any]: Feature drift analysis results

        Raises:
            requests.exceptions.HTTPError: If the analysis fails or returns invalid results
        """
        endpoint = "api/mpm/v2/features/drift"
        feature_name = prefix_helpers.remove_prefix(feature_name)
        source = self.get_feature_source_type(model_id, feature_name)
        if source is None:
            raise Exception("unable to handle label as feature")
        params = {
            "modelId": model_id,
            "name": feature_name,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "algorithmType": algorithm,
            "source": source,
            "predicates": predicates,
            "version": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_feature_category_distribution(
        self,
        model_id: str,
        feature_name: str,
        normalize: bool,
        start_date: str,
        end_date: str,
        interval_type: str,
        predicates: List[Dict[str, str]],
        model_version: Optional[str],
    ) -> Dict[str, Any]:
        """
        Get the category distribution of a feature.

        Args:
            model_id: Model ID
            feature_name: Name of the feature to analyze
            normalize: Whether to normalize the distribution (default: False)
            start_date: Start date for the analysis (ISO format)
            end_date: End date for the analysis (ISO format)
            interval_type: Time interval type ("DAILY" or "HOURLY")
            predicates: List of filter predicate dictionaries with "key" and "query" fields
            model_version: Model version identifier

        Returns:
            Dict[str, Any]: Category distribution of the feature

        Raises:
            requests.exceptions.HTTPError: If the analysis fails or returns invalid results

        Note:
            This method is specifically for categorical features.
        """
        categorical_features = self.get_categorical_features(model_id)
        if feature_name not in categorical_features:
            raise ValueError(
                f"{feature_name} is not categorical; should be one of {categorical_features}"
            )

        endpoint = "api/mpm/v2/features/distribution"
        feature_name = prefix_helpers.remove_prefix(feature_name)
        source = self.get_feature_source_type(model_id, feature_name)
        params = {
            "modelId": model_id,
            "normalize": normalize,
            "name": feature_name,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "source": source,
            "predicates": predicates,
            "version": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_feature_density(
        self,
        model_id: str,
        feature_name: str,
        start_date: str,
        end_date: str,
        predicates: List[Dict[str, str]],
        model_version: Optional[str],
        interval_type: str,
    ) -> Dict[str, Any]:
        """
        Get the probability density function (PDF) of a numerical feature.

        Args:
            model_id: ID of the model
            feature_name: Name of the numerical feature
            start_date: Start date for the analysis (ISO format)
            end_date: End date for the analysis (ISO format)
            predicates: List of filter predicate dictionaries with "key" and "query" fields
            model_version: Model version identifier
            interval_type: Time interval type ("DAILY" or "HOURLY")

        Returns:
            Dict[str, Any]: Probability density function of the feature values

        Raises:
            requests.exceptions.HTTPError: If the analysis fails or returns invalid results

        Note:
            This method is specifically for numerical features and returns a PDF.
        """
        numerical_features = self.get_numerical_features(model_id)
        if feature_name not in numerical_features:
            raise ValueError(
                f"{feature_name} is not numerical; should be one of {numerical_features}"
            )

        endpoint = "api/mpm/v2/features/numerical-distribution-pdf"
        feature_name = prefix_helpers.remove_prefix(feature_name)
        source = self.get_feature_source_type(model_id, feature_name)
        params = {
            "modelId": model_id,
            "name": feature_name,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "source": source,
            "predicates": predicates,
            "version": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_feature_percentiles(
        self,
        model_id: str,
        feature_name: str,
        percentiles: List[float],
        start_date: str,
        end_date: str,
        predicates: List[Dict[str, str]],
        model_version: Optional[str],
        interval_type: str,
    ) -> Dict[str, Any]:
        """
        Get percentile values for a numerical feature.

        Args:
            model_id: ID of the model
            feature_name: Name of the numerical feature
            percentiles: List of percentile values to calculate (e.g., [0.25, 0.5, 0.75])
            start_date: Start date for the analysis (ISO format)
            end_date: End date for the analysis (ISO format)
            predicates: List of filter predicate dictionaries with "key" and "query" fields
            model_version: Model version identifier
            interval_type: Time interval type ("DAILY" or "HOURLY")

        Returns:
            Dict[str, Any]: Percentile values for the specified feature

        Raises:
            requests.exceptions.HTTPError: If the analysis fails or returns invalid results

        Note:
            This method is specifically for numerical features and returns percentile statistics.
        """
        numerical_features = self.get_numerical_features(model_id)
        if feature_name not in numerical_features:
            raise ValueError(
                f"{feature_name} is not numerical; should be one of {numerical_features}"
            )

        endpoint = "api/mpm/v2/features/distribution"
        feature_name = prefix_helpers.remove_prefix(feature_name)
        source = self.get_feature_source_type(model_id, feature_name)
        params = {
            "modelId": model_id,
            "name": feature_name,
            "from": start_date,
            "to": end_date,
            "intervalType": interval_type,
            "source": source,
            "predicates": predicates,
            "version": model_version,
        }
        response = self.post(endpoint, params)
        return response

    def get_categorical_features(self, model_id: str) -> List[str]:
        """
        Get the list of categorical features for a model.

        Args:
            model_id: The ID of the model

        Returns:
            List[str]: List of categorical feature names with their prefixes
        """
        details = self.get_model_details(model_id)
        return [
            prefix_helpers.source_type_to_prefix(feature.get("source"))
            + "_"
            + feature["name"]
            for feature in details["model"]["features"]
            if feature["type"] == "CATEGORICAL"
        ]

    def get_numerical_features(self, model_id: str) -> List[str]:
        """
        Get the list of numerical features for a model.

        Args:
            model_id: The ID of the model

        Returns:
            List[str]: List of numerical feature names with their prefixes
        """
        details = self.get_model_details(model_id)
        return [
            prefix_helpers.source_type_to_prefix(feature.get("source"))
            + "_"
            + feature["name"]
            for feature in details["model"]["features"]
            if feature["type"] == "NUMERICAL"
        ]

    def get_feature_source_type(
        self, model_id: str, feature_name: str
    ) -> Optional[str]:
        """
        Get the source type of a feature.

        Args:
            model_id: ID of the model
            feature_name: Name of the feature (unprefixed)

        Returns:
            Optional[str]: Source type of the feature, or None if not found
        """
        # Unprefixed feature_name
        details = self.get_model_details(model_id)
        matching_sources = [
            feature.get("source")
            for feature in details["model"]["features"]
            if feature["name"] == feature_name
        ]
        return matching_sources[0] if matching_sources else None
