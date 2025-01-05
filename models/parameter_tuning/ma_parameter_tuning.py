"""
Module for creating ma based parameters.
"""

import os
import json
from multiprocessing import Pool

import plotly.express as px

import utilities as utilities
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
from models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from models.backtest_models.moving_average_backtest_processor import MovingAverageBacktestProcessor


class MaParameterTuning(ParameterTuningProcessor):
    """
    Processor for parameter tuning based on the a momentum portfolio.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        """
        Initializes the parameter tuning class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data)
        self.theme = models_data.theme_mode
        self.portfolio_name = models_data.weights_filename

    def process(self):
        """
        Method for processing within the momentum parameter tuning class.
        """
        results = self.get_portfolio_results()
        self.plot_results(results=results)
        self.persist_results(results=results)

    def get_portfolio_results(self) -> dict:
        results = {}
        ma_list = [21, 42, 63, 84, 105, 126, 147, 168, 189, 210, 231, 252]
        trading_frequencies = ["Monthly", "Bi-Monthly", "Quarterly", "Yearly"]
        ma_types = ["SMA", "EMA"]

        parameter_combinations = [
            (ma, frequency, ma_type) 
            for ma in ma_list 
            for frequency in trading_frequencies 
            for ma_type in ma_types
        ]

        with Pool() as pool:
            parallel_results = pool.starmap(self.process_combination, parameter_combinations)

        for params, result in zip(parameter_combinations, parallel_results):
            results[params] = result

        return results

    def process_combination(self, ma, frequency, ma_type) -> dict:
        """
        Processes a single parameter combination and returns the backtest results.

        Parameters
        ----------
        ma : int
            Moving average window.
        frequency : str
            Trading frequency.
        num_assets : int
            Number of assets to select.
        ma_type : str
            Type of moving average (SMA or EMA).

        Returns
        -------
        dict
            The backtest results for the given parameter combination.
        """
        self.data_models.ma_window = ma
        self.data_models.trading_frequency = frequency
        self.data_models.ma_type = ma_type

        backtest = MovingAverageBacktestProcessor(models_data=self.data_models, portfolio_data=self.data_portfolio)
        backtest.process()

        return {
            "cagr": self.data_models.cagr,
            "average_annual_return": self.data_models.average_annual_return,
            "max_drawdown": self.data_models.max_drawdown,
            "var": self.data_models.var,
            "cvar": self.data_models.cvar,
            "annual_volatility": self.data_models.annual_volatility,
        }

    def plot_results(self, results: dict):
        """
        Plot results from the momentum strategy testing.

        Parameters
        ----------
        results : dict
            Dictionary of results from parameter tuning.
        """
        data = {
            "Moving_Average_Strategy": [
                f"MA:{key[0]} Freq:{key[1]} Type:{key[2]}" for key in results.keys()
            ],
            "cagr": [round(v["cagr"] * 100, 2) for v in results.values()],
            "average_annual_return": [round(v["average_annual_return"] * 100, 2) for v in results.values()],
            "annual_volatility": [round(v["annual_volatility"] * 100, 2) for v in results.values()],
            "max_drawdown": [round(v["max_drawdown"] * 100, 2) for v in results.values()],
            "var": [round(v["var"] * 100, 2) for v in results.values()],
            "cvar": [round(v["cvar"] * 100, 2) for v in results.values()],
            "sharpe_ratio": [
                round(v["cagr"] / v["annual_volatility"], 2) if v["annual_volatility"] != 0 else None
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
            hover_data=['Moving_Average_Strategy', 'max_drawdown', 'var', 'cvar', "average_annual_return"],
            labels={
                "cagr": "Compound Annual Growth Rate",
                "annual_volatility": "Annual Volatility",
                "max_drawdown": "Maximum Drawdown",
                "cvar": "Conditional Value at Risk",
                "var": "Value at Risk",
                "sharpe_ratio": "Sharpe Ratio",
                "average_annual_return": "Annualized Return"
            },
            title=f"Possible Moving Average Strategies - {self.portfolio_name}"
        )
        chart_theme = "plotly_dark" if self.theme.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            coloraxis_colorbar_title="Sharpe Ratio",
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
            The dictionary containing momentum backtest results and portfolio statistics.
        """
        current_directory = os.getcwd()
        artifacts_directory = os.path.join(current_directory, "artifacts", "data")
        os.makedirs(artifacts_directory, exist_ok=True)

        full_path = os.path.join(artifacts_directory, "sma_parameter_tune.json")
        results_serializable = {f"MA_{key[0]}_Freq_{key[1]}": value for key, value in results.items()}
        with open(full_path, 'w') as json_file:
            json.dump(results_serializable, json_file, indent=4)
        print(f"Results successfully saved to {full_path}")
