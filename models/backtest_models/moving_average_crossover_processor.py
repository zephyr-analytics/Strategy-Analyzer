"""
Moving Average Crossover Backtesting Processor.
"""

import logging
import datetime

import pandas as pd

from logger import logger
from data.portfolio_data import PortfolioData
from models.models_data import ModelsData
from models.backtest_models.backtesting_processor import BacktestingProcessor
from results.models_results import ModelsResults
from results.results_processor import ResultsProcessor

logger = logging.getLogger(__name__)


class MovingAverageCrossoverProcessor(BacktestingProcessor):
    """
    A class to backtest a portfolio using a moving average crossover strategy.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the Moving Average Crossover Backtest Processor.

        Parameters
        ----------
        models_data : ModelsData
            Contains all relevant parameters and data for backtesting.
        portfolio_data : PortfolioData
            Portfolio data required for backtesting.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)

    def get_portfolio_assets_and_weights(self, current_date):
        """
        """
        adjusted_weights = self.adjust_weights(current_date=current_date)

        return adjusted_weights

    def calculate_momentum(self, current_date: datetime=None):
        pass

    def calculate_moving_averages(self, data, period):
        """
        Calculates the moving average based on the specified type.

        Parameters
        ----------
        data : DataFrame
            The DataFrame containing price data.
        period : int
            The period for calculating the moving average.

        Returns
        -------
        Series
            The moving average values.
        """
        if self.ma_type == "SMA":
            return data.rolling(window=period).mean()
        elif self.ma_type == "EMA":
            return data.ewm(span=period).mean()
        else:
            raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

    def is_below_ma(self, ticker, data, current_date):
        """
        Checks if the price of the given ticker is below its moving average.

        Parameters
        ----------
        ticker : str
            The ticker to check.
        data : DataFrame
            The DataFrame containing the ticker's data.
        current_date : datetime
            The current date for which the check is performed.

        Returns
        -------
        bool
            True if the price is below the moving average, False otherwise.
        """
        # TODO I am not certain this implementation is corret.
        price = data.loc[:current_date, ticker].iloc[-1]
        if self.ma_type == "SMA":
            ma = data.loc[:current_date, ticker].rolling(window=self.slow_ma_period).mean().iloc[-1]
        elif self.ma_type == "EMA":
            ma = data.loc[:current_date, ticker].ewm(span=self.slow_ma_period).mean().iloc[-1]
        else:
            raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

        return price < ma

    def adjust_weights(
            self, current_date: datetime, selected_assets: pd.DataFrame =None, selected_out_of_market_asset: pd.DataFrame=None
    ) -> dict:
        """
        Adjusts the weights of the assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : dict or None
            Optional preselected assets with weights. If None, uses `self.assets_weights`.
        selected_out_of_market_asset : dict or None
            Optional out-of-market assets to be used when replacing assets.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        fast_ma = self.calculate_moving_averages(self.asset_data.loc[:current_date], self.fast_ma_period)
        slow_ma = self.calculate_moving_averages(self.asset_data.loc[:current_date], self.slow_ma_period)

        adjusted_weights = self.assets_weights.copy()

        for ticker, weight in list(adjusted_weights.items()):
            if fast_ma[ticker].iloc[-1] > slow_ma[ticker].iloc[-1]:
                adjusted_weights[ticker] = weight
            else:
                replacement_asset = None
                if self.cash_ticker and self.is_below_ma(self.cash_ticker, self.cash_data, current_date):
                    replacement_asset = self.cash_ticker
                elif self.bond_ticker and self.is_below_ma(self.bond_ticker, self.bond_data, current_date):
                    replacement_asset = self.bond_ticker

                if replacement_asset:
                    adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + weight
                    adjusted_weights[ticker] = 0

        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for ticker in adjusted_weights:
                adjusted_weights[ticker] /= total_weight

        return adjusted_weights
