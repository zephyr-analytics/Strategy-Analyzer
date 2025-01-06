"""
Moving Average Crossover Backtesting Processor.
"""

import logging

import pandas as pd

import utilities as utilities
from logger import logger
from results.results_processor import ResultsProcessor
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
from models.backtest_models.backtesting_processor import BacktestingProcessor

logger = logging.getLogger(__name__)


class MovingAverageCrossoverProcessor(BacktestingProcessor):
    """
    A class to backtest a portfolio using a moving average crossover strategy.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, fast_ma_period: int, slow_ma_period: int, ma_type: str = "SMA"):
        """
        Initializes the Moving Average Crossover Backtest Processor.

        Parameters
        ----------
        models_data : ModelsData
            Contains all relevant parameters and data for backtesting.
        portfolio_data : PortfolioData
            Portfolio data required for backtesting.
        fast_ma_period : int
            The period for the fast moving average.
        slow_ma_period : int
            The period for the slow moving average.
        ma_type : str
            The type of moving average to use ("SMA" or "EMA").
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data)
        self.fast_ma_period = fast_ma_period
        self.slow_ma_period = slow_ma_period
        self.ma_type = ma_type

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        logger.info(f"Moving Average Crossover backtest for: {self.weights_filename}, Trading Freq:{self.trading_frequency}, Fast MA:{self.fast_ma_period}, Slow MA:{self.slow_ma_period}, Type:{self.ma_type}")
        self.run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self._calculate_benchmark()
        self.persist_data()
        if self.processing_type.endswith("BACKTEST"):
            results_processor = ResultsProcessor(self.data_models)
            results_processor.plot_portfolio_value()
            results_processor.plot_var_cvar()
            results_processor.plot_returns_heatmaps()
        else:
            pass

    def calculate_moving_averages(self, data, period):
        """
        Calculates the moving average based on the specified type.

        Parameters
        ----------
        data : DataFrame
            The DataFrame containing price data.
        period : int
            The period for calculating the moving average.

        Returns
        -------
        Series
            The moving average values.
        """
        if self.ma_type == "SMA":
            return data.rolling(window=period).mean()
        elif self.ma_type == "EMA":
            return data.ewm(span=period).mean()
        else:
            raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

    def adjust_weights(self, current_date):
        """
        Adjusts weights based on the crossover signals.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        fast_ma = self.calculate_moving_averages(self.asset_data.loc[:current_date], self.fast_ma_period)
        slow_ma = self.calculate_moving_averages(self.asset_data.loc[:current_date], self.slow_ma_period)

        adjusted_weights = self.assets_weights.copy()

        for ticker, weight in list(adjusted_weights.items()):
            if fast_ma[ticker].iloc[-1] > slow_ma[ticker].iloc[-1]:
                adjusted_weights[ticker] = weight
            else:
                replacement_asset = self.cash_ticker if self.cash_ticker in self.cash_data.columns else self.bond_ticker
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
        Runs the moving average crossover backtest.
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

            last_date_next_month = self.trading_data.index[self.trading_data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self.trading_data.loc[last_date_next_month]

            monthly_returns = next_month_end_data / month_end_data - 1
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
