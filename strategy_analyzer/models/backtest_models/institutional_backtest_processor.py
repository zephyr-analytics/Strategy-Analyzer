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

    def get_portfolio_assets_and_weights(self, current_date):
        """
        Select portfolio assets and adjust their weights based on momentum and excess return criteria.
        Assets are ranked by momentum, and those with excess return constraints are filtered.
        If an asset has momentum greater than 1.0, it is replaced with a fallback asset.
        
        Parameters
        ----------
        current_date : str or pd.Timestamp
            The date at which to calculate asset selection and weighting.

        Returns
        -------
        pd.Series
            A Series representing the adjusted portfolio weights for selected assets.
        """
        momentum = self.calculate_momentum(current_date=current_date)
        excess_return = self.calculate_excess_return(current_date=current_date)

        selected_index = momentum.nlargest(self.data_models.num_assets_to_select).index

        excess_return_selected = excess_return.reindex(selected_index)
        print(excess_return_selected)
        selected_assets = pd.DataFrame({
            'Asset': selected_index,
            'Momentum': momentum.loc[selected_index].values,
            'Excess_Return': excess_return_selected.values
        })

        print(selected_assets)

        adjusted_weights = self.adjust_weights(current_date=current_date, selected_assets=selected_assets)

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

    def calculate_excess_return(self, current_date):
        """
        Calculate the excess return over the risk-free rate for each asset.
        The excess return is calculated over fixed time periods.

        Returns
        -------
        pd.Series
            A Series where index = asset tickers, values = excess return scores.
        """
        asset_prices = self.data_portfolio.assets_data.dropna()
        risk_free_prices = self.data_portfolio.cash_data.dropna()

        asset_prices = asset_prices.loc[:current_date]
        risk_free_prices = risk_free_prices.loc[:current_date]

        if asset_prices.empty or risk_free_prices.empty:
            return pd.Series(0, index=asset_prices.columns)

        risk_free_ticker = risk_free_prices.columns[0]
        risk_free_prices = risk_free_prices[risk_free_ticker]

        if risk_free_ticker in asset_prices.columns:
            asset_prices = asset_prices.drop(columns=[risk_free_ticker])

        periods = [21, 63, 126, 189, 252]

        excess_return_values = {}

        for asset in asset_prices.columns:
            excess_return_list = []

            for p in periods:
                if len(asset_prices) >= p and len(risk_free_prices) >= p:
                    asset_return = (asset_prices.iloc[-1, asset_prices.columns.get_loc(asset)] / 
                                    asset_prices.iloc[-p, asset_prices.columns.get_loc(asset)]) - 1
                    risk_free_return = (risk_free_prices.iloc[-1] / risk_free_prices.iloc[-p]) - 1

                    excess_return = asset_return - risk_free_return
                    excess_return_list.append(excess_return)

            if excess_return_list:
                excess_return_values[asset] = sum(excess_return_list) / len(excess_return_list)
            else:
                excess_return_values[asset] = 0

        return pd.Series(excess_return_values, name="Excess Return")


    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame = None,
            selected_out_of_market_assets: pd.DataFrame = None
    ) -> dict:
        """
        Adjusts the weights of the assets based on momentum, excess return, and SMA filtering.
        """

        def get_replacement_asset(current_date):
            """
            Determines the replacement asset (cash or bond) based on SMA threshold.
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

        # Start with the selected assets from the previous step
        selected_assets = selected_assets.set_index("Asset")
        
        # Extract momentum and excess return for selected assets
        momentum = selected_assets["Momentum"]
        excess_return = selected_assets["Excess_Return"]

        # Filter assets that are in the available weight dictionary
        final_weights = pd.Series(self.data_models.assets_weights).copy()
        final_weights = final_weights.loc[final_weights.index.intersection(momentum.index)]

        # Identify assets with negative excess returns and remove them
        excess_return_negative = excess_return < 0
        removed_weight = final_weights[excess_return_negative].sum()
        final_weights[excess_return_negative] = 0  

        # Rank momentum and excess return within the selected assets
        ranked_momentum = momentum.rank(ascending=False)
        ranked_excess_return = excess_return.rank(ascending=False)

        # Adjust weights using ranking-based multipliers
        weight_factors = pd.Series(1, index=final_weights.index)
        weight_factors[(ranked_momentum <= 3) | (ranked_excess_return <= 3)] *= 2
        weight_factors[(ranked_momentum > len(momentum) - 3) | (ranked_excess_return > len(momentum) - 3)] /= 2
        final_weights *= weight_factors

        below_sma = selected_assets.index[selected_assets.index.map(
            lambda ticker: utilities.is_below_ma(
                current_date=current_date,
                ticker=ticker,
                data=self.data_portfolio.assets_data,  # Ensure the correct data source
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            )
        )]

        # Remove weight for assets below SMA
        removed_weight += final_weights[below_sma].sum()
        final_weights[below_sma] = 0 

        # If all assets are removed, allocate fully to replacement asset (bond/cash)
        if final_weights.sum() == 0:
            replacement_asset = get_replacement_asset(current_date=current_date)
            if replacement_asset:
                return {replacement_asset: 1.0}

        # Allocate the removed weight to cash
        final_weights[self.data_models.cash_ticker] = removed_weight
        final_weights = final_weights.div(final_weights.sum()).fillna(0)

        return final_weights.to_dict()
