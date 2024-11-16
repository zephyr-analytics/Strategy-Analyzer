"""
Module for backtesting momentum assets.
"""

import datetime
import warnings

import pandas as pd

import utilities as utilities

from models_data import ModelsData
from momentum_models.momentum_processor import MomentumProcessor
from results.results_processor import ResultsProcessor

warnings.filterwarnings("ignore")


class BacktestMomentumPortfolio(MomentumProcessor):
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
        The period for calculating the Simple Moving Average (SMA). Default is 168.
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
    _momentum_data : DataFrame
        DataFrame to store the returns data for calculating momentum.
    """

    def __init__(self, data_models: ModelsData):
        """
        Initializes the BacktestMomentumPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        super().__init__(data_models=data_models)


    def calculate_momentum(self, current_date: datetime) -> float:
        """
        Calculate average momentum based on 3, 6, 9, and 12-month cumulative returns.
        
        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        """
        momentum_3m = (self._momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (self._momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (self._momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (self._momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        return (momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 4


    def _adjust_weights(self, current_date: datetime, selected_assets: list) -> dict:
        """
        Adjusts the weights of the selected assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame of selected assets and their weights.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        # TODO there are still cases where asset weights are not as expected.
        # Initialize equal weights for selected assets
        num_assets = len(selected_assets)
        equal_weight = 1 / num_assets
        adjusted_weights = {asset: equal_weight for asset in selected_assets['Asset']}
        
        if self.threshold_asset:
            # Note this is logic for threshold asset adjusting.
            threshold_price = self._data.loc[:current_date, self.threshold_asset].iloc[-1]
            threshold_sma = self._data.loc[:current_date, self.threshold_asset].rolling(window=self.sma_period).mean().iloc[-1]
            if threshold_price < threshold_sma:
                if self._data.loc[:current_date, self.bond_ticker].iloc[-1] < self._data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                    adjusted_weights = {self.cash_ticker: 1.0}
                else:
                    adjusted_weights = {self.bond_ticker: 1.0}
            else:
                for ticker in list(adjusted_weights.keys()):
                    asset_price = self._data.loc[:current_date, ticker].iloc[-1]
                    asset_sma = self._data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]

                    if asset_price < asset_sma:
                        if self._data.loc[:current_date, self.bond_ticker].iloc[-1] < self._data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                            adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + adjusted_weights[ticker]
                        else:
                            adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + adjusted_weights[ticker]
                        adjusted_weights[ticker] = 0
        else:
            # Note: This is logic for non-threshold asset adjusting.
            for ticker in list(adjusted_weights.keys()):
                asset_price = self._data.loc[:current_date, ticker].iloc[-1]
                asset_sma = self._data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]
                if asset_price < asset_sma:
                    if self._data.loc[:current_date, self.bond_ticker].iloc[-1] < self._data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                        adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + adjusted_weights[ticker]
                    else:
                        adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + adjusted_weights[ticker]
                    adjusted_weights[ticker] = 0

        # Note a final check for # of assets and weights.
        actual_assets_count = sum(1 for weight in adjusted_weights.values() if weight > 0)
        if actual_assets_count < self.num_assets_to_select:
            fill_asset = self.cash_ticker if self._data.loc[:current_date, self.bond_ticker].iloc[-1] < self._data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1] else self.bond_ticker
            fill_weight = (self.num_assets_to_select - actual_assets_count) / self.num_assets_to_select
            adjusted_weights[fill_asset] = adjusted_weights.get(fill_asset, 0) + fill_weight

        #Note normalize weights to ensure they sum to 1.
        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight

        print(f'{current_date}: Weights: {adjusted_weights}')
        return adjusted_weights


    def _run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []
        if self.trading_frequency == 'Monthly':
            step = 1
            freq = 'M'
        elif self.trading_frequency == 'Bi-Monthly':
            step = 2
            freq = '2M'
        else:
            raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")

        for i in range(0, len(monthly_dates), step):
            current_date = monthly_dates[i]
            next_date = monthly_dates[min(i + step, len(monthly_dates) - 1)]
            last_date_current_month = self._data.index[self._data.index.get_loc(current_date, method='pad')]

            # Calculate momentum
            momentum = self.calculate_momentum(last_date_current_month)
            
            # Select assets based on momentum
            selected_assets = pd.DataFrame({'Asset': momentum.nlargest(self.num_assets_to_select).index, 'Momentum': momentum.nlargest(self.num_assets_to_select).values})
            print(selected_assets)
            # Adjust weights based on the selected assets
            adjusted_weights = self._adjust_weights(last_date_current_month, selected_assets)

            previous_value = portfolio_values[-1]
            month_end_data = self._data.loc[last_date_current_month]
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self._data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_end_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.adjusted_weights = adjusted_weights
        # Update portfolio values and returns with the correct index
        self.data_models.portfolio_values = pd.Series(
            portfolio_values,
            index=pd.date_range(
                start=self.start_date,
                periods=len(portfolio_values),
                freq=freq
            )
        )
        self.data_models.portfolio_returns = pd.Series(
            portfolio_returns,
            index=pd.date_range(
                start=self.start_date,
                periods=len(portfolio_returns),
                freq=freq
            )
        )
