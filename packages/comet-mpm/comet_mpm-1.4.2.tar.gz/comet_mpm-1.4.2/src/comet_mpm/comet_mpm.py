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

import asyncio as asyncio_module
import atexit
import logging
import os
import sys
import traceback
from typing import Any, Awaitable, Dict, Iterable, List, Optional, Union

from . import constants, logging_messages, optional_update
from ._logging import ErrorStore
from .connection import MPM_BASE_PATH, stream_dataset_file
from .connection_helpers import url_join
from .environment import check_environment
from .events import events_from_dataframe
from .events.label_event import LabelsEvent
from .events.prediction_event import PredictionEvent
from .exceptions import CometMPMBackendException, CometMPMBackendIsNotAvailable
from .logging_messages import MPM_JOIN_DEPRECATED_WARNING, MPM_LABEL_DEPRECATED_WARNING
from .sender import get_sender
from .server_address import ServerAddress
from .settings import MPMSettings, get_model
from .settings_helper import extract_comet_url

LOGGER = logging.getLogger(__name__)

LogEventsResult = Union[List[Any], Awaitable[List[Any]]]


class CometMPM:
    """
    The Comet MPM class is used to upload a model's input and output features to MPM
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace_name: Optional[str] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        disabled: Optional[bool] = None,
        asyncio: bool = False,
        max_batch_size: Optional[int] = None,
        max_batch_time: Optional[int] = None,
        raise_on_error_during_init: bool = False,
    ):
        """
        Creates the Comet MPM Event logger object.
        Args:
            api_key: The Comet API Key
            workspace_name: The Comet Workspace Name of the model
            model_name: The Comet Model Name of the model
            model_version: The Comet Model Version of the model
            disabled: If set to True, CometMPM will not send anything to the backend.
            asyncio: Set to True if you are using an Asyncio-based framework like FastAPI.
            max_batch_size: Maximum number of MPM events sent in a batch, can also be configured using the environment variable MPM_MAX_BATCH_SIZE.
            max_batch_time: Maximum time before a batch of events is submitted to MPM, can also be configured using the environment variable MPM_MAX_BATCH_SIZE.
            raise_on_error_during_init: If set to True, CometMPM will raise exceptions instead of just logging errors during initialization. Default is False for backwards compatibility.
        """

        settings_user_values: Dict[str, Union[str, int]] = {}
        optional_update.update(
            settings_user_values,
            {
                "api_key": api_key,
                "mpm_model_name": model_name,
                "mpm_model_version": model_version,
                "mpm_workspace_name": workspace_name,
                "mpm_max_batch_size": max_batch_size,
                "mpm_max_batch_time": max_batch_time,
            },
        )

        self._settings = get_model(
            MPMSettings,
            **settings_user_values,
        )
        if disabled:
            self.disabled = disabled  # type: bool
        else:
            self.disabled = bool(os.getenv("COMET_MPM_DISABLED"))
        self._asyncio = asyncio
        # Use the provided raise_on_error_during_init value, or fall back to settings value
        self._raise_on_error_during_init = (
            raise_on_error_during_init or self._settings.mpm_raise_on_error_during_init
        )

        comet_url = extract_comet_url(self._settings)

        self._mpm_server_address = ServerAddress(
            base_url=url_join(comet_url, MPM_BASE_PATH),
            api_version="v2",
        )

        # Create instance-specific error store for capturing background thread errors
        self._error_store = ErrorStore()

        if self.disabled:
            self._sender = None
        else:
            self._sender = get_sender(
                api_key=self._settings.api_key,
                server_address=self._mpm_server_address,
                max_batch_size=self._settings.mpm_max_batch_size,
                max_batch_time=self._settings.mpm_max_batch_time,
                asyncio=self._asyncio,
                batch_sending_timeout=self._settings.mpm_batch_sending_timeout,
                error_store=self._error_store,
            )

            if not self._asyncio:
                self._do_connect()

            atexit.register(self._on_end)

        check_environment()

    def log_event(
        self,
        prediction_id: str,
        input_features: Optional[Dict[str, Any]] = None,
        output_value: Optional[Any] = None,
        output_probability: Optional[Any] = None,
        output_features: Optional[Dict[str, Any]] = None,
        labels: Optional[Dict[str, Union[int, float, bool, str]]] = None,
        timestamp: Optional[float] = None,
    ) -> Optional[Awaitable[None]]:
        """
        Asynchronously log a single event to MPM. Events are identified by the
        mandatory prediction_id parameter.
        If you send multiple events with the same prediction_id,
        the Comet platform with automatically reject the duplicate events.

        Args:
            prediction_id: The unique prediction ID. It can be provided by the
                framework, you, or a random unique value such as str(uuid4()).
            input_features: If provided, it must be a flat dictionary where the
                keys are the feature names, and the values are native Python
                scalars, such as integers, floats, booleans, or strings. For
                example: `{"age": 42, "income": 42894.89}`.
            output_value: The prediction as a native Python scalar, such as an
                 integer, float, boolean, or string.
            output_probability: If provided, it must be a float between 0 and
                 1, indicating the model's confidence in the prediction.
            output_features: A dictionary of output features.
            labels: If provided, it must be a flat dictionary where the
                keys are the label names, and the values are native Python
                scalars, such as integers, floats, booleans, or strings. For
                example: `{"person": 2, "bicycle": 1, "car": 3}`.
            timestamp: An optional timestamp to associate with the event
                (seconds since epoch in UTC timezone). If not provided, the
                 current time will be used."""
        if self.disabled:
            if self._asyncio is False:
                return None
            else:
                return asyncio_module.sleep(0)

        output_features = _handle_event_output_features(
            output_value, output_probability, output_features
        )

        event = PredictionEvent(
            workspace=self._settings.mpm_workspace_name,
            model_name=self._settings.mpm_model_name,
            model_version=self._settings.mpm_model_version,
            prediction_id=prediction_id,
            input_features=input_features,
            output_features=output_features,
            labels=labels,
            timestamp=timestamp,
        )
        return self._log_event(event)

    def upload_dataset_csv(
        self,
        file_path: str,
        dataset_type: str,
        dataset_name: Optional[str] = None,
        na_values: Optional[str] = None,
        keep_default_na_values: Optional[str] = None,
    ) -> None:
        """Uploads dataset from a local CSV file to the backend, streaming the data line by line.

        This method facilitates the creation or updating of a dataset with data streamed from a specified
        CSV file. The uploaded data is used as a reference for detecting drift in a production model within the same
        workspace. Each line of the CSV file is sent as an event to the dataset, allowing for incremental
        updates.

        Args:
            file_path (`str`): The path to the local CSV file whose data is to be streamed to the backend.
            dataset_type (`Literal['EVENTS', 'LATE_LABELS', 'TRAINING_EVENTS']`): Type of the dataset to be updated
            or created. Default is 'TRAINING_EVENTS'.
            dataset_name (`str`): The name of the dataset where the data will be stored. If a model
                with this name does not exist, a new model will be created. If the model already exists, new records
                will be added to it (duplicated predictionIds will be ignored).
                In case dataset_type is TRAINING_EVENTS this is mandatory as the MPM model_name
                is the production model, which the dataset_name parameter is referring to.
            na_values (`str`, *optional*): Additional strings to recognize as NA/NaN. By default, the system
                recognizes standard missing values (like empty fields, 'NaN', 'NULL', etc.). Specifying this parameter
                allows for the inclusion of custom missing value identifiers, enhancing the flexibility in data
                handling. If specified, it should be as comma delimiter string. The default list is (Note that empty
                string is also in this list): None,,null,NULL,N/A,NA,NaN,n/a,nan
            keep_default_na_values (`str`, *optional*, defaults to None): A boolean that determines whether to
                include the default set of NA identifiers in addition to the values specified in 'na_values'. If
                `True`, both default and specified missing value identifiers are used. If `False`, only the values
                specified in 'na_values' are considered.

        Returns: None

        Notes:
            CSV Format:
            - The first line of the CSV file must contain headers.
            - Columns:
              1. timestamp (optional): If missing, the current timestamp will be used as the event time. If specified,
                 it should be the millis since epoch.
              2. predictionId (optional): Unique identifier for each event. If missing, a UUID will be generated.
                 Duplicate predictionIds in new events will be ignored.
              3. feature_* columns: These prefixed columns specify the input features for the model,
                 e.g., 'feature_age' or 'feature_color'.
              4. prediction_* columns: These prefixed columns are for the output features,
                 e.g., 'prediction_animal' or 'prediction_probability'.
              5. label_value_* columns: These columns are for the label values of the event,
                 e.g., 'label_value_price' or 'label_value_animal'.

            Sample CSV content:
                timestamp,predictionId,feature_oneMoreFeature,feature_anotherFeature,feature_someFeature,prediction_fingers_count,prediction_probability,prediction_value,label_value_fingers_count,label_value_animal
                1713006000001,someAssetId_-1895825684,Dog,special,53.09863247819340,7,0.87,Bird,4,Fish
                1713006600001,someAssetId_926457604,null,special,55.73110218323990,1,0.69,Fish,6,Fish
                1713007200001,someAssetId_2145792990,Rabbit,special,49.40627545548700,4,0.59,Bird,1,Fish

        Examples:
            ```python linenums="1"
            from comet_mpm import CometMPM

            MPM = CometMPM()
            MPM.upload_dataset_csv(
                file_path="path/to/your/data.csv",
                dataset_type="TRAINING_EVENTS",  # Or use 'EVENTS', 'LATE_LABELS' as needed
                dataset_name="your-dataset-name"
            )
            ```
        """
        stream_dataset_file(
            api_key=self._settings.api_key,
            file_path=file_path,
            base_url=self._mpm_server_address.base_url,
            workspace_name=self._settings.mpm_workspace_name,
            model_name=self._settings.mpm_model_name,
            model_version=self._settings.mpm_model_version,
            dataset_type=dataset_type,
            dataset_name=dataset_name,
            na_values=na_values,
            keep_default_na_values=keep_default_na_values,
        )

    def log_label(
        self,
        prediction_id: str,
        label: Optional[Any] = None,
        labels: Optional[Dict[str, Union[int, float, bool, str]]] = None,
        timestamp: Optional[float] = None,
    ) -> Optional[Awaitable[None]]:
        """
        Send an MPM event containing the ground truth value for a prediction whose input and output
        features are already stored in Comet.
        If you send multiple labels with the same prediction_id,
        the Comet platform with automatically reject the duplicate labels.
        Args:
            prediction_id: The unique prediction ID
            label: Deprecated, please use the labels instead. If provided, this
                value will be used put as 'value' within the labels.
            labels: The ground truth values for the prediction. It must be a flat dictionary where the
                keys are the label names, and the values are native Python
                scalars, such as integers, floats, booleans, or strings. For
                example: `{"person": 2, "bicycle": 1, "car": 3}`.
            timestamp: An optional timestamp to associate with the label
                (seconds since epoch in UTC timezone). If not provided, the
                 current time will be used.
        """
        if self.disabled:
            if self._asyncio is False:
                return None
            else:
                return asyncio_module.sleep(0)

        if labels is None:
            labels = {}

        if label is not None:
            LOGGER.warning(MPM_LABEL_DEPRECATED_WARNING)
            labels["value"] = label

        event = LabelsEvent(
            workspace=self._settings.mpm_workspace_name,
            model_name=self._settings.mpm_model_name,
            model_version=self._settings.mpm_model_version,
            prediction_id=prediction_id,
            labels=labels,
            timestamp=timestamp,
        )
        return self._log_event(event)

    def log_dataframe(  # type: ignore[no-untyped-def]
        self,
        dataframe,
        prediction_id_column: str,
        feature_columns: Optional[List[str]] = None,
        output_value_column: Optional[str] = None,
        output_probability_column: Optional[str] = None,
        output_features_columns: Optional[List[str]] = None,
        labels_columns: Optional[List[str]] = None,
        timestamp_column: Optional[str] = None,
    ) -> LogEventsResult:
        """
        This function logs each row of a Pandas DataFrame as an MPM event. The
        events are structured as described in the [log_event](#cometmpmlog_event)
        method, so please refer to it for full context.

        Args:
            dataframe: The Pandas DataFrame to be logged.
            prediction_id_column: This column should contain the prediction_id values for the
                events.
            feature_columns: If provided, these columns will be used as the input_features
                for the events.
            output_features_columns: If provided, these columns will be used as the output_features for the events.
            output_value_column: Deprecated, please use the output_features_column field instead. If provided, this
                column will be used as the output_value for the events.
            output_probability_column: Deprecated, please use the output_features_column field instead.
                If provided, this column will be used as the output_probability for the events.
            labels_columns: If provided, these columns will be used as the labels for the events.
            timestamp_column: If provided, this column will be used as the timestamp (seconds since
                epoch start in UTC timezone) for the events.
        """
        events = events_from_dataframe.generate(
            workspace=self._settings.mpm_workspace_name,
            model_name=self._settings.mpm_model_name,
            model_version=self._settings.mpm_model_version,
            dataframe=dataframe,
            prediction_id_column=prediction_id_column,
            feature_columns=feature_columns,
            output_features_columns=output_features_columns,
            output_value_column=output_value_column,
            output_probability_column=output_probability_column,
            labels_columns=labels_columns,
            timestamp_column=timestamp_column,
        )

        return self._log_events(events)

    def connect(self) -> Optional[Awaitable[None]]:
        """
        When using CometMPM in asyncio mode, this coroutine needs to be awaited
        at the server start.
        """
        if self._asyncio is False:
            return None
        else:
            if self._sender is not None:
                return asyncio_module.create_task(self._do_async_connect())

            return asyncio_module.sleep(0)

    def join(self, timeout: Optional[int] = None) -> Optional[Awaitable[None]]:
        """
        MPM.join is deprecated, use MPM.end instead.
        """
        LOGGER.warning(MPM_JOIN_DEPRECATED_WARNING)
        return self.end(timeout)

    def end(self, timeout: Optional[int] = None) -> Optional[Awaitable[None]]:
        """Ensure that all data has been sent to Comet and close the MPM object.
        After that, no data can be logged anymore. Waits for up to 30 seconds if timeout is not set.
        """
        if timeout is None:
            timeout = self._settings.mpm_join_timeout

        if not self.disabled:
            assert self._sender is not None
            if self._asyncio:
                return self._sender.join(timeout)
            else:
                self._sender.close(timeout)

                # Check for remaining events after manual close (similar to _on_end)
                if self._sender.sender_queue is not None:
                    remaining_events = self._sender.sender_queue.qsize()
                    if remaining_events > 0:
                        error_message = f"Upload timeout reached, {remaining_events:,.0f} MPM events were not synced with MPM. Consider increasing timeout parameter or using MPM.end() earlier in your script."
                        LOGGER.warning(error_message)
                        print(
                            f"COMET WARNING: {error_message}",
                            file=sys.stderr,
                            flush=True,
                        )

        if self._asyncio is False:
            return None
        else:
            return asyncio_module.sleep(0)

    def get_logging_errors(self, clear: bool = True) -> List[Dict[str, Any]]:
        """Get any logging errors that occurred during background processing.

        This method allows users to programmatically check for and handle
        errors that occurred in background threads, such as network failures
        when sending batch data to the backend.

        Args:
            clear: If True, clear the error store after retrieving errors.
                   Defaults to True to prevent memory leaks.

        Returns:
            List of error dictionaries, each containing:
            - 'message': The error message
            - 'logger_name': Name of the logger that produced the error
            - 'timestamp': ISO timestamp when the error occurred
            - 'data_affected': Description of what data was affected (optional)
            - 'traceback': Exception traceback information (optional)

        Example:
            >>> mpm = CometMPM(...)
            >>> mpm.log_event(...)
            >>> mpm.end()
            >>> errors = mpm.get_logging_errors()
            >>> if errors:
            ...     print(f"Found {len(errors)} errors:")
            ...     for error in errors:
            ...         print(f"  {error['timestamp']}: {error['message']}")
        """
        return self._error_store.get_errors(clear=clear)

    def has_logging_error(self) -> bool:
        """Check if there are any stored logging errors without retrieving them.

        Returns:
            True if there are errors in the store, False otherwise.

        Example:
            >>> mpm = CometMPM(...)
            >>> mpm.log_event(...)
            >>> mpm.end()
            >>> if mpm.has_logging_error():
            ...     errors = mpm.get_logging_errors()
            ...     # Handle errors
        """
        return self._error_store.has_errors()

    def _on_end(self) -> None:
        if not self.disabled:
            assert self._sender is not None
            self._sender.close(timeout=self._settings.mpm_join_timeout)

            if self._sender.sender_queue is not None:
                remaining_events = self._sender.sender_queue.qsize()
                if remaining_events > 0:
                    error_message = f"Upload process timed-out, {remaining_events:,.0f} MPM events were not synced with MPM. Timeout can be increased using the COMET_MPM_JOIN_TIMEOUT environment variable."
                    print(f"COMET ERROR: {error_message}", file=sys.stderr, flush=True)

    def _log_events(self, events: Iterable[PredictionEvent]) -> LogEventsResult:
        results = []
        for event in events:
            result = self._log_event(event)
            if result is not None:
                results.append(result)

        if self._asyncio and len(results) > 0:
            return asyncio_module.gather(*results)

        return results

    def _log_event(
        self, event: Union[PredictionEvent, LabelsEvent]
    ) -> Optional[Awaitable[None]]:
        assert self._sender is not None
        return self._sender.put(event)

    def _do_connect(self) -> None:
        try:
            assert self._sender is not None
            self._sender.connect()
        except (CometMPMBackendException, CometMPMBackendIsNotAvailable) as exc:
            error_message = f"Connection failed during initialization: {str(exc)}"
            LOGGER.error(error_message)
            self.disabled = True

            # Store connection error for programmatic access
            if hasattr(self, "_error_store") and self._error_store is not None:
                self._error_store.add_error(
                    message=error_message,
                    logger_name="comet_mpm.comet_mpm",
                    data_affected=None,
                    traceback_info=traceback.format_exc(),
                )

            if self._raise_on_error_during_init:
                raise

    async def _do_async_connect(self) -> None:
        try:
            assert self._sender is not None
            await self._sender.connect()
        except (CometMPMBackendException, CometMPMBackendIsNotAvailable) as exc:
            LOGGER.error(str(exc))
            self.disabled = True

            # Store connection error for programmatic access
            if hasattr(self, "_error_store") and self._error_store is not None:
                self._error_store.add_error(
                    message=str(exc),
                    logger_name="comet_mpm.comet_mpm",
                    data_affected=None,
                    traceback_info=traceback.format_exc(),
                )

            if self._raise_on_error_during_init:
                raise
        except Exception:
            # Convert connection errors to CometMPMBackendIsNotAvailable for consistency
            backend_exc = CometMPMBackendIsNotAvailable()
            LOGGER.error(str(backend_exc))
            self.disabled = True

            # Store connection error for programmatic access
            if hasattr(self, "_error_store") and self._error_store is not None:
                self._error_store.add_error(
                    message=str(backend_exc),
                    logger_name="comet_mpm.comet_mpm",
                    data_affected=None,
                    traceback_info=traceback.format_exc(),
                )

            if self._raise_on_error_during_init:
                raise backend_exc


def _handle_event_output_features(
    output_value: Any,
    output_probability: Any,
    output_features: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    event_output_features: Optional[Dict[str, Any]]

    if (
        output_value is not None or output_probability is not None
    ) and output_features is None:
        LOGGER.warning(
            logging_messages.DEPRECATED_OUTPUT_VALUE_AND_PROBABILITY_WITHOUT_FEATURES
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
            logging_messages.DEPRECATED_OUTPUT_VALUE_AND_PROBABILITY_WITH_FEATURES
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
