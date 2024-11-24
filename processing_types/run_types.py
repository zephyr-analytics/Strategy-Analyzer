"""
Module to create run types.
"""

from enum import Enum

class Runs(Enum):
    BACKTEST = "backtest"
    SIGNALS = "signals"
    SIMULATION = "simulation"
