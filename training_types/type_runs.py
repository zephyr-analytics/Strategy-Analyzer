"""
Module to initialize run types.
"""

import warnings

from enum import Enum

warnings.filterwarnings("ignore")


class RunType(Enum):
    """
    Enum to define different types of backtest runs.
    """
    MOMENTUM = "momentum"
    IAOMOMENTUM = "in_and_out_momentum"
