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
import os

AWS_LAMBDA_ENVIRONMENT_MARKER_KEY = "LAMBDA_TASK_ROOT"


def is_aws_lambda_environment() -> bool:
    """Allows to check if we are executing in AWS lambda environment"""
    return AWS_LAMBDA_ENVIRONMENT_MARKER_KEY in os.environ
