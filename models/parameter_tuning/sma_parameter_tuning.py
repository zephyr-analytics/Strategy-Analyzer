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
        self.theme = models_data.theme_mode

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
        ma_types = ["SMA", "EMA"]

        for ma in ma_list:
            for frequency in trading_frequencies:
                for ma_type in ma_types:
                    self.data_models.ma_window = ma
                    self.data_models.trading_frequency = frequency
                    self.data_models.ma_type = ma_type

                    backtest = SmaBacktestPortfolio(self.data_models)
                    backtest.process()

                    cagr = self.data_models.cagr
                    average_annual_return = self.data_models.average_annual_return
                    max_drawdown = self.data_models.max_drawdown
                    var = self.data_models.var
                    cvar = self.data_models.cvar
                    annual_volatility = self.data_models.annual_volatility

                    results[(ma, frequency, ma_type)] = {
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
        Plot results from the MA strategy testing.

        Parameters
        ----------
        results : dict
            Dictionary of results from parameter tuning.
        """
        data = {
            "MA_Strategy": [
                f"MA:{key[0]} Freq:{key[1]} Type:{key[2]}" for key in results.keys()
            ],
            "cagr": [v["cagr"] for v in results.values()],
            "annual_volatility": [v["annual_volatility"] for v in results.values()],
            "max_drawdown": [v["max_drawdown"] for v in results.values()],
            "var": [v["var"] for v in results.values()],
            "cvar": [v["cvar"] for v in results.values()],
            "sharpe_ratio": [
                v["cagr"] / v["annual_volatility"] if v["annual_volatility"] != 0 else None 
                for v in results.values()
            ]
        }

        trimmed_twilight = px.colors.cyclical.Twilight[1:]
        fig = px.scatter(
            data,
            x='annual_volatility',
            y='cagr',
            color='sharpe_ratio',
            color_continuous_scale=trimmed_twilight[::-1],
            hover_data=['MA_Strategy', 'max_drawdown', 'var', 'cvar'],
            labels={
                "cagr": "Compound Annual Growth Rate",
                "annual_volatility": "Annual Volatility"
            },
            title="Possible MA Strategies"
        )
        chart_theme = "plotly_dark" if self.theme.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0.5, y=0.2,
                    text="© Zephyr Analytics",
                    showarrow=False,
                    font=dict(size=80, color="#f8f9f9"),
                    xanchor='center',
                    yanchor='bottom',
                    opacity=0.5
                )
            ]
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
        results_serializable = {f"MA_{key[0]}_Freq_{key[1]}": value for key, value in results.items()}
        with open(full_path, 'w') as json_file:
            json.dump(results_serializable, json_file, indent=4)
        print(f"Results successfully saved to {full_path}")
