"""
Module for backtesting momentum assets.
"""

import datetime
import logging

import numpy as np
import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.models.backtest_models.backtesting_processor import BacktestingProcessor
from strategy_analyzer.results.models_results import ModelsResults

logger = logging.getLogger(__name__)


class InstitutionalBacktestProcessor(BacktestingProcessor):
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


    def get_portfolio_assets_and_weights(self, current_date, use_momentum=False):
        """
        Select portfolio assets and adjust their weights based on momentum and excess return criteria.
        Assets are ranked by momentum, and those with excess return constraints are filtered.
        If an asset has momentum greater than 1.0, it is replaced with a fallback asset.

        Parameters
        ----------
        current_date : str or pd.Timestamp
            The date at which to calculate asset selection and weighting.
        use_momentum : bool, optional
            If False, momentum values are set to 1 for all assets instead of being calculated. Default is True.

        Returns
        -------
        pd.Series
            A Series representing the adjusted portfolio weights for selected assets.
        """
        asset_data = self.data_portfolio.assets_data.copy()
        risk_free_data = self.data_portfolio.cash_data.copy()

        if use_momentum:
            momentum = self.calculate_momentum(current_date=current_date, asset_data=asset_data)
        else:
            momentum = pd.Series(1, index=asset_data.columns)

        excess_return = self.calculate_excess_return(
            current_date=current_date,
            asset_data=asset_data,
            risk_free_data=risk_free_data
        )

        selected_index = momentum.sort_values(ascending=False).index
        excess_return_selected = excess_return.reindex(selected_index)

        selected_assets = pd.DataFrame({
            'Asset': selected_index,
            'Momentum': momentum.loc[selected_index].values,
            'Excess_Return': excess_return_selected.values
        })

        adjusted_weights = self.adjust_weights(current_date=current_date, selected_assets=selected_assets)

        return adjusted_weights


    def calculate_momentum(self, current_date: datetime, asset_data: pd.DataFrame) -> pd.Series:
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
        momentum_data = asset_data.pct_change().dropna()
        periods = [21, 63, 126, 189, 252]
        momentum_values = [(momentum_data.loc[:current_date].iloc[-p:] + 1).prod() - 1 for p in periods]

        return sum(momentum_values) / len(periods)


    def calculate_excess_return(self, current_date, asset_data, risk_free_data):
        """
        Calculate the excess return over the risk-free rate for each asset.
        The excess return is calculated over fixed time periods.

        Returns
        -------
        pd.Series
            A Series where index = asset tickers, values = excess return scores.
        """
        asset_prices = asset_data
        risk_free_prices = risk_free_data

        asset_prices = asset_prices.pct_change().dropna()
        risk_free_prices = risk_free_prices.pct_change().dropna()

        asset_prices = asset_prices.loc[:current_date]
        risk_free_prices = risk_free_prices.loc[:current_date]

        risk_free_ticker = risk_free_prices.columns[0]
        risk_free_prices = risk_free_prices[risk_free_ticker]

        if risk_free_ticker in asset_prices.columns:
            asset_prices = asset_prices.drop(columns=[risk_free_ticker])

        periods = [21, 63]

        excess_return_values = {}

        for asset in asset_prices.columns:
            excess_return_list = []

            for p in periods:
                if len(asset_prices) >= p and len(risk_free_prices) >= p:
                    asset_return = (asset_prices.iloc[-p:].add(1).prod() - 1)[asset]
                    risk_free_return = (risk_free_prices.iloc[-p:].add(1).prod() - 1)

                    excess_return = asset_return - risk_free_return
                    excess_return_list.append(excess_return)

            excess_return_values[asset] = sum(excess_return_list) / len(excess_return_list) if excess_return_list else 0

        return pd.Series(excess_return_values, name="Excess Return")


    def get_replacement_asset(self, current_date):
        """
        Determines the replacement asset (cash or bond) based on SMA, momentum, and excess return criteria.
        """
        bond_ticker = self.data_models.bond_ticker
        cash_ticker = self.data_models.cash_ticker

        if bond_ticker and bond_ticker in self.data_portfolio.bond_data.columns:
            bond_momentum = self.calculate_momentum(
                current_date=current_date, asset_data=self.data_portfolio.bond_data.copy()
            ).get(bond_ticker, 0)
            cash_momentum = self.calculate_momentum(
                current_date=current_date, asset_data=self.data_portfolio.cash_data.copy()
            ).get(cash_ticker, 0)

            bond_excess_return = self.calculate_excess_return(
                current_date,
                self.data_portfolio.bond_data,
                self.data_portfolio.cash_data
            ).get(bond_ticker, 0)

            if (
                not utilities.is_below_ma(
                    current_date=current_date,
                    ticker=bond_ticker,
                    data=self.data_portfolio.bond_data,
                    ma_type=self.data_models.ma_type,
                    ma_window=self.data_models.ma_window,
                )
                and bond_momentum > cash_momentum
                and bond_excess_return > 0
            ):
                return bond_ticker

        return cash_ticker


    def compute_weight_factors(self, base_weights: pd.Series, momentum: pd.Series, excess_return: pd.Series) -> pd.Series:
        """
        Computes weight adjustment factors based on asset ranking for momentum, excess return, and volatility.
        This method does not remove weights but only modifies existing weights based on ranking.

        Returns:
            adjusted_weights (pd.Series): The modified weights after ranking-based adjustments.
        """
        ranked_momentum = momentum.rank(ascending=False)
        ranked_excess_return = excess_return.rank(ascending=False)

        adjusted_weights_momentum = base_weights.copy()
        adjusted_weights_excess_return = base_weights.copy()

        top_momentum_indices = ranked_momentum.nlargest(self.data_models.asset_shift).index
        top_excess_return_indices = ranked_excess_return.nlargest(self.data_models.asset_shift).index

        bottom_momentum_indices = ranked_momentum.nsmallest(self.data_models.asset_shift).index
        bottom_excess_return_indices = ranked_excess_return.nsmallest(self.data_models.asset_shift).index

        adjusted_weights_momentum.loc[top_momentum_indices] *= self.data_models.positive_adjustment
        adjusted_weights_excess_return.loc[top_excess_return_indices] *= self.data_models.positive_adjustment

        adjusted_weights_momentum.loc[bottom_momentum_indices] *= self.data_models.negative_adjustment
        adjusted_weights_excess_return.loc[bottom_excess_return_indices] *= self.data_models.negative_adjustment

        adjusted_weights = (adjusted_weights_momentum + adjusted_weights_excess_return) / 2

        return adjusted_weights


    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame = None,
            selected_out_of_market_assets: pd.DataFrame = None
    ) -> dict:
        """
        Adjusts the weights of the assets based on independent momentum, excess return, 
        volatility, and SMA filtering, while incorporating ranking-based weighting adjustments.
        """
        selected_assets = selected_assets.set_index("Asset")

        momentum = selected_assets["Momentum"]
        excess_return = selected_assets["Excess_Return"]

        if self.data_models.ma_threshold_asset:
            if utilities.is_below_ma(
                current_date=current_date,
                ticker=self.data_models.ma_threshold_asset,
                data=self.data_portfolio.ma_threshold_data.copy(),
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            ):
                replacement_asset = self.get_replacement_asset(current_date=current_date)
                if replacement_asset:
                    return {replacement_asset: 1.0}

        final_weights = pd.Series(self.data_models.assets_weights).copy()
        final_weights = final_weights.loc[final_weights.index.intersection(momentum.index)]

        adjusted_weights = self.compute_weight_factors(final_weights, momentum, excess_return)

        negative_momentum = momentum < 0
        adjusted_weights[negative_momentum] = 0

        negative_excess_return = excess_return < 0
        adjusted_weights[negative_excess_return] = 0

        adjusted_weights /= adjusted_weights.sum()

        below_sma = selected_assets.index[selected_assets.index.map(
            lambda ticker: utilities.is_below_ma(
                current_date=current_date,
                ticker=ticker,
                data=self.data_portfolio.assets_data,
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            )
        )]

        adjusted_weights[below_sma] = 0

        if adjusted_weights.sum() == 0:
            replacement_asset = self.get_replacement_asset(current_date=current_date)
            if replacement_asset:
                return {replacement_asset: 1.0}
        else:
            removed_weight = 1 - adjusted_weights.sum()
            replacement_asset = self.get_replacement_asset(current_date=current_date)

            if replacement_asset:
                adjusted_weights[replacement_asset] = removed_weight

            total_weight = adjusted_weights.sum()
            
            if total_weight > 0:
                adjusted_weights = {
                    ticker: weight / total_weight for ticker, weight in adjusted_weights.items()
                }
            else:
                return {replacement_asset: 1.0}

        return adjusted_weights
