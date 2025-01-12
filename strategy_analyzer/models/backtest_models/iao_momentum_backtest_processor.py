"""
Module for backtesting in and out of market momentum assets.
"""

import datetime
import logging

import pandas as pd

from strategy_analyzer.logger import logger
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.backtest_models.backtesting_processor import BacktestingProcessor
from strategy_analyzer.results.models_results import ModelsResults

logger = logging.getLogger(__name__)


class IAOMomentumBacktestProcessor(BacktestingProcessor):
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA),
    with momentum calculations for both in-market and out-of-market assets.
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
        in_market_momentum, out_of_market_momentum = self.calculate_momentum(current_date=current_date)
        selected_assets = pd.DataFrame({'Asset': in_market_momentum.nlargest(self.num_assets_to_select).index, 'Momentum': in_market_momentum.nlargest(self.num_assets_to_select).values})
        selected_out_of_market_asset =pd.DataFrame({'Asset': out_of_market_momentum.nlargest(1).index, 'Momentum': out_of_market_momentum.nlargest(1).values})

        adjusted_weights = self.adjust_weights(
            current_date=current_date, selected_assets=selected_assets, selected_out_of_market_asset=selected_out_of_market_asset
        )

        return adjusted_weights

    def calculate_momentum(self, current_date: datetime) -> tuple:
        """
        Calculate average momentum based on 3, 6, 9, and 12-month cumulative returns for both in-market and out-of-market assets.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        tuple
            in_market_momentum and out_of_market_momentum
        """
        momentum_data = self.asset_data.copy().pct_change().dropna()
        momentum_3m = (momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        in_market_momentum = (momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 4

        momentum_data_out_of_market = self.out_of_market_data.copy().pct_change().dropna()
        momentum_3m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-252:] + 1).prod() - 1
        out_of_market_momentum = (momentum_3m_out + momentum_6m_out + momentum_9m_out + momentum_12m_out) / 4

        return in_market_momentum, out_of_market_momentum

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
        adjusted_weights = {}

        def is_below_ma(ticker: str, data: pd.DataFrame) -> bool:
            """
            Checks if the asset's price is below its moving average.

            Parameters
            ----------
            ticker : str
                The ticker to check.
            data : pd.DataFrame
                Data containing the asset's price history.

            Returns
            -------
            bool
                True if the price is below the moving average, False otherwise.
            """
            if ticker not in data.columns:
                return True

            price = data.loc[:current_date, ticker].iloc[-1]

            if self.ma_type == "SMA":
                ma = data.loc[:current_date, ticker].rolling(window=self.ma_period).mean().iloc[-1]
            elif self.ma_type == "EMA":
                ma = data.loc[:current_date, ticker].ewm(span=self.ma_period).mean().iloc[-1]
            else:
                raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

            return price < ma

        def allocate_to_safe_asset(weight: float):
            """
            Allocates weights to the selected out-of-market asset if it is above its moving average,
            otherwise falls back to bonds or cash.

            Parameters
            ----------
            weight : float
                Weight to be allocated.
            """
            if not is_below_ma(selected_out_of_market_asset['Asset'].iloc[0], self.out_of_market_data):
                adjusted_weights[selected_out_of_market_asset['Asset'].iloc[0]] = adjusted_weights.get(selected_out_of_market_asset['Asset'].iloc[0], 0) + weight
            elif not is_below_ma(self.bond_ticker, self.bond_data):
                adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + weight
            else:
                adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + weight

        if self.ma_threshold_asset and is_below_ma(self.ma_threshold_asset, self.ma_threshold_data):
            allocate_to_safe_asset(1.0)
            return adjusted_weights

        for _, row in selected_assets.iterrows():
            asset, momentum = row['Asset'], row['Momentum']
            weight = 1 / len(selected_assets)
            if self.filter_negative_momentum and momentum <= 0 or is_below_ma(asset, self.asset_data):
                allocate_to_safe_asset(weight)
            else:
                adjusted_weights[asset] = weight

        total_weight = sum(adjusted_weights.values())
        adjusted_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}

        return adjusted_weights
