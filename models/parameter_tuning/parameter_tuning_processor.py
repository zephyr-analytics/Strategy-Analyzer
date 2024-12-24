"""
Abstract module for processing parameter tuning.
"""
import json
import os
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

    def persist_results(self, results):
        """
        Persists the results dictionary as a JSON file.

        Parameters
        ----------
        results : dict
            The dictionary containing SMA backtest results and portfolio statistics.
        file_path : str
            The path to the JSON file where the results will be saved.
        """
        current_directory = os.getcwd()
        artifacts_directory = os.path.join(current_directory, "artifacts", "data")
        os.makedirs(artifacts_directory, exist_ok=True)

        full_path = os.path.join(artifacts_directory, "sma_parameter_tune.json")
        results_serializable = {f"SMA_{key[0]}_Freq_{key[1]}": value for key, value in results.items()}
        with open(full_path, 'w') as json_file:
            json.dump(results_serializable, json_file, indent=4)
        print(f"Results successfully saved to {full_path}")

    def optimize_portfolio(self, results, return_metric="cagr", risk_metric="max_drawdown"):
        """
        Finds the best portfolio from the results dictionary based on the selected return and risk metrics.

        Parameters
        ----------
        results : dict
            The dictionary containing SMA backtest results and portfolio statistics.
        return_metric : str, optional
            The primary return metric to optimize for (default is "cagr").
        risk_metric : str, optional
            The risk metric to consider for optimization (default is "max_drawdown").

        Returns
        -------
        tuple
            The best SMA and trading frequency configuration, along with its statistics.
        """
        best_config = None
        best_score = float('-inf')
        best_stats = None

        for (sma, frequency), stats in results.items():

            return_value = stats.get(return_metric, None)
            risk_value = stats.get(risk_metric, None)

            if return_value is None or risk_value is None:
                continue

            score = return_value / abs(risk_value)

            if score > best_score:
                best_score = score
                best_config = (sma, frequency)
                best_stats = stats
        print(best_config)
        print(best_stats)
        return best_config, best_stats
