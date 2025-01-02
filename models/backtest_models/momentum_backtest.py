"""
Module for backtesting momentum assets.
"""

import datetime
import warnings

import pandas as pd

import utilities as utilities

from data.data_obtain import DataObtainmentProcessor
from models.models_data import ModelsData
from models.backtest_models.backtesting_processor import BacktestingProcessor
from results.results_processor import ResultsProcessor

warnings.filterwarnings("ignore")


class BacktestMomentumPortfolio(BacktestingProcessor):
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


    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        data_processor = DataObtainmentProcessor(models_data=self.data_models)
        self._data = data_processor.process()

        self._momentum_data = self._data.copy().pct_change().dropna()
        self.run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self.persist_data()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value()
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()



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

    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame,
            filter_negative_momentum: bool = True,
            selected_out_of_market_assets=None
        ) -> dict:
        """
        Adjusts the weights of the selected assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame of selected assets and their weights.
        filter_negative_momentum : bool, optional
            Whether to filter out assets with negative momentum. Default is True.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        trading_assets = selected_assets[selected_assets['Asset'] != self.threshold_asset]

        def get_replacement_asset():
            """
            Determines the replacement asset (cash or bond) based on SMA.
            """
            if self.bond_ticker and not is_below_sma(self.bond_ticker):
                return self.bond_ticker
            return self.cash_ticker

        def is_below_sma(ticker: str):
            """
            Checks if the asset's price is below its SMA.

            Parameters
            ----------
            ticker : str
                String representing ticker symbol.
            """
            price = self._data.loc[:current_date, ticker].iloc[-1]
            ma = self._data.loc[:current_date, ticker].rolling(window=self.ma_period).mean().iloc[-1]
            return price < ma

        adjusted_weights = {}
        total_weight = 0

        for _, row in trading_assets.iterrows():
            asset = row['Asset']
            momentum = row['Momentum']

            # Apply conditional logic for filtering negative momentum
            if (filter_negative_momentum and momentum <= 0) or is_below_sma(asset):
                replacement_asset = get_replacement_asset()
                adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + 1
            else:
                adjusted_weights[asset] = adjusted_weights.get(asset, 0) + 1

            total_weight += 1

        # Normalize weights
        adjusted_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}

        print(f'{current_date}: Weights: {adjusted_weights}')
        return adjusted_weights

    def run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []
        all_adjusted_weights = []

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
            momentum = momentum.drop(self.threshold_asset, errors='ignore')
            
            # Select assets based on momentum
            selected_assets = pd.DataFrame({'Asset': momentum.nlargest(self.num_assets_to_select).index, 'Momentum': momentum.nlargest(self.num_assets_to_select).values})
            print(selected_assets)
            # Adjust weights based on the selected assets
            adjusted_weights = self.adjust_weights(last_date_current_month, selected_assets)

            previous_value = portfolio_values[-1]
            month_end_data = self._data.loc[last_date_current_month]
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self._data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_end_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)

            all_adjusted_weights.append(adjusted_weights)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.adjusted_weights = pd.Series(
            all_adjusted_weights,
            index=pd.date_range(
                start=self.start_date,
                periods=len(all_adjusted_weights),
                freq=freq
            )
        )
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
