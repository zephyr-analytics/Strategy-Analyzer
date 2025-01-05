"""
Abstract module for processing parameter tuning.
"""

from abc import ABC, abstractmethod

import utilities as utilities
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData

class ParameterTuningProcessor(ABC):
    """
    Abstract base class for creating portfolio signals.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        """
        Initializes the SignalProcessor class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        self.data_models = models_data
        self.data_portfolio = portfolio_data

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
    def plot_results(self, results: dict):
        """
        """
        pass

    @abstractmethod
    def persist_results(self, results: dict):
        """
        Persists the results dictionary as a JSON file.
        """
        pass
