"""
Backtesting processor module.
"""

import logging

import pandas as pd

import utilities as utilities
from processing_types import run_types
from logger import logger
from results.results_processor import ResultsProcessor
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
from models.backtest_models.backtesting_processor import BacktestingProcessor

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
        self.run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self._calculate_benchmark()
        self.persist_data()
        if self.processing_type == run_types.Runs.BACKTEST:
            results_processor = ResultsProcessor(self.data_models)
            results_processor.plot_portfolio_value()
            results_processor.plot_var_cvar()
            results_processor.plot_returns_heatmaps()
        else:
            pass

    def calculate_momentum(self, current_date=None):
        pass

    def adjust_weights(self, current_date, selected_assets=None, selected_out_of_market_assets=None) -> dict:
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
        adjusted_weights = self.assets_weights.copy() if selected_assets is None else selected_assets.copy()

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

    def run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []
        all_adjusted_weights = []

        if self.trading_frequency == "Monthly":
            step = 1
            freq = "M"
        elif self.trading_frequency == "Bi-Monthly":
            step = 2
            freq = "2M"
        elif self.trading_frequency == "Quarterly":
            step = 3
            freq = "3M"
        elif self.trading_frequency == "Yearly":
            step = 12
            freq = "12M"
        else:
            raise ValueError("Invalid trading frequency. Choose 'Monthly', 'Bi-Monthly', 'Quarterly', or 'Yearly'.")

        for i in range(0, len(monthly_dates), step):
            current_date = monthly_dates[i]
            next_date = monthly_dates[min(i + step, len(monthly_dates) - 1)]
            last_date_current_month = self.trading_data.index[self.trading_data.index.get_loc(current_date, method='pad')]
            adjusted_weights = self.adjust_weights(last_date_current_month)
            previous_value = portfolio_values[-1]
            month_end_data = self.trading_data.loc[last_date_current_month]
            month_start_data = month_end_data

            last_date_next_month = self.trading_data.index[self.trading_data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self.trading_data.loc[last_date_next_month]

            monthly_returns = next_month_end_data / month_start_data - 1
            month_return = sum(
                [monthly_returns.get(ticker, 0) * weight for ticker, weight in adjusted_weights.items()]
            )
            new_portfolio_value = previous_value * (1 + month_return)

            all_adjusted_weights.append(adjusted_weights)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.adjusted_weights = pd.Series(
            all_adjusted_weights,
            index=pd.date_range(start=self.start_date, periods=len(all_adjusted_weights), freq=freq)
        )
        self.data_models.portfolio_values = pd.Series(
            portfolio_values,
            index=pd.date_range(start=self.start_date, periods=len(portfolio_values), freq=freq)
        )
        self.data_models.portfolio_returns = pd.Series(
            portfolio_returns,
            index=pd.date_range(start=self.start_date, periods=len(portfolio_returns), freq=freq)
        )
