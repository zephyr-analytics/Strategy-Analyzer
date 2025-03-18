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
        Select portfolio assets and adjust their weights based solely on excess return criteria.

        Parameters
        ----------
        current_date : str or pd.Timestamp
            The date at which to calculate asset selection and weighting.

        Returns
        -------
        pd.Series
            A Series representing the adjusted portfolio weights for selected assets.
        """
        asset_data = self.data_portfolio.assets_data.copy()
        risk_free_data = self.data_portfolio.cash_data.copy()

        excess_return = self.calculate_excess_return(
            current_date=current_date,
            asset_data=asset_data,
            risk_free_data=risk_free_data
        )

        selected_index = excess_return.sort_values(ascending=False).index

        selected_assets = pd.DataFrame({
            'Asset': selected_index,
            'Excess_Return': excess_return.loc[selected_index].values
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
        pass


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

        periods = [21, 63, 126]

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
                and bond_excess_return > 0
            ):
                return bond_ticker

        return cash_ticker

    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame = None
    ) -> dict:
        """
        Adjusts the weights of the assets while retaining the existing weights of qualifying assets.
        Any removed weight is allocated to the replacement asset determined by get_replacement_asset.
        The original weights of qualifying assets remain constant.
        """
        # Initialize adjusted_weights from the data models directly
        adjusted_weights = self.data_models.assets_weights.copy()

        if self.data_models.ma_threshold_asset:
            if utilities.is_below_ma(
                current_date=current_date,
                ticker=self.data_models.ma_threshold_asset,
                data=self.data_portfolio.ma_threshold_data,
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            ):
                replacement_asset = self.get_replacement_asset(current_date=current_date)
                if replacement_asset:
                    return {replacement_asset: 1.0}

        # Create a set of assets with positive excess returns from selected_assets
        if selected_assets is not None:
            assets_with_positive_excess_return = set(selected_assets[selected_assets['Excess_Return'] > 0]['Asset'])
            # Retain only assets with positive excess returns
            qualifying_assets = {
                asset: weight for asset, weight in adjusted_weights.items()
                if asset in assets_with_positive_excess_return
            }
        else:
            qualifying_assets = adjusted_weights.copy()

        # Apply the moving average (MA) filter
        below_sma = [
            ticker for ticker in qualifying_assets.keys()
            if utilities.is_below_ma(
                current_date=current_date,
                ticker=ticker,
                data=self.data_portfolio.assets_data.copy(),
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            )
        ]

        # Drop assets that are below their SMA
        final_weights = {
            asset: weight for asset, weight in qualifying_assets.items()
            if asset not in below_sma
        }

        # Calculate the removed weight
        removed_weight = sum(adjusted_weights.values()) - sum(final_weights.values())

        # Get the replacement asset for removed weight
        replacement_asset = self.get_replacement_asset(current_date=current_date)
        if removed_weight > 0 and replacement_asset:
            final_weights[replacement_asset] = removed_weight

        # Ensure weights sum to 1
        total_weight = sum(final_weights.values())
        if total_weight > 0:
            final_weights = {ticker: weight for ticker, weight in final_weights.items()}

        return final_weights
