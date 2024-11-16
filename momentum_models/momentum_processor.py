"""
Abstract module for processing momentum trading models.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict
import datetime

import utilities as utilities

from models_data import ModelsData
from momentum_models.momentum_processor import MomentumProcessor
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
    # TODO this is not properly abstracted.
    def __init__(self, data_models):
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

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        all_tickers = list(self.assets_weights.keys()) + [self.cash_ticker]

        if self.threshold_asset != "":
            all_tickers.append(self.threshold_asset)

        if self.bond_ticker != "":
            all_tickers.append(self.bond_ticker)

        utilities.fetch_data(all_tickers, self.start_date, self.end_date)

        self._momentum_data = self._data.copy().pct_change().dropna()
        self._run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value()
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()


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
