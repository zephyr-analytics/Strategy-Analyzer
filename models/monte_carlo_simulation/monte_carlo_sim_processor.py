"""
Abstract module for processing monte carlo simulations.
"""

from abc import ABC, abstractmethod
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import utilities as utilities

class MonteCarloProcessor(ABC):
    def __init__(self):
        super().__init__()
        pass