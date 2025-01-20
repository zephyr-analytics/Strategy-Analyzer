"""
Abstract module for processing parameter tuning.
"""

import json
import os
from abc import ABC, abstractmethod

from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.results.parameter_tuning_results_processor import ParameterTuningResultsProcessor


class ParameterTuningProcessor(ABC):
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
        results = self.get_portfolio_results()
        self.plot_results(results=results)

    @abstractmethod
    def get_portfolio_results(self) -> dict:
        """
        Processes parameters for tuning using joblib to parallelize execution.

        Returns
        -------
        dict
            A dictionary of backtest results and portfolio statistics from parameter tuning.
        """

    @abstractmethod
    def process_combination_wrapper(self, args) -> dict:
        """
        Wrapper function for processing a combination.
        Calls the class method with unpacked arguments.

        Parameters
        ----------
        args : tuple
            A tuple containing (ma, frequency, ma_type).

        Returns
        -------
        dict
            The result of the combination processing.
        """

    def plot_results(self, results: dict):
        """
        """
        results_process = ParameterTuningResultsProcessor(
            models_data=self.data_models,
            models_results=self.results_models,
            results=results
        )
        results_process.process()
