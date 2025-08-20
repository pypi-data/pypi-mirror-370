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

BACKEND_IS_NOT_AVAILABLE_ERROR = "Comet Production Monitoring don't seems to be installed in your installation. Please contact your Comet Admin."

BACKEND_500_ERROR = "Comet Production Monitoring isn't working as expected, Please contact your Comet admin."

BATCH_SENDING_ERROR = "Error sending batch data to the backend"

UPLOAD_CSV_DATASET_ERROR = "Error on uploading csv dataset"

BATCH_SENDING_EXCEPTION = "Unknown exception happened when sending data to the backend"

LABEL_EVENT_SEND_ERROR = "Error sending label to the backend"

GEVENT_NOT_SUPPORTED = (
    "Using the MPM SDK with gevent is not officially supported, data loss might occurs"
)

ASYNCIO_SENDER_NOT_CONNECTED_ERROR = (
    "You need to call CometMPM.connect before sending events with CometMPM.log_event"
)

ASYNCIO_SENDER_HARD_SHUTDOWN = "There are still some data in-flight and might be missing. Make sure to call CometMPM.join() manually to guarantee that all data has been sent to the Backend"

ERROR_QUANTILES_LIST_EMPTY = (
    "Error cannot compute distribution summary because the quantiles list is empty."
)
ERROR_QUANTILES_INVALID_VALUE = (
    "The quantile must be within [0,1]. The current min value %f and max %f"
)

LOGGING_DIRECTORY_CREATION_ERROR = "Cannot create path to log file %r"

LOGGING_LOG_FILE_OPEN_ERROR = "Cannot open log file %r; file logging is disabled"

INVALID_SETTING_DEFAULT_FALLBACK = "Some MPM settings values were invalid, default values were used instead, see below for the list"

UNEXPECTED_EVENT_TYPE = "Unexpected event type %r"

DEPRECATED_OUTPUT_VALUE_AND_PROBABILITY_WITHOUT_FEATURES = 'You are using the deprecated fields `output_value` and `output_probability`,you should specify `output_features={"value": "<>", "probability": "<>"}`'

DEPRECATED_OUTPUT_VALUE_AND_PROBABILITY_WITH_FEATURES = 'You are using the deprecated fields `output_value` and `output_probability`, you should specify `output_features={"value": "<>", "probability": "<>", ...}`'

DEPRECATED_DATAFRAME_OUTPUT_VALUE_AND_PROBABILITY = "You are using the deprecated fields `output_value_column` and `output_probability_column`,you should specify `output_features_columns with value and probability columns`"

MPM_ALREADY_CLOSED_LOG_DATA_WARNING = "This MPM instance has already been closed. Create a new instance to log additional data."

MPM_IN_AWS_LAMBDA_NEEDS_END = "As you are running in a Lambda function, you will need to call 'mpm.end()' when finished to ensure all data is logged before exiting."

MPM_JOIN_DEPRECATED_WARNING = "MPM.join is deprecated, use MPM.end instead."

MPM_LABEL_DEPRECATED_WARNING = (
    "label parameter deprecated, use labels parameter instead."
)

PARSE_API_KEY_EMPTY_KEY = "Can not parse empty Comet API key"

PARSE_API_KEY_EMPTY_EXPECTED_ATTRIBUTES = (
    "Expected attributes not found in the Comet API key: %r"
)

PARSE_API_KEY_TOO_MANY_PARTS = "Too many parts (%d) found in the Comet API key: %r"

BASE_URL_MISMATCH_CONFIG_API_KEY = "Comet URL conflict detected between config (%r) and API Key (%r). MPM SDK will use config URL. Resolve by either removing config URL or set it to the same value."
