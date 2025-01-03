"""
Backtesting processor module.
"""

import pandas as pd

import utilities as utilities

from results.results_processor import ResultsProcessor
import warnings

from data.data_obtain import DataObtainmentProcessor
from models.models_data import ModelsData
from models.backtest_models.backtesting_processor import BacktestingProcessor

warnings.filterwarnings("ignore")


class SmaBacktestPortfolio(BacktestingProcessor):
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
    ma_period : int
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
    """

    def __init__(self, data_models: ModelsData):
        """
        Initializes the BacktestStaticPortfolio class with data from ModelsData.

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

        self.run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self.persist_data()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value()
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()

    def calculate_momentum(self, current_date=None):
        pass


    def adjust_weights(self, current_date, selected_assets=None, selected_out_of_market_assets=None):
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

        def is_below_ma(ticker):
            """
            Checks if the price of the given ticker is below its moving average.

            Parameters
            ----------
            ticker : str
                The ticker to check.

            Returns
            -------
            bool
                True if the price is below the moving average, False otherwise.
            """
            price = self._data.loc[:current_date, ticker].iloc[-1]

            if self.ma_type == "SMA":
                ma = self._data.loc[:current_date, ticker].rolling(window=self.ma_period).mean().iloc[-1]
            elif self.ma_type == "EMA":
                ma = self._data.loc[:current_date, ticker].ewm(span=self.ma_period).mean().iloc[-1]
            else:
                raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

            return price < ma

        def get_replacement_asset():
            """
            Determines the replacement asset (cash or bond) based on SMA.

            Returns
            -------
            str
                The replacement asset ticker.
            """
            if self.bond_ticker and not is_below_ma(self.bond_ticker):
                return self.bond_ticker
            return self.cash_ticker

        for ticker in list(adjusted_weights.keys()):
            if is_below_ma(ticker):
                replacement_asset = get_replacement_asset()
                adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + adjusted_weights[ticker]
                adjusted_weights[ticker] = 0

        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight

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
            last_date_current_month = self._data.index[self._data.index.get_loc(current_date, method='pad')]
            adjusted_weights = self.adjust_weights(last_date_current_month)
            previous_value = portfolio_values[-1]
            month_end_data = self._data.loc[last_date_current_month]
            month_start_data = month_end_data
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self._data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_start_data) - 1
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
