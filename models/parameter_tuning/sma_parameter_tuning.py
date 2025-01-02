"""
Module for creating sma based porfolio signals.
"""

import os
import json

import plotly.express as px

import utilities as utilities
from models.models_data import ModelsData
from models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from models.backtest_models.sma_backtesting import SmaBacktestPortfolio


class SmaParameterTuning(ParameterTuningProcessor):
    """
    Processor for parameter tuning based on the an SMA portfolio.
    """
    def __init__(self, models_data: ModelsData):
        """
        Initializes the parameter tuning class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        super().__init__(models_data)

    def process(self):
        """
        Method for processing within the sma parameter tuning class.
        """
        results = self.get_portfolio_results()
        self.plot_results(results=results)
        self.persist_results(results=results)

    def get_portfolio_results(self) -> dict:
        """
        Processes parameters for tuning and stores results.
        
        Returns
        -------
        dict
            A dictionary of backtest results and portfolio statistics from parameter tuning.
        """
        results = {}
        ma_list = [21, 42, 63, 84, 105, 126, 147, 168, 189, 210]
        trading_frequencies = ["Monthly", "Bi-Monthly"]

        for ma in ma_list:
            for frequency in trading_frequencies:
                self.data_models.ma_window = ma
                self.data_models.trading_frequency = frequency

                backtest = SmaBacktestPortfolio(self.data_models)
                backtest.process()

                cagr = self.data_models.cagr
                average_annual_return = self.data_models.average_annual_return
                max_drawdown = self.data_models.max_drawdown
                var = self.data_models.var
                cvar = self.data_models.cvar
                annual_volatility = self.data_models.annual_volatility

                results[(ma, frequency)] = {
                    "cagr": cagr,
                    "average_annual_return": average_annual_return,
                    "max_drawdown": max_drawdown,
                    "var": var,
                    "cvar": cvar,
                    "annual_volatility": annual_volatility
                }

        return results

    def plot_results(self, results: dict):
        """
        Plot results from the SMA strategy testing.
        """
        data = {
            "MA_strategy": [
                f"MA_{key[0]}_Freq_{key[1]}" for key in results.keys()
            ],
            "cagr": [v["cagr"] for v in results.values()],
            "annual_volatility": [v["annual_volatility"] for v in results.values()],
            "max_drawdown": [v["max_drawdown"] for v in results.values()],
            "var": [v["var"] for v in results.values()],
            "cvar": [v["cvar"] for v in results.values()],
        }

        data["MA_Length"] = [key.split('_')[1] for key in data["MA_strategy"]]

        fig = px.scatter(
            data,
            x='annual_volatility',
            y='cagr',
            color='MA_Length',
            hover_data=['MA_strategy', 'max_drawdown', 'var', 'cvar'],
            labels={
                "cagr": "Compound Annual Growth Rate",
                "annual_volatility": "Annual Volatility"
            },
            title="Scatter Plot of MA Strategies"
        )

        utilities.save_fig(fig, self.data_models.weights_filename, self.data_models.processing_type)

    def persist_results(self, results: dict):
        """
        Persists the results dictionary as a JSON file.

        Parameters
        ----------
        results : dict
            The dictionary containing SMA backtest results and portfolio statistics.
        """
        current_directory = os.getcwd()
        artifacts_directory = os.path.join(current_directory, "artifacts", "data")
        os.makedirs(artifacts_directory, exist_ok=True)

        full_path = os.path.join(artifacts_directory, "sma_parameter_tune.json")
        results_serializable = {f"SMA_{key[0]}_Freq_{key[1]}": value for key, value in results.items()}
        with open(full_path, 'w') as json_file:
            json.dump(results_serializable, json_file, indent=4)
        print(f"Results successfully saved to {full_path}")
