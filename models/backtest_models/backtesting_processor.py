"""
Abstract module for processing momentum trading models.
"""

import datetime

from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd

import utilities as utilities

from data.portfolio_data import PortfolioData
from models.models_data import ModelsData
from processing_types import *


class BacktestingProcessor(ABC):
    """
    Abstract base class for backtesting portfolios with configurable strategies.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        self.data_models = models_data

        self.assets_weights = self.data_models.assets_weights
        self.weights_filename = self.data_models.weights_filename
        self.start_date = self.data_models.start_date
        self.end_date = self.data_models.end_date
        self.trading_frequency = self.data_models.trading_frequency
        self.output_filename = self.data_models.weights_filename
        self.rebalance_threshold = 0.02
        self.weighting_strategy = self.data_models.weighting_strategy
        self.ma_period = int(self.data_models.ma_window)
        self.bond_ticker = str(self.data_models.bond_ticker)
        self.cash_ticker = str(self.data_models.cash_ticker)
        self.initial_portfolio_value = int(self.data_models.initial_portfolio_value)
        self.num_assets_to_select = int(self.data_models.num_assets_to_select)
        self.ma_threshold_asset = str(self.data_models.ma_threshold_asset)
        self.processing_type = self.data_models.processing_type
        self.ma_type = self.data_models.ma_type
        self.benchmark_asset = self.data_models.benchmark_asset
        self.out_of_market_tickers = self.data_models.out_of_market_tickers
        self.filter_negative_momentum = self.data_models.negative_mom

        self.trading_data = portfolio_data.trading_data
        self.asset_data = portfolio_data.assets_data
        self.benchmark_data = portfolio_data.benchmark_data
        self.bond_data = portfolio_data.bond_data
        self.cash_data = portfolio_data.cash_data
        self.ma_threshold_data = portfolio_data.ma_threshold_data
        self.out_of_market_data = portfolio_data.out_of_market_data


    @abstractmethod
    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        pass


    @abstractmethod
    def calculate_momentum(self, current_date: datetime.date) -> float:
        """
        Calculates momentum based on asset performance.

        Parameters
        ----------
        current_date : datetime.date
            The current date for which the momentum is calculated.
        
        Returns
        -------
        float
            Momentum value for the current date.
        """
        pass


    @abstractmethod
    def adjust_weights(
        self,
        current_date: datetime.date,
        selected_assets: pd.DataFrame,
        selected_out_of_market_assets: pd.DataFrame
        ) -> Dict[str, float]:
        """
        Adjusts portfolio weights based on asset performance and strategy.

        Parameters
        ----------
        current_date : datetime.date
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame containing selected assets and their weights.
        _out_of_market_assets : DataFrame
            DataFrame containing selected assets for out of market and their weights.
        Returns
        -------
        dict
            Dictionary of adjusted weights.
        """
        pass


    @abstractmethod
    def run_backtest(self):
        """
        Executes the backtest by iterating over the time period and rebalancing portfolio as per the strategy.
        """
        pass


    def _get_portfolio_statistics(self):
        """
        Calculates and sets portfolio statistics such as CAGR, average annual return, max drawdown, VaR, and CVaR in models_data.
        """
        cagr = utilities.calculate_cagr(portfolio_value=self.data_models.portfolio_values)
        average_annual_return = utilities.calculate_average_annual_return(returns=self.data_models.portfolio_returns)
        max_drawdown = utilities.calculate_max_drawdown(portfolio_value=self.data_models.portfolio_values)
        var, cvar = utilities.calculate_var_cvar(returns=self.data_models.portfolio_returns)
        annual_volatility = utilities.calculate_annual_volatility(portfolio_returns=self.data_models.portfolio_returns)
        standard_deviation = utilities.calculate_standard_deviation(returns=self.data_models.portfolio_returns)

        self.data_models.cagr = cagr
        self.data_models.average_annual_return = average_annual_return
        self.data_models.max_drawdown = max_drawdown
        self.data_models.var = var
        self.data_models.cvar = cvar
        self.data_models.annual_volatility = annual_volatility
        self.data_models.standard_deviation = standard_deviation


    def _calculate_buy_and_hold(self):
        """
        Calculates the buy-and-hold performance of the portfolio with the same assets and weights over the time frame.
        """
        self.bnh_data = self.asset_data

        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []

        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        
        for i in range(1, len(monthly_dates)):
            start_index = self.bnh_data.index.get_indexer([monthly_dates[i-1]], method='nearest')[0]
            end_index = self.bnh_data.index.get_indexer([monthly_dates[i]], method='nearest')[0]
            start_data = self.bnh_data.iloc[start_index]
            end_data = self.bnh_data.iloc[end_index]

            previous_value = portfolio_values[-1]
            monthly_returns = (end_data / start_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in self.assets_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.buy_and_hold_values = pd.Series(portfolio_values, index=monthly_dates[:len(portfolio_values)])
        self.data_models.buy_and_hold_returns = pd.Series(portfolio_returns, index=monthly_dates[1:len(portfolio_returns)+1])


    def _calculate_benchmark(self):
        """
        Calculates the performance of a benchmark asset over the specified timeframe.
        """
        if not self.benchmark_asset:
            return
        else:
            benchmark_values = [self.initial_portfolio_value]
            benchmark_returns = []

            monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')

            for i in range(1, len(monthly_dates)):
                start_index = self.benchmark_data.index.get_indexer([monthly_dates[i-1]], method='nearest')[0]
                end_index = self.benchmark_data.index.get_indexer([monthly_dates[i]], method='nearest')[0]

                start_price = self.benchmark_data.iloc[start_index][self.benchmark_asset]
                end_price = self.benchmark_data.iloc[end_index][self.benchmark_asset]

                monthly_return = (end_price / start_price) - 1

                previous_value = benchmark_values[-1]
                new_benchmark_value = previous_value * (1 + monthly_return)
                benchmark_values.append(new_benchmark_value)
                benchmark_returns.append(monthly_return)
    
            self.data_models.benchmark_values = pd.Series(benchmark_values, index=monthly_dates[:len(benchmark_values)])
            self.data_models.benchmark_returns = pd.Series(benchmark_returns, index=monthly_dates[1:len(benchmark_returns)+1])



    def persist_data(self):
        """
        Saves combined datasets to a single CSV file in the specified directory.

        Handles adjusted weights, portfolio returns, and portfolio values dynamically.
        """
        adjusted_weights_df = pd.DataFrame(list(self.data_models.adjusted_weights), index=self.data_models.adjusted_weights.index)
        adjusted_weights_df = adjusted_weights_df.fillna(0.0)
        combined_df = pd.concat(
            [
                adjusted_weights_df,
                self.data_models.portfolio_returns.rename("Portfolio Returns"),
                self.data_models.portfolio_values.rename("Portfolio Values"),
            ],
            axis=1,
        )

        utilities.save_dataframe_to_csv(
            data=combined_df,
            output_filename=self.output_filename,
            processing_type=self.processing_type,
            num_assets=self.num_assets_to_select
        )
