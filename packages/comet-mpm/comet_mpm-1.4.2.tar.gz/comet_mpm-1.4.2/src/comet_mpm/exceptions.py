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
from comet_mpm.logging_messages import (
    ASYNCIO_SENDER_NOT_CONNECTED_ERROR,
    BACKEND_IS_NOT_AVAILABLE_ERROR,
)


class CometMPMException(Exception):
    """A common Exception class, all exceptions raised by comet_mpm will be children of this class"""


class AsyncioSenderNoConnected(CometMPMException):
    def __init__(self) -> None:
        self.args = (ASYNCIO_SENDER_NOT_CONNECTED_ERROR,)


class CometMPMBackendException(CometMPMException):
    def __init__(self, message: str):
        super().__init__(message)


class CometMPMBackendIsNotAvailable(CometMPMBackendException):
    def __init__(self) -> None:
        super().__init__(BACKEND_IS_NOT_AVAILABLE_ERROR)
