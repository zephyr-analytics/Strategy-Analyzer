"""
Module for backtesting in and out of market momentum assets.
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


class BacktestInAndOutMomentumPortfolio(BacktestingProcessor):
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA),
    with momentum calculations for both in-market and out-of-market assets.
    """

    def __init__(self, data_models: ModelsData):
        """
        Initializes the BacktestMomentumPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        self.data_models = data_models

        self.assets_weights = data_models.assets_weights
        self.start_date = data_models.start_date
        self.end_date = data_models.end_date
        self.trading_frequency = data_models.trading_frequency
        self.output_filename = data_models.weights_filename
        self.rebalance_threshold = 0.02
        self.weighting_strategy = data_models.weighting_strategy
        self.sma_period = int(data_models.ma_window)
        self.bond_ticker = data_models.bond_ticker
        self.cash_ticker = data_models.cash_ticker
        self.initial_portfolio_value = int(data_models.initial_portfolio_value)
        self.num_assets_to_select = int(data_models.num_assets_to_select)
        self.threshold_asset = str(data_models.ma_threshold_asset)
        self.out_of_market_tickers = data_models.out_of_market_tickers

        # Class-defined attributes
        self._data = None  # In-market assets data
        self._out_of_market_data = None  # Out-of-market assets data
        self._momentum_data = None  # In-market momentum data
        self._momentum_data_out_of_market = None  # Out-of-market momentum data


    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        data_processor = DataObtainmentProcessor(models_data=self.data_models)
        self.data = data_processor.process

        all_tickers = list(self.assets_weights.keys()) + [self.cash_ticker]

        if self.threshold_asset != "":
            all_tickers.append(self.threshold_asset)

        if self.bond_ticker != "":
            all_tickers.append(self.bond_ticker)

        self._data, message = utilities.fetch_data(all_tickers, self.start_date, self.end_date)
        print(f"Data was updated for common start dates:\n\n {message}")

        self._out_of_market_data = utilities.fetch_out_of_market_data(self.out_of_market_tickers, self.start_date, self.end_date)
        print(f"Data was updated for common start dates:\n\n {message}")

        # Calculate momentum for both in-market and out-of-market assets
        self._momentum_data = self._data.copy().pct_change().dropna()
        self._momentum_data_out_of_market = self._out_of_market_data.copy().pct_change().dropna()

        self.run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self.persist_data()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value()
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()


    def calculate_momentum(self, current_date: datetime) -> tuple:
        """
        Calculate average momentum based on 1, 3, 6, 9, and 12-month.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        tuple
            in_market_momentum and out_of_market_momentum
        """
        momentum_3m = (self._momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (self._momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (self._momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (self._momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        in_market_momentum = (momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 4

        momentum_3m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-252:] + 1).prod() - 1
        out_of_market_momentum = (momentum_3m_out + momentum_6m_out + momentum_9m_out + momentum_12m_out) / 4

        return in_market_momentum, out_of_market_momentum


    def adjust_weights(
            self, 
            current_date: datetime, 
            selected_assets: pd.DataFrame, 
            selected_out_of_market_assets: pd.DataFrame
        ) -> dict:
        """
        Adjusts the weights of the selected assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame, optional
            DataFrame of selected in-market assets and their weights.
        selected_out_of_market_assets : DataFrame, optional
            DataFrame of selected out-of-market assets and their weights.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        adjusted_weights = {}

        def is_below_sma(ticker: str, data_source: pd.DataFrame):
            """
            Checks if the asset's price is below its SMA.

            Parameters
            ----------
            ticker : str
                String representing the ticker symbol.
            data_source : Dataframe
                Dataframe of price data for portfolio.
            """
            price = data_source.loc[:current_date, ticker].iloc[-1]
            sma = data_source.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]
            return price < sma

        def allocate_to_safe_asset(asset_weight: float):
            """
            Allocates weights to a safe asset (cash or bond).

            Parameters
            ----------
            asset_weight : float
                The weight of the asset to adjust.
            """
            if self.bond_ticker and not is_below_sma(self.bond_ticker, self._out_of_market_data):
                safe_asset = self.bond_ticker
            else:
                safe_asset = self.cash_ticker
            adjusted_weights[safe_asset] = adjusted_weights.get(safe_asset, 0) + asset_weight

        # Handle threshold asset logic if applicable
        if self.threshold_asset and is_below_sma(self.threshold_asset, self._data):
            allocate_to_safe_asset(1.0)
            return adjusted_weights

        # Process in-market assets
        if selected_assets is not None:
            for ticker in selected_assets['Asset']:
                weight = 1 / len(selected_assets)
                if not is_below_sma(ticker, self._data):
                    adjusted_weights[ticker] = weight
                else:
                    # Check out-of-market assets when in-market asset is below SMA
                    highest_momentum_asset = None
                    highest_momentum_value = float('-inf')

                    if selected_out_of_market_assets is not None:
                        for out_ticker, momentum in zip(selected_out_of_market_assets['Asset'], selected_out_of_market_assets['Momentum']):
                            if not is_below_sma(out_ticker, self._out_of_market_data):
                                if momentum > highest_momentum_value:
                                    highest_momentum_value = momentum
                                    highest_momentum_asset = out_ticker

                    if highest_momentum_asset:
                        adjusted_weights[highest_momentum_asset] = adjusted_weights.get(highest_momentum_asset, 0) + weight
                    else:
                        allocate_to_safe_asset(weight)

        # Normalize weights to ensure they sum to 1
        total_weight = sum(adjusted_weights.values())
        adjusted_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}
        print(f'{current_date}: Adjusted Weights: {adjusted_weights}')
        return adjusted_weights


    def run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        # TODO this only handles instances where num_assets will be the number of out of market assets to select.
        combined_data = pd.concat([self._data, self._out_of_market_data], axis=1).fillna(method='ffill')

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
            raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")

        for i in range(0, len(monthly_dates), step):
            current_date = monthly_dates[i]
            next_date = monthly_dates[min(i + step, len(monthly_dates) - 1)]
            last_date_current_month = combined_data.index[combined_data.index.get_loc(current_date, method='pad')]
            in_market_momentum, out_of_market_momentum = self.calculate_momentum(last_date_current_month)
            selected_assets = pd.DataFrame({'Asset': in_market_momentum.nlargest(self.num_assets_to_select).index,
                                            'Momentum': in_market_momentum.nlargest(self.num_assets_to_select).values})
            selected_out_of_market_assets = pd.DataFrame({'Asset': out_of_market_momentum.nlargest(self.num_assets_to_select).index,
                                                        'Momentum': out_of_market_momentum.nlargest(self.num_assets_to_select).values})
            adjusted_weights = self.adjust_weights(last_date_current_month, selected_assets, selected_out_of_market_assets)
            previous_value = portfolio_values[-1]
            month_end_data = combined_data.loc[last_date_current_month]
            last_date_next_month = combined_data.index[combined_data.index.get_loc(next_date, method='pad')]
            next_month_end_data = combined_data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_end_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items() if ticker in monthly_returns])
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
