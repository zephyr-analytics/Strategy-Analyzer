"""
Abstract module for processing parameter tuning.
"""

from abc import ABC, abstractmethod

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

    @abstractmethod
    def process(self):
        """
        Abstract method to process data and generate trading signals.
        """
        pass

    @abstractmethod
    def get_portfolio_results(self):
        """
        Abstract method to generate trading results for all parameters.
        """
        pass
    
    @abstractmethod
    def persist_results(self, results):
        """
        Persists the results dictionary as a JSON file.
        """
        pass

    @abstractmethod
    def optimize_portfolio(self, results, return_metric="cagr", risk_metric="max_drawdown"):
        """
        Abstract method for optimizing portfolio based on stats.
        """
        pass