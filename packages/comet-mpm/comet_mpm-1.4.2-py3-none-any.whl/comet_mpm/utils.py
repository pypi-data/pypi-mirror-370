# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2025 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
import asyncio
import sys
import time
from typing import Awaitable, Callable, Optional

if sys.version_info[:2] >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


def get_comet_version() -> str:
    try:
        return importlib_metadata.version("comet_mpm")
    except importlib_metadata.PackageNotFoundError:
        return "Please install comet with `pip install comet_mpm`"


def wait_for_done(
    check_function: Callable[[], bool],
    timeout: float,
    progress_callback: Optional[Callable[[], None]] = None,
    sleep_time: float = 1,
) -> None:
    """Wait up to timeout seconds for the check function to return True.

    Args:
        check_function: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        progress_callback: Optional function called periodically during wait
        sleep_time: Interval between progress callback calls in seconds
    """
    end_time = time.time() + timeout
    while check_function() is False and time.time() < end_time:
        if progress_callback is not None:
            progress_callback()
        # Wait a max of sleep_time, but keep checking to see if
        # check_function is done. Allows wait_for_done to end
        # before sleep_time has elapsed:
        end_sleep_time = time.time() + sleep_time
        while check_function() is False and time.time() < end_sleep_time:
            time.sleep(sleep_time / 20.0)


async def async_wait_for_done(
    check_function: Callable[[], bool],
    timeout: float,
    progress_callback: Optional[Callable[[], Awaitable[None]]] = None,
    sleep_time: float = 1,
) -> None:
    """Async version: Wait up to timeout seconds for the check function to return True.

    Args:
        check_function: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        progress_callback: Optional async function called periodically during wait
        sleep_time: Interval between progress callback calls in seconds
    """
    end_time = time.time() + timeout
    while check_function() is False and time.time() < end_time:
        if progress_callback is not None:
            await progress_callback()
        # Wait a max of sleep_time, but keep checking to see if
        # check_function is done. Allows async_wait_for_done to end
        # before sleep_time has elapsed:
        end_sleep_time = time.time() + sleep_time
        while check_function() is False and time.time() < end_sleep_time:
            await asyncio.sleep(sleep_time / 20.0)
