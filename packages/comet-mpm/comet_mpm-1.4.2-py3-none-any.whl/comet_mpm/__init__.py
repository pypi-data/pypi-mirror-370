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

__all__ = ["CometMPM", "API", "ui"]

try:
    from comet_ml import ui
except ImportError:
    ui = None

from ._logging import _setup_comet_mpm_logging
from ._version import __version__  # noqa: F401
from .api_objects.api import API
from .comet_mpm import CometMPM

_setup_comet_mpm_logging()
