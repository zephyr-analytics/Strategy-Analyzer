"""
Abstract module for processing momentum trading models.
"""

import datetime
import logging
from datetime import datetime
from abc import ABC, abstractmethod

import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.processing_types import *
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.results.backtest_results_processor import BacktestResultsProcessor

logger = logging.getLogger(__name__)


class BacktestingProcessor(ABC):
    """
    Abstract base class for backtesting portfolios with configurable strategies.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results

        self.return_data = self.data_portfolio.trading_data.pct_change().dropna()


    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        all_adjusted_weights, portfolio_values, portfolio_returns = self.run_backtest()
        self._persist_portfolio_data(
            all_adjusted_weights=all_adjusted_weights,
            portfolio_values=portfolio_values,
            portfolio_returns=portfolio_returns
        )
        self._get_portfolio_statistics()
        self._calculate_buy_and_hold()
        self._calculate_benchmark()
        self.persist_data()
        if self.data_models.processing_type.endswith("BACKTEST"):
            results_processor = BacktestResultsProcessor(models_data=self.data_models, models_results=self.results_models)
            results_processor.process()

    @abstractmethod
    def get_portfolio_assets_and_weights(self, current_date: datetime):
        """
        Abstract method to encapsulate monthly asset selection.
        """

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

    @abstractmethod
    def adjust_weights(
            self,
            current_date: datetime,
            selected_assets: pd.DataFrame =None,
            selected_out_of_market_asset: pd.DataFrame=None,
            distances: pd.DataFrame=None
    ) -> dict:
        """
        Adjusts the weights of the assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : dict or None
            Optional preselected assets with weights. If None, uses `self.assets_weights`.
        selected_out_of_market_asset : dict or None
            Optional out-of-market assets to be used when replacing assets.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """

    # def calculate_weighting(self, adjusted_weights):
    #     """
    #     """
    #     if self.risk_metric == "Standard Deviation":
    #         utilities.calculate_standard_deviation_weighting(
    #             returns_df=self.return_data,
    #             weights=adjusted_weights,
    #             cash_ticker=self.cash_ticker,
    #             bond_ticker=self.bond_ticker
    #         )
    #     if self.risk_metric == "Conditional Value at Risk":
    #         utilities.calculate_conditional_value_at_risk_weighting(
    #             returns_df=self.return_data,
    #             weights=adjusted_weights,
    #             cash_ticker=self.cash_ticker,
    #             bond_ticker=self.bond_ticker
    #         )
    #     if self.risk_metric == "Max Drawdown":
    #         utilities.calculate_max_drawdown_weighting(
    #             returns_df=self.return_data,
    #             weights=adjusted_weights,
    #             cash_ticker=self.cash_ticker,
    #             bond_ticker=self.bond_ticker
    #         )

    #     return adjusted_weights

    def run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        monthly_dates = pd.date_range(start=self.data_models.start_date, end=self.data_models.end_date, freq='M')
        last_month_end = monthly_dates[-1]
        next_month_end = (last_month_end + pd.offsets.MonthEnd(1))
        if next_month_end not in monthly_dates:
            monthly_dates = monthly_dates.append(pd.DatetimeIndex([next_month_end]))

        portfolio_values = [int(self.data_models.initial_portfolio_value)]
        portfolio_returns = []
        all_adjusted_weights = []

        if self.data_models.trading_frequency == "Monthly":
            step = 1
        elif self.data_models.trading_frequency == "Bi-Monthly":
            step = 2
        elif self.data_models.trading_frequency == "Quarterly":
            step = 3
        elif self.data_models.trading_frequency == "Yearly":
            step = 12
        else:
            raise ValueError("Invalid trading frequency. Choose 'Monthly', 'Bi-Monthly', 'Quarterly', or 'Yearly'.")

        for i in range(0, len(monthly_dates), step):
            current_date = monthly_dates[i]
            last_date_current_month = self.data_portfolio.trading_data.index[
                self.data_portfolio.trading_data.index.get_loc(current_date, method='pad')
            ]

            adjusted_weights = self.get_portfolio_assets_and_weights(current_date=last_date_current_month)

            for j in range(step):
                if i + j >= len(monthly_dates) - 1:
                    break
                next_date = monthly_dates[i + j + 1]
                last_date_next_month = self.data_portfolio.trading_data.index[
                    self.data_portfolio.trading_data.index.get_loc(next_date, method='pad')
                ]
                month_end_data = self.data_portfolio.trading_data.loc[last_date_current_month]
                next_month_end_data = self.data_portfolio.trading_data.loc[last_date_next_month]
                monthly_returns = (next_month_end_data / month_end_data) - 1
                month_return = sum(
                    [monthly_returns.get(ticker, 0) * weight for ticker, weight in adjusted_weights.items()]
                )
                new_portfolio_value = portfolio_values[-1] * (1 + month_return)
                portfolio_values.append(new_portfolio_value)
                portfolio_returns.append(month_return)
                last_date_current_month = last_date_next_month
                all_adjusted_weights.append(adjusted_weights)

        return all_adjusted_weights, portfolio_values, portfolio_returns



    def _persist_portfolio_data(
            self, all_adjusted_weights: pd.Series, portfolio_values: pd.Series, portfolio_returns: pd.Series
    ):
        """
        Method to persist all data from the backtest to models_data for further analysis.

        Parameters
        ----------
        all_adjusted_weights : pd.Series
            Series of all weights and assets from the backtest.
        portfolio_values : pd.Series
            Series of all portfolio values from the backtest.
        portfolio_returns : pd.Series
            Series of all portfolio returns from the backtest.
        """
        self.results_models.adjusted_weights = pd.Series(
            all_adjusted_weights,
            index=pd.date_range(start=self.data_models.start_date, periods=len(all_adjusted_weights), freq="M")
        )
        self.results_models.portfolio_values = pd.Series(
            portfolio_values,
            index=pd.date_range(start=self.data_models.start_date, periods=len(portfolio_values), freq="M")
        )
        self.results_models.portfolio_returns = pd.Series(
            portfolio_returns,
            index=pd.date_range(start=self.data_models.start_date, periods=len(portfolio_returns), freq="M")
        )
        # logger.info("Portfolio Returns: %s, Portfolio Values: %s", self.results_models.portfolio_returns, self.results_models.portfolio_values)

    def _get_portfolio_statistics(self):
        """
        Calculates and sets portfolio statistics.
        """
        # TODO length of these needs to be adjusted.
        self.results_models.cagr = utilities.calculate_cagr(
            portfolio_value=self.results_models.portfolio_values
        )
        self.results_models.average_annual_return = utilities.calculate_average_annual_return(
            returns=self.results_models.portfolio_returns
        )
        self.results_models.max_drawdown = utilities.calculate_max_drawdown(
            portfolio_value=self.results_models.portfolio_values
        )
        self.results_models.var, self.results_models.cvar = utilities.calculate_var_cvar(
            returns=self.results_models.portfolio_returns
        )
        self.results_models.annual_volatility = utilities.calculate_annual_volatility(
            portfolio_returns=self.results_models.portfolio_returns
        )
        self.results_models.standard_deviation = utilities.calculate_standard_deviation(
            returns=self.results_models.portfolio_returns
        )


    def _calculate_buy_and_hold(self):
        """
        Calculates the buy-and-hold performance of the portfolio with the same assets and weights over the time frame.
        """
        bnh_data = self.data_portfolio.assets_data

        portfolio_values = [int(self.data_models.initial_portfolio_value)]
        portfolio_returns = []

        monthly_dates = pd.date_range(start=self.data_models.start_date, end=self.data_models.end_date, freq='M')
        
        for i in range(1, len(monthly_dates)):
            start_index = bnh_data.index.get_indexer([monthly_dates[i-1]], method='nearest')[0]
            end_index = bnh_data.index.get_indexer([monthly_dates[i]], method='nearest')[0]
            start_data = bnh_data.iloc[start_index]
            end_data = bnh_data.iloc[end_index]

            previous_value = portfolio_values[-1]
            monthly_returns = (end_data / start_data) - 1
            month_return = sum(
                [monthly_returns[ticker] * weight for ticker, weight in self.data_models.assets_weights.items()]
            )
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.results_models.buy_and_hold_values = pd.Series(
            portfolio_values, index=monthly_dates[:len(portfolio_values)]
        )
        self.results_models.buy_and_hold_returns = pd.Series(
            portfolio_returns, index=monthly_dates[1:len(portfolio_returns)+1]
        )


    def _calculate_benchmark(self):
        """
        Calculates the performance of a benchmark asset over the specified timeframe.
        """
        if not self.data_models.benchmark_asset:
            return
        else:
            benchmark_values = [int(self.data_models.initial_portfolio_value)]
            benchmark_returns = []

            monthly_dates = pd.date_range(start=self.data_models.start_date, end=self.data_models.end_date, freq='M')

            for i in range(1, len(monthly_dates)):
                start_index = self.data_portfolio.benchmark_data.index.get_indexer([monthly_dates[i-1]], method='nearest')[0]
                end_index = self.data_portfolio.benchmark_data.index.get_indexer([monthly_dates[i]], method='nearest')[0]

                start_price = self.data_portfolio.benchmark_data.iloc[start_index][self.data_models.benchmark_asset]
                end_price = self.data_portfolio.benchmark_data.iloc[end_index][self.data_models.benchmark_asset]

                monthly_return = (end_price / start_price) - 1

                previous_value = benchmark_values[-1]
                new_benchmark_value = previous_value * (1 + monthly_return)
                benchmark_values.append(new_benchmark_value)
                benchmark_returns.append(monthly_return)
    
            self.results_models.benchmark_values = pd.Series(
                benchmark_values, index=monthly_dates[:len(benchmark_values)]
            )
            self.results_models.benchmark_returns = pd.Series(
                benchmark_returns, index=monthly_dates[1:len(benchmark_returns)+1]
            )


    def persist_data(self):
        """
        Saves combined datasets to a single CSV file in the specified directory.
        """
        adjusted_weights_df = pd.DataFrame(
            list(self.results_models.adjusted_weights), index=self.results_models.adjusted_weights.index
        )
        adjusted_weights_df = adjusted_weights_df.fillna(0.0)
        combined_df = pd.concat(
            [
                adjusted_weights_df,
                self.results_models.portfolio_returns.rename("Portfolio Returns"),
                self.results_models.portfolio_values.rename("Portfolio Values"),
            ],
            axis=1,
        )

        utilities.save_dataframe_to_csv(
            data=combined_df,
            output_filename=self.data_models.weights_filename,
            processing_type=self.data_models.processing_type
        )
