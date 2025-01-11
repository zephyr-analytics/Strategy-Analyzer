"""
Backtesting processor module.
"""

import datetime
import logging

import pandas as pd

from logger import logger
from data.portfolio_data import PortfolioData
from models.models_data import ModelsData
from models.backtest_models.backtesting_processor import BacktestingProcessor
from results.results_processor import ResultsProcessor

logger = logging.getLogger(__name__)


class MovingAverageBacktestProcessor(BacktestingProcessor):
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA).
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        """
        Initializes the BacktestStaticPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data)

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        logger.info(f"Moving Average backtest for: {self.weights_filename}, Trading Freq:{self.trading_frequency}, Moving Average:{self.ma_period}, Type:{self.ma_type}")
        all_adjusted_weights, portfolio_values, portfolio_returns = self.run_backtest()
        self._persist_portfolio_data(
            all_adjusted_weights=all_adjusted_weights,
            portfolio_values=portfolio_values,
            portfolio_returns=portfolio_returns
        )
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self._calculate_benchmark()
        self.persist_data()
        if self.processing_type.endswith("BACKTEST"):
            results_processor = ResultsProcessor(self.data_models)
            results_processor.plot_portfolio_value()
            results_processor.plot_var_cvar()
            results_processor.plot_returns_heatmaps()

    def get_portfolio_assets_and_weights(self, current_date):
        """
        """
        adjusted_weights = self.adjust_weights(current_date=current_date)

        return adjusted_weights

    def calculate_momentum(self, current_date: datetime=None):
        pass

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
        adjusted_weights = self.assets_weights.copy() if selected_assets is None else selected_assets.copy()
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

        for ticker, weight in list(adjusted_weights.items()):
            if ticker in self.asset_data.columns and is_below_ma(ticker, self.asset_data):
                replacement_asset = get_replacement_asset()
                if replacement_asset:
                    adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + weight
                    adjusted_weights[ticker] = 0

        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for ticker in adjusted_weights:
                adjusted_weights[ticker] /= total_weight

        return adjusted_weights
