"""
Module for backtesting momentum assets.
"""

import datetime
import warnings

import pandas as pd

import utilities as utilities

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
        all_tickers = list(self.assets_weights.keys()) + [self.cash_ticker]

        if self.threshold_asset != "":
            all_tickers.append(self.threshold_asset)

        if self.bond_ticker != "":
            all_tickers.append(self.bond_ticker)

        self._data, message = utilities.fetch_data(all_tickers, self.start_date, self.end_date)

        print(f"Data was updated for common start dates:\n\n {message}")

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

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        num_assets = len(selected_assets)
        equal_weight = 1 / num_assets
        adjusted_weights = {asset: equal_weight for asset in selected_assets['Asset']}


        def is_below_sma(ticker: str):
            """
            Checks if the asset's price is below its SMA.

            Parameters
            ----------
            ticker : str
                String representing ticker symbol.
            """
            price = self._data.loc[:current_date, ticker].iloc[-1]
            sma = self._data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]
            return price < sma


        def allocate_to_safe_asset():
            """
            Allocates weights to a safe asset (cash or bond).
            """
            if self.bond_ticker and is_below_sma(self.bond_ticker):
                return {self.cash_ticker: 1.0}
            if self.bond_ticker:
                return {self.bond_ticker: 1.0}
            return {self.cash_ticker: 1.0}  # If no bond ticker, always allocate to cash.


        # Check threshold asset logic
        if self.threshold_asset and is_below_sma(self.threshold_asset):
            return allocate_to_safe_asset()

        for ticker in list(adjusted_weights.keys()):
            if is_below_sma(ticker):
                safe_asset = self.cash_ticker  # Default to cash if no bond ticker is provided.
                if self.bond_ticker and not is_below_sma(self.bond_ticker):
                    safe_asset = self.bond_ticker
                adjusted_weights[safe_asset] = adjusted_weights.get(safe_asset, 0) + adjusted_weights[ticker]
                adjusted_weights[ticker] = 0

        # Ensure minimum number of assets are selected
        actual_assets_count = sum(1 for weight in adjusted_weights.values() if weight > 0)
        if actual_assets_count < self.num_assets_to_select:
            fill_asset = self.cash_ticker
            if self.bond_ticker and not is_below_sma(self.bond_ticker):
                fill_asset = self.bond_ticker
            fill_weight = (self.num_assets_to_select - actual_assets_count) / self.num_assets_to_select
            adjusted_weights[fill_asset] = adjusted_weights.get(fill_asset, 0) + fill_weight

        # Normalize weights to ensure they sum to 1
        total_weight = sum(adjusted_weights.values())
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
