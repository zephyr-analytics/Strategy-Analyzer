"""
Backtesting processor module.
"""

import datetime
import logging

import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.models.backtest_models.backtesting_processor import BacktestingProcessor
from strategy_analyzer.results.models_results import ModelsResults

logger = logging.getLogger(__name__)


class MovingAverageBacktestProcessor(BacktestingProcessor):
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA).
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the BacktestStaticPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)

    def get_portfolio_assets_and_weights(self, current_date):
        """
        """
        adjusted_weights = self.adjust_weights(current_date=current_date)

        return adjusted_weights

    def calculate_momentum(self, current_date: datetime=None):
        pass

    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame =None,
            selected_out_of_market_asset: pd.DataFrame=None
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
        adjusted_weights = self.data_models.assets_weights.copy() if selected_assets is None else selected_assets.copy()

        def get_replacement_asset(current_date):
            """
            Determines the replacement asset (cash or bond) based on the moving average (MA) threshold.

            Parameters
            ----------
            current_date : datetime
                The current date for which to evaluate the MA condition.

            Returns
            -------
            str or None
                The replacement asset ticker, either a bond or cash ticker. Returns None if no valid replacement asset is found.
            """
            if (
                self.data_models.bond_ticker
                and self.data_models.bond_ticker in self.data_portfolio.bond_data.columns
            ):
                if not utilities.is_below_ma(
                    current_date=current_date,
                    ticker=self.data_models.bond_ticker,
                    data=self.data_portfolio.bond_data,
                    ma_type=self.data_models.ma_type,
                    ma_window=self.data_models.ma_window,
                ):
                    return self.data_models.bond_ticker

            return self.data_models.cash_ticker

        if self.data_models.ma_threshold_asset:
            if utilities.is_below_ma(
                current_date=current_date,
                ticker=self.data_models.ma_threshold_asset,
                data=self.data_portfolio.ma_threshold_data,
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            ):
                replacement_asset = get_replacement_asset(current_date=current_date)
                if replacement_asset:
                    return {replacement_asset: 1.0}

        for ticker, weight in list(adjusted_weights.items()):
            if (
                ticker in self.data_portfolio.assets_data.columns
                and utilities.is_below_ma(
                    current_date=current_date,
                    ticker=ticker,
                    data=self.data_portfolio.assets_data,
                    ma_type=self.data_models.ma_type,
                    ma_window=self.data_models.ma_window,
                )
            ):
                replacement_asset = get_replacement_asset(current_date=current_date)
                if replacement_asset:
                    adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + weight
                    adjusted_weights[ticker] = 0

        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for ticker in adjusted_weights:
                adjusted_weights[ticker] /= total_weight

        return adjusted_weights
