"""
Module for backtesting momentum assets.
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
        Select portfolio assets and adjust their weights based on momentum and custom rules.
        If an asset has momentum greater than 1.0, replace it with a fallback asset.
        """
        momentum = self.calculate_momentum(current_date=current_date)

        selected_assets = pd.DataFrame({
            'Asset': momentum.nlargest(self.data_models.num_assets_to_select).index,
            'Momentum': momentum.nlargest(self.data_models.num_assets_to_select).values
        })
        print(selected_assets)
        adjusted_weights = self.adjust_weights(current_date=current_date, selected_assets=selected_assets)
        # adjusted_weights = utilities.calculate_conditional_value_at_risk_weighting(
        #     returns_df=self.data_portfolio.assets_data.copy().pct_change().dropna(),
        #     weights=adjusted_weights,
        #     confidence_level=0.95,
        #     cash_ticker=self.data_models.cash_ticker,
        #     bond_ticker=self.data_models.bond_ticker
        # )
        # print(adjusted_weights)
        return adjusted_weights

    def calculate_momentum(self, current_date: datetime) -> pd.Series:
        """
        Calculate average momentum based on 1, 3, 6, 9, and 12-month cumulative returns.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        pd.Series
            Series of momentum values for each asset.
        """
        momentum_data = self.data_portfolio.assets_data.pct_change().dropna()
        periods = [21, 63, 126, 189, 252]

        momentum_values = [(momentum_data.loc[:current_date].iloc[-p:] + 1).prod() - 1 for p in periods]

        return sum(momentum_values) / len(periods)

    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame=None,
            selected_out_of_market_assets: pd.DataFrame=None
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

        adjusted_weights = {}
        total_weight = 0

        for _, row in selected_assets.iterrows():
            asset = row['Asset']
            momentum = row['Momentum']

            if (
                (self.data_models.negative_mom and momentum <= 0)
                or utilities.is_below_ma(
                    current_date=current_date,
                    ticker=asset,
                    data=self.data_portfolio.assets_data,
                    ma_type=self.data_models.ma_type,
                    ma_window=self.data_models.ma_window,
                )
            ):
                replacement_asset = get_replacement_asset(current_date=current_date)
                if replacement_asset:
                    adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + 1
            else:
                adjusted_weights[asset] = adjusted_weights.get(asset, 0) + 1

            total_weight += 1

        adjusted_weights = {
            ticker: weight / total_weight for ticker, weight in adjusted_weights.items()
        }

        return adjusted_weights
