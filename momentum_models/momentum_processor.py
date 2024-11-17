"""
Abstract module for processing momentum trading models.
"""

import datetime

from abc import ABC, abstractmethod
from typing import List, Dict

import pandas as pd

import utilities as utilities

from models_data import ModelsData
from results.results_processor import ResultsProcessor


class MomentumProcessor(ABC):
    """
    Abstract base class for backtesting portfolios with configurable strategies.

    Attributes
    ----------
    assets_weights : dict
        Dictionary of asset tickers and their corresponding weights in the portfolio.
    start_date : str
        The start date for the backtest.
    end_date : str
        The end date for the backtest.
    initial_portfolio_value : float
        The initial value of the portfolio.
    trading_frequency : str
        Frequency of portfolio rebalancing (e.g., 'Monthly', 'Bi-Monthly').
    data_models : ModelsData
        The data model instance containing parameters and configurations for the portfolio.
    _data : DataFrame or None
        DataFrame to store the adjusted closing prices of the assets.
    """
    # TODO this needs to become backtesting processor, and sma backtesting needs to be become apart of it.
    def __init__(self, data_models: ModelsData):
        self.data_models = data_models

        self.assets_weights = data_models.assets_weights
        self.start_date = data_models.start_date
        self.end_date = data_models.end_date
        self.trading_frequency = data_models.trading_frequency
        self.output_filename = data_models.weights_filename
        self.rebalance_threshold = 0.02
        self.weighting_strategy = data_models.weighting_strategy
        self.sma_period = int(data_models.sma_window)
        self.bond_ticker = str(data_models.bond_ticker)
        self.cash_ticker = str(data_models.cash_ticker)
        self.initial_portfolio_value = int(data_models.initial_portfolio_value)
        self.num_assets_to_select = int(data_models.num_assets_to_select)
        self.threshold_asset = str(data_models.threshold_asset)

        self._data = None
        self._momentum_data = None


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
        cagr = utilities.calculate_cagr(self.data_models.portfolio_values, self.trading_frequency)
        average_annual_return = utilities.calculate_average_annual_return(self.data_models.portfolio_returns, self.trading_frequency)
        max_drawdown = utilities.calculate_max_drawdown(self.data_models.portfolio_values)
        var, cvar = utilities.calculate_var_cvar(self.data_models.portfolio_returns)
        annual_volatility = utilities.calculate_annual_volatility(self.trading_frequency, self.data_models.portfolio_returns)
        standard_deviation = utilities.calculate_standard_deviation(self.data_models.portfolio_returns)

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
        all_tickers = list(self.assets_weights.keys())
        self._bnh_data, message = utilities.fetch_data(
            all_tickers=all_tickers,
            start_date=self.start_date,
            end_date=self.end_date
        )

        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []
        
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        
        for i in range(1, len(monthly_dates)):
            start_index = self._bnh_data.index.get_indexer([monthly_dates[i-1]], method='nearest')[0]
            end_index = self._bnh_data.index.get_indexer([monthly_dates[i]], method='nearest')[0]
            start_data = self._bnh_data.iloc[start_index]
            end_data = self._bnh_data.iloc[end_index]

            previous_value = portfolio_values[-1]
            monthly_returns = (end_data / start_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in self.assets_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.buy_and_hold_values = pd.Series(portfolio_values, index=monthly_dates[:len(portfolio_values)])
        self.data_models.buy_and_hold_returns = pd.Series(portfolio_returns, index=monthly_dates[1:len(portfolio_returns)+1])
