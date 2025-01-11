"""
Module for creating momentum based parameters.
"""

from multiprocessing import Pool

import plotly.express as px

import utilities as utilities
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
from models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from models.backtest_models.iao_momentum_backtest_processor import IAOMomentumBacktestProcessor
from results.models_results import ModelsResults


class InAndOutMomentumParameterTuning(ParameterTuningProcessor):
    """
    Processor for parameter tuning based on the a momentum portfolio.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the parameter tuning class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)

    def get_portfolio_results(self) -> dict:
        """
        Processes parameters for tuning using joblib to parallelize execution.

        Returns
        -------
        dict
            A dictionary of backtest results and portfolio statistics from parameter tuning.
        """
        results = {}
        ma_list = [21, 42, 63, 84, 105, 126, 147, 168, 189, 210, 231, 252]
        num_asset_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        trading_frequencies = ["Monthly", "Bi-Monthly", "Quarterly", "Yearly"]
        ma_types = ["SMA", "EMA"]

        total_assets = len(self.data_models.assets_weights)

        parameter_combinations = [
            (ma, frequency, num_assets, ma_type)
            for ma in ma_list
            for frequency in trading_frequencies
            for num_assets in num_asset_list if num_assets <= total_assets
            for ma_type in ma_types
        ]

        with Pool() as pool:
            parallel_results = pool.starmap(self.process_combination, parameter_combinations)

        for params, result in zip(parameter_combinations, parallel_results):
            results[params] = result

        return results

    def process_combination(self, ma, frequency, num_assets, ma_type) -> dict:
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
        self.data_models.num_assets_to_select = num_assets
        self.data_models.ma_type = ma_type

        backtest = IAOMomentumBacktestProcessor(models_data=self.data_models, portfolio_data=self.data_portfolio)
        backtest.process()

        return {
            "cagr": self.data_models.cagr,
            "average_annual_return": self.data_models.average_annual_return,
            "max_drawdown": self.data_models.max_drawdown,
            "var": self.data_models.var,
            "cvar": self.data_models.cvar,
            "annual_volatility": self.data_models.annual_volatility,
        }

# TODO this needs to be moved to the results processor.
    def plot_results(self, results: dict):
        """
        Plot results from the momentum strategy testing.

        Parameters
        ----------
        results : dict
            Dictionary of results from parameter tuning.
        """
        data = {
            "Momentum_Strategy": [
                f"MA:{key[0]} Freq:{key[1]} Assets:{key[2]} Type:{key[3]}" for key in results.keys()
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
            hover_data=['Momentum_Strategy', 'max_drawdown', 'var', 'cvar', "average_annual_return"],
            labels={
                "cagr": "Compound Annual Growth Rate",
                "annual_volatility": "Annual Volatility",
                "max_drawdown": "Maximum Drawdown",
                "cvar": "Conditional Value at Risk",
                "var": "Value at Risk",
                "sharpe_ratio": "Sharpe Ratio",
                "average_annual_return": "Annualized Return"
            },
            title=f"Possible In and Out Momentum Strategies - {self.portfolio_name}"
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
