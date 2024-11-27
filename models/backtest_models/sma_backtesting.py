"""
Backtesting processor module.
"""

import pandas as pd

import utilities as utilities

from results.results_processor import ResultsProcessor
import warnings

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
    """
# TODO this needs to be properly abstracted.
    def __init__(self, data_models: ModelsData):
        """
        Initializes the BacktestStaticPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        super().__init__(data_models=data_models)
        # self.data_models = data_models

        # self.assets_weights = data_models.assets_weights
        # self.start_date = data_models.start_date
        # self.end_date = data_models.end_date
        # self.trading_frequency = data_models.trading_frequency
        # self.output_filename = data_models.weights_filename
        # self.rebalance_threshold = 0.02
        # self.threshold_asset = str(data_models.threshold_asset)
        # self.weighting_strategy = data_models.weighting_strategy
        # self.sma_period = int(data_models.sma_window)
        # self.bond_ticker = str(data_models.bond_ticker)
        # self.cash_ticker = str(data_models.cash_ticker)
        # self.initial_portfolio_value = int(data_models.initial_portfolio_value)

        # # Class-defined attributes
        # self._data = None


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

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        # if self.weighting_strategy == 'Use File Weights':
        #     adjusted_weights = self.assets_weights.copy()
        # elif self.weighting_strategy == 'Equal Weight':
        #     adjusted_weights = utilities.equal_weighting(self.assets_weights)
        # elif self.weighting_strategy == 'Risk Contribution':
        #     adjusted_weights = utilities.risk_contribution_weighting(self._data.cov(), self.assets_weights)
        # elif self.weighting_strategy == 'Min Volatility':
        #     weights = utilities.min_volatility_weighting(self._data.cov())
        #     adjusted_weights = dict(zip(self.assets_weights.keys(), weights))
        # elif self.weighting_strategy == 'Max Sharpe':
        #     returns = self._data.pct_change().mean()
        #     weights = utilities.max_sharpe_ratio_weighting(self._data.cov(), returns)
        #     adjusted_weights = dict(zip(self.assets_weights.keys(), weights))
        # else:
        #     raise ValueError("Invalid weighting strategy")
        adjusted_weights = self.assets_weights.copy()

        for ticker in self.assets_weights.keys():
            # Check if the current ticker is below its SMA
            if self._data.loc[:current_date, ticker].iloc[-1] < self._data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                # Handle the case where bond_ticker is not available
                if self.bond_ticker == "":
                    adjusted_weights[ticker] = 0
                    adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + self.assets_weights[ticker]
                else:
                    # Bond ticker exists; check if it's below its SMA
                    if self._data.loc[:current_date, self.bond_ticker].iloc[-1] < self._data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                        adjusted_weights[ticker] = 0
                        adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + self.assets_weights[ticker]
                    else:
                        adjusted_weights[ticker] = 0
                        adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + self.assets_weights[ticker]

        # Normalize weights to sum to 1
        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight

        print(f'{current_date}: Weights: {adjusted_weights}')
        return adjusted_weights


    def run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        # print(self.sma_period, self.cash_ticker, self.bond_ticker)
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
            adjusted_weights = self.adjust_weights(last_date_current_month)
            # adjusted_weights = self._rebalance_portfolio(adjusted_weights)
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

        # placeholder_weights = {asset: 0.0 for asset in all_adjusted_weights[0].keys()}
        # all_adjusted_weights = all_adjusted_weights + [placeholder_weights]

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
