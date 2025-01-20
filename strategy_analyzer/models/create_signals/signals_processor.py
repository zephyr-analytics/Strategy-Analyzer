"""
Abstract module for processing trading signals.
"""

from abc import ABC, abstractmethod

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import strategy_analyzer.utilities as utilities
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.results.signals_results_processor import SignalsResultsProcessor


class SignalsProcessor(ABC):
    """
    Abstract base class for creating portfolio signals.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the SignalProcessor class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results


    def process(self):
        """
        Abstract method to process data and generate trading signals.
        """
        self.generate_signals()
        results_processor = SignalsResultsProcessor(models_data=self.data_models, models_results=self.results_models)
        results_processor.process()


    @abstractmethod
    def generate_signals(self):
        """
        Abstract method to generate trading signals.
        """
