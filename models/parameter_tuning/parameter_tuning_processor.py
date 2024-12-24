"""
Abstract module for processing parameter tuning.
"""

from abc import ABC, abstractmethod

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import utilities as utilities
from models.models_data import ModelsData


class ParameterTuningProcessor(ABC):
    """
    Abstract base class for creating portfolio signals.
    """

    def __init__(self, models_data: ModelsData):
        """
        Initializes the SignalProcessor class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        self.data_models = models_data

    def process(self):
        """
        Abstract method to process data and generate trading signals.
        """
        self.process_parameters()


    @abstractmethod
    def process_parameters(self):
        """
        Abstract method to generate trading signals.
        """
