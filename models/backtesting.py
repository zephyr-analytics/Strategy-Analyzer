import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go

from results.results_processor import ResultsProcessor

import utilities as utilities

# TODO further testing of functionality. 

class BacktestStaticPortfolio:
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA).

    Attributes
    ----------
    assets_weights : dict
        Dictionary of asset tickers and their corresponding weights in the portfolio.
    start_date : str
        The start date for the backtest.
    end_date : str
        The end date for the backtest.
    sma_period : int
        The period for calculating the Simple Moving Average (SMA).
    bond_ticker : str
        The ticker symbol for the bond asset. Default is 'BND'.
    cash_ticker : str
        The ticker symbol for the cash asset. Default is 'SHV'.
    initial_portfolio_value : float
        The initial value of the portfolio. Default is 10000.
    _data : DataFrame or None
        DataFrame to store the adjusted closing prices of the assets.
    _portfolio_value : Series
        Series to store the portfolio values over time.
    _returns : Series
        Series to store the portfolio returns over time.
    """

    def __init__(self, assets_weights, start_date, end_date, trading_frequency, output_filename, weighting_strategy, sma_period, bond_ticker, cash_ticker, rebalance_threshold=0.001): 
        """
        Initializes the BacktestStaticPortfolio class with given asset weights, start date, end date, weighting strategy, and SMA period.

        Parameters
        ----------
        assets_weights : dict
            Dictionary of asset tickers and their corresponding weights in the portfolio.
        start_date : str
            The start date for the backtest.
        end_date : str
            The end date for the backtest.
        trading_frequency : str
            The frequency of trades. Either 'monthly' or 'bi-monthly'.
        output_filename : str
            The name of the file to save the output.
        rebalance_threshold : float, optional
            The threshold for rebalancing the portfolio weights. Default is 0.02.
        weighting_strategy : str, optional
            The strategy used to weight the assets. Default is 'use_file_weights'.
        sma_period : int, optional
            The period for calculating the Simple Moving Average (SMA). Default is 168.
        """
        self.assets_weights = assets_weights
        self.start_date = start_date
        self.end_date = end_date
        self.trading_frequency = trading_frequency
        self.output_filename = output_filename
        self.rebalance_threshold = rebalance_threshold
        self.weighting_strategy = weighting_strategy
        self.sma_period = sma_period
        self.bond_ticker = bond_ticker
        self.cash_ticker = cash_ticker
        self.initial_portfolio_value = 10000
        self._data = None
        self._portfolio_value = pd.Series(dtype=float)
        self._returns = pd.Series(dtype=float)

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        self._data = utilities.fetch_data(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker)
        self._run_backtest()
        results_processor = ResultsProcessor(self.output_filename)
        results_processor.plot_portfolio_value(self.get_portfolio_value())
        results_processor.plot_var_cvar(self._returns, self.get_portfolio_value(), self.trading_frequency)
        results_processor.plot_returns_heatmaps(self._returns, self._returns, self.output_filename)

    def _run_backtest(self):
            """
            Runs the backtest by calculating portfolio values and returns over time.
            """
            monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
            portfolio_values = [self.initial_portfolio_value]
            portfolio_returns = []
            
            if self.trading_frequency == 'Monthly':
                step = 1
            elif self.trading_frequency == 'Bi-Monthly':
                step = 2
            else:
                raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")
            
            adjusted_weights = utilities.adjusted_weights(
                self.assets_weights, 
                self._data, 
                self.bond_ticker, 
                self.cash_ticker, 
                self.weighting_strategy, 
                self.sma_period, 
                monthly_dates[0]
            )
            
            for i in range(1, len(monthly_dates), step):
                previous_date = monthly_dates[i - 1]  
                current_date = monthly_dates[i]  
                last_date_previous_month = self._data.index[self._data.index.get_loc(previous_date, method='pad')]
                month_start_data = self._data.loc[last_date_previous_month]
                previous_value = portfolio_values[-1]
                last_date_current_month = self._data.index[self._data.index.get_loc(current_date, method='pad')]
                current_month_end_data = self._data.loc[last_date_current_month]
                monthly_returns = (current_month_end_data / month_start_data) - 1
                month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
                new_portfolio_value = previous_value * (1 + month_return)
                print(f'Current Return:{month_return}')
                print(f'Previous Portfolio Value:{previous_value}')
                print(f'New Portfolio Value:{new_portfolio_value}')

                portfolio_values.append(new_portfolio_value)
                portfolio_returns.append(month_return)
                
                adjusted_weights = utilities.adjusted_weights(
                    self.assets_weights, 
                    self._data, 
                    self.bond_ticker, 
                    self.cash_ticker, 
                    self.weighting_strategy, 
                    self.sma_period, 
                    current_date
                )
                adjusted_weights = self._rebalance_portfolio(adjusted_weights)
            
            self._portfolio_value = pd.Series(portfolio_values, index=pd.date_range(start=self.start_date, periods=len(portfolio_values), freq='M'))
            self._returns = pd.Series(portfolio_returns, index=pd.date_range(start=self.start_date, periods=len(portfolio_returns), freq='M'))

    def _rebalance_portfolio(self, current_weights):
        """
        Rebalances the portfolio if the weights are outside their target range.

        Parameters
        ----------
        current_weights : dict
            Dictionary of current asset weights.

        Returns
        -------
        dict
            Dictionary of rebalanced asset weights.
        """
        rebalanced_weights = current_weights.copy()
        for ticker, target_weight in self.assets_weights.items():
            if abs(current_weights[ticker] - target_weight) > self.rebalance_threshold:
                rebalanced_weights[ticker] = target_weight
        total_weight = sum(rebalanced_weights.values())
        for ticker in rebalanced_weights:
            rebalanced_weights[ticker] /= total_weight

        return rebalanced_weights

    def get_portfolio_value(self):
        """
        Returns the portfolio value series.

        Returns
        -------
        Series
            Series containing the portfolio values over time.
        """
        return self._portfolio_value
