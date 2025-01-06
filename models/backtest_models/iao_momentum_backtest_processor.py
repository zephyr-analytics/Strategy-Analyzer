"""
Module for backtesting in and out of market momentum assets.
"""

import datetime
import logging
import pandas as pd

import utilities as utilities
from logger import logger
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
from models.backtest_models.backtesting_processor import BacktestingProcessor
from results.results_processor import ResultsProcessor

logger = logging.getLogger(__name__)

class IAOMomentumBacktestProcessor(BacktestingProcessor):
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA),
    with momentum calculations for both in-market and out-of-market assets.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        """
        Initializes the BacktestMomentumPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data)

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        logger.info(f"Momentum In and Out backtest for: {self.weights_filename}, Trading Freq:{self.trading_frequency}, Moving Average:{self.ma_period}, Type:{self.ma_type}, Assets:{self.num_assets_to_select}")
        self.run_backtest()
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self._calculate_benchmark()
        self.persist_data()
        if self.processing_type.endswith("BACKTEST"):
            results_processor = ResultsProcessor(self.data_models)
            results_processor.plot_portfolio_value()
            results_processor.plot_var_cvar()
            results_processor.plot_returns_heatmaps()
        else:
            pass

    def calculate_momentum(self, current_date: datetime) -> tuple:
        """
        Calculate average momentum based on 3, 6, 9, and 12-month cumulative returns for both in-market and out-of-market assets.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        tuple
            in_market_momentum and out_of_market_momentum
        """
        momentum_data = self.asset_data.copy().pct_change().dropna()
        momentum_3m = (momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        in_market_momentum = (momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 4

        momentum_data_out_of_market = self.out_of_market_data.copy().pct_change().dropna()
        momentum_3m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m_out = (momentum_data_out_of_market.loc[:current_date].iloc[-252:] + 1).prod() - 1
        out_of_market_momentum = (momentum_3m_out + momentum_6m_out + momentum_9m_out + momentum_12m_out) / 4

        return in_market_momentum, out_of_market_momentum

    def adjust_weights(self, current_date: datetime, selected_assets: pd.DataFrame, selected_out_of_market_asset: pd.DataFrame) -> dict:
        """
        Adjusts the weights of the selected assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame of selected in-market assets and their weights.
        selected_out_of_market_asset : str
            The out-of-market asset with the highest momentum to be used as the safe asset.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        adjusted_weights = {}

        def is_below_ma(ticker: str, data: pd.DataFrame) -> bool:
            """
            Checks if the asset's price is below its moving average.

            Parameters
            ----------
            ticker : str
                The ticker to check.
            data : pd.DataFrame
                Data containing the asset's price history.

            Returns
            -------
            bool
                True if the price is below the moving average, False otherwise.
            """
            if ticker not in data.columns:
                return True

            price = data.loc[:current_date, ticker].iloc[-1]

            if self.ma_type == "SMA":
                ma = data.loc[:current_date, ticker].rolling(window=self.ma_period).mean().iloc[-1]
            elif self.ma_type == "EMA":
                ma = data.loc[:current_date, ticker].ewm(span=self.ma_period).mean().iloc[-1]
            else:
                raise ValueError("Invalid ma_type. Choose 'SMA' or 'EMA'.")

            return price < ma

        def allocate_to_safe_asset(weight: float):
            """
            Allocates weights to the selected out-of-market asset if it is above its moving average,
            otherwise falls back to bonds or cash.

            Parameters
            ----------
            weight : float
                Weight to be allocated.
            """
            if not is_below_ma(selected_out_of_market_asset['Asset'].iloc[0], self.out_of_market_data):
                adjusted_weights[selected_out_of_market_asset['Asset'].iloc[0]] = adjusted_weights.get(selected_out_of_market_asset['Asset'].iloc[0], 0) + weight
            elif not is_below_ma(self.bond_ticker, self.bond_data):
                adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + weight
            else:
                adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + weight

        if self.ma_threshold_asset and is_below_ma(self.ma_threshold_asset, self.ma_threshold_data):
            allocate_to_safe_asset(1.0)
            return adjusted_weights

        for _, row in selected_assets.iterrows():
            asset, momentum = row['Asset'], row['Momentum']
            weight = 1 / len(selected_assets)
            if self.filter_negative_momentum and momentum <= 0 or is_below_ma(asset, self.asset_data):
                allocate_to_safe_asset(weight)
            else:
                adjusted_weights[asset] = weight

        total_weight = sum(adjusted_weights.values())
        adjusted_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}
        logger.info(f"Date:{current_date}, Selected Assets:{adjusted_weights}")
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
            last_date_current_month = self.trading_data.index[self.trading_data.index.get_loc(current_date, method='pad')]

            in_market_momentum, out_of_market_momentum = self.calculate_momentum(last_date_current_month)
            selected_assets = pd.DataFrame({'Asset': in_market_momentum.nlargest(self.num_assets_to_select).index, 'Momentum': in_market_momentum.nlargest(self.num_assets_to_select).values})
            selected_out_of_market_asset =pd.DataFrame({'Asset': out_of_market_momentum.nlargest(1).index, 'Momentum': out_of_market_momentum.nlargest(1).values})

            adjusted_weights = self.adjust_weights(last_date_current_month, selected_assets, selected_out_of_market_asset)

            previous_value = portfolio_values[-1]
            month_end_data = self.trading_data.loc[last_date_current_month]
            last_date_next_month = self.trading_data.index[self.trading_data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self.trading_data.loc[last_date_next_month]

            monthly_returns = (next_month_end_data / month_end_data) - 1
            month_return = sum([monthly_returns.get(ticker, 0) * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)

            all_adjusted_weights.append(adjusted_weights)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.adjusted_weights = pd.Series(
            all_adjusted_weights,
            index=pd.date_range(start=self.start_date, periods=len(all_adjusted_weights), freq=freq)
        )
        self.data_models.portfolio_values = pd.Series(
            portfolio_values,
            index=pd.date_range(start=self.start_date, periods=len(portfolio_values), freq=freq)
        )
        self.data_models.portfolio_returns = pd.Series(
            portfolio_returns,
            index=pd.date_range(start=self.start_date, periods=len(portfolio_returns), freq=freq)
        )
