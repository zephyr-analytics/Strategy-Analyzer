"""
Abstract module for processing momentum trading models.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict
import datetime

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
    def __init__(self, data_models):
        self.data_models = data_models
        self.assets_weights = data_models.assets_weights
        self.start_date = data_models.start_date
        self.end_date = data_models.end_date
        self.initial_portfolio_value = data_models.initial_portfolio_value
        self.trading_frequency = data_models.trading_frequency

        self._data = None

    @abstractmethod
    def process(self):
        """
        Orchestrates the backtest process, including fetching data, running the backtest, and generating reports.
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
    def _adjust_weights(self, current_date: datetime.date, selected_assets: pd.DataFrame) -> Dict[str, float]:
        """
        Adjusts portfolio weights based on asset performance and strategy.

        Parameters
        ----------
        current_date : datetime.date
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame containing selected assets and their weights.
        
        Returns
        -------
        dict
            Dictionary of adjusted weights.
        """
        pass

    @abstractmethod
    def _run_backtest(self):
        """
        Executes the backtest by iterating over the time period and rebalancing portfolio as per the strategy.
        """
        pass

    @abstractmethod
    def _get_portfolio_statistics(self):
        """
        Computes portfolio statistics like CAGR, max drawdown, and volatility.
        """
        pass

    @abstractmethod
    def _calculate_buy_and_hold(self):
        """
        Calculates the buy-and-hold performance for comparison with the strategy.
        """
        pass
