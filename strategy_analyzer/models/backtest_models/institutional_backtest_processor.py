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
        self.reweight_num= 10

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
        momentum = self.calculate_momentum(
            current_date=current_date,
            asset_data=self.data_portfolio.assets_data.copy()
        )

        excess_return = self.calculate_excess_return(
            current_date=current_date,
            asset_data=self.data_portfolio.assets_data,
            risk_free_data=self.data_portfolio.cash_data
        )

        selected_index = momentum.nlargest(self.data_models.num_assets_to_select).index

        excess_return_selected = excess_return.reindex(selected_index)

        selected_assets = pd.DataFrame({
            'Asset': selected_index,
            'Momentum': momentum.loc[selected_index].values,
            'Excess_Return': excess_return_selected.values
        })

        print(selected_assets)

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


    def get_replacement_asset(self, current_date):
        """
        Determines the replacement asset (cash or bond) based on SMA, momentum, and excess return criteria.
        """
        bond_ticker = self.data_models.bond_ticker
        cash_ticker = self.data_models.cash_ticker

        if bond_ticker and bond_ticker in self.data_portfolio.bond_data.columns:
            bond_momentum = self.calculate_momentum(current_date=current_date, asset_data=self.data_portfolio.bond_data.copy()).get(bond_ticker, 0)
            cash_momentum = self.calculate_momentum(current_date=current_date, asset_data=self.data_portfolio.cash_data.copy()).get(cash_ticker, 0)

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
        Computes weight adjustment factors based on asset ranking for momentum and excess return.
        This method does not remove weights but only modifies existing weights based on ranking.

        The original base weights serve as the foundation for adjustments.

        Returns:
            adjusted_weights (pd.Series): The modified weights after ranking-based adjustments.
        """
        ranked_momentum = momentum.rank(ascending=False)
        ranked_excess_return = excess_return.rank(ascending=False)

        # Start with the original base weights
        adjusted_weights_momentum = base_weights.copy()
        adjusted_weights_excess_return = base_weights.copy()

        # Get indices of the top `reweight_num` ranked assets
        top_momentum_indices = ranked_momentum.nlargest(self.reweight_num).index
        top_excess_return_indices = ranked_excess_return.nlargest(self.reweight_num).index

        # Get indices of the bottom `reweight_num` ranked assets
        bottom_momentum_indices = ranked_momentum.nsmallest(self.reweight_num).index
        bottom_excess_return_indices = ranked_excess_return.nsmallest(self.reweight_num).index

        # Increase weight for top-ranked assets
        adjusted_weights_momentum.loc[top_momentum_indices] *= 1.5
        adjusted_weights_excess_return.loc[top_excess_return_indices] *= 1.5

        # Decrease weight for bottom-ranked assets
        adjusted_weights_momentum.loc[bottom_momentum_indices] /= 2
        adjusted_weights_excess_return.loc[bottom_excess_return_indices] /= 2

        # Take the average of both adjusted weight sets
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
        and SMA filtering, while incorporating ranking-based weighting adjustments.
        
        This method is responsible for removing weights (negative momentum, negative excess return, SMA filtering)
        and redistributing them accordingly.
        """
        selected_assets = selected_assets.set_index("Asset")

        momentum = selected_assets["Momentum"]
        excess_return = selected_assets["Excess_Return"]

        final_weights = pd.Series(self.data_models.assets_weights).copy()
        final_weights = final_weights.loc[final_weights.index.intersection(momentum.index)]

        # Apply ranking-based adjustments (without modifying base weights)
        adjusted_weights = self.compute_weight_factors(final_weights, momentum, excess_return)

        # Remove weight for assets with negative momentum or negative excess return
        negative_momentum = momentum < 0
        negative_excess_return = excess_return < 0

        adjusted_weights[negative_momentum] = 0
        adjusted_weights[negative_excess_return] = 0

        # Apply SMA filtering separately
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
        print(adjusted_weights)
        # Track removed weight after setting them to zero
        removed_weight = 1 - adjusted_weights.sum()

        # Handle case where all weights are removed
        if adjusted_weights.sum() == 0:
            replacement_asset = self.get_replacement_asset(current_date=current_date)
            if replacement_asset:
                return {replacement_asset: 1.0}

        replacement_asset = self.get_replacement_asset(current_date=current_date)
        adjusted_weights[replacement_asset] = removed_weight
        print(adjusted_weights)
        return adjusted_weights.to_dict()
