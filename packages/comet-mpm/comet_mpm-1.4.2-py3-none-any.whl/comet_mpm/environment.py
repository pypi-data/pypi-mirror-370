# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.com
#  Copyright (C) 2021-2024 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
import logging

from .aws_lambda.lambda_helpers import is_aws_lambda_environment
from .logging_messages import MPM_IN_AWS_LAMBDA_NEEDS_END

LOGGER = logging.getLogger(__name__)


def check_environment() -> None:
    if is_aws_lambda_environment():
        LOGGER.warning(MPM_IN_AWS_LAMBDA_NEEDS_END)
