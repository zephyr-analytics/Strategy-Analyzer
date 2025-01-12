"""
Module for backtesting momentum assets.
"""

import datetime
import logging

import pandas as pd

from logger import logger
from data.portfolio_data import PortfolioData
from models.models_data import ModelsData
from models.backtest_models.backtesting_processor import BacktestingProcessor
from results.models_results import ModelsResults
from results.results_processor import ResultsProcessor

logger = logging.getLogger(__name__)


class MomentumBacktestProcessor(BacktestingProcessor):
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA).
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the BacktestMomentumPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)

    def get_portfolio_assets_and_weights(self, current_date):
        """
        """
        momentum = self.calculate_momentum(current_date=current_date)
        selected_assets = pd.DataFrame({'Asset': momentum.nlargest(self.num_assets_to_select).index, 
                                        'Momentum': momentum.nlargest(self.num_assets_to_select).values})
        selected_assets = selected_assets[selected_assets['Asset'].isin(self.assets_weights.keys())]
        adjusted_weights = self.adjust_weights(current_date=current_date, selected_assets=selected_assets)

        return adjusted_weights

    def calculate_momentum(self, current_date: datetime) -> pd.Series:
        """
        Calculate average momentum based on 3, 6, 9, and 12-month cumulative returns.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        pd.Series
            Series of momentum values for each asset.
        """
        momentum_data = self.asset_data.copy().pct_change().dropna()
        momentum_3m = (momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        return (momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 4

    def adjust_weights(
            self, current_date: datetime, selected_assets: pd.DataFrame =None, selected_out_of_market_assets: pd.DataFrame=None
    ) -> dict:
        """
        Adjusts the weights of the assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : dict or None
            Optional preselected assets with weights. If None, uses `self.assets_weights`.
        selected_out_of_market_assets : dict or None
            Optional out-of-market assets to be used when replacing assets.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        # NOTE this can be a utilities method
        def get_replacement_asset():
            """
            Determines the replacement asset (cash or bond) based on SMA.

            Returns
            -------
            str
                The replacement asset ticker.
            """
            if self.bond_ticker and self.bond_ticker in self.bond_data.columns:
                if not is_below_ma(self.bond_ticker, self.bond_data):
                    return self.bond_ticker
            return self.cash_ticker if self.cash_ticker in self.cash_data.columns else None

        # NOTE this can be a utilities method
        def is_below_ma(ticker, data):
            """
            Checks if the price of the given ticker is below its moving average.

            Parameters
            ----------
            ticker : str
                The ticker to check.
            data : DataFrame
                The DataFrame containing the ticker's data.

            Returns
            -------
            bool
                True if the price is below the moving average, False otherwise.
            """
            if ticker not in data.columns:
                return False

            price = data.loc[:current_date, ticker].iloc[-1]

            if self.ma_type == "SMA":
                ma = data.loc[:current_date, ticker].rolling(window=self.ma_period).mean().iloc[-1]
            elif self.ma_type == "EMA":
                ma = data.loc[:current_date, ticker].ewm(span=self.ma_period).mean().iloc[-1]
            else:
                raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

            return price < ma

        if not self.ma_threshold_asset:
            pass
        elif is_below_ma(self.ma_threshold_asset, self.ma_threshold_data):
            replacement_asset = get_replacement_asset()
            if replacement_asset:
                return {replacement_asset: 1.0}

        adjusted_weights = {}
        total_weight = 0

        for _, row in selected_assets.iterrows():
            asset = row['Asset']
            momentum = row['Momentum']

            if (self.filter_negative_momentum and momentum <= 0) or is_below_ma(asset, self.asset_data):
                replacement_asset = get_replacement_asset()
                if replacement_asset:
                    adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + 1
            else:
                adjusted_weights[asset] = adjusted_weights.get(asset, 0) + 1

            total_weight += 1

        adjusted_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}

        return adjusted_weights
