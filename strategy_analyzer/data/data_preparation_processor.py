"""
Module for preparing data for models and backtesting.
"""

import logging
import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData

logger = logging.getLogger(__name__)


class DataPreparationProcessor:
    """
    Class for obtaining and persisting data with retry mechanisms and validation.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.end_date = pd.to_datetime(self.data_models.end_date)
        self.min_time = 8

    def process(self):
        """
        Main method to check, load, and validate data.
        """
        logger.info("Preparing Data for %s.", self.data_models.weights_filename)
        data = self._read_data()
        trimmed_data = self._trim_data(data)
        self._parse_data(filtered_data=trimmed_data)

    def _read_data(self) -> pd.DataFrame:
        """
        Method to read and filter data using utility functions.

        Returns
        -------
        Dataframe
            Dataframe of filtered data from the raw data file.
        """
        full_data = utilities.load_raw_data_file(filename=self.data_models.weights_filename)

        if self.min_time is not None:
            min_time_offset = pd.DateOffset(years=self.min_time)
            earliest_date = full_data.index.max()
            cutoff_date = earliest_date - min_time_offset
            print(cutoff_date)
            dropped_tickers = [
                ticker for ticker in full_data.columns
                if full_data.loc[:cutoff_date, ticker].dropna().empty
            ]

            if dropped_tickers:
                logger.info(
                    "Tickers dropped due to insufficient data for  %s years: %s",
                    self.min_time,
                    ', '.join(dropped_tickers)
                )

                for ticker in dropped_tickers:
                    self.data_models.assets_weights.pop(ticker, None)

                filtered_data = full_data.drop(columns=dropped_tickers)
            else:
                pass
        else:
            filtered_data = full_data

        return filtered_data

    def _trim_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Trim data based on the start date or use the earliest available date if specified.

        Parameters
        ----------
        data : pd.DataFrame
            The input data to be trimmed.

        Returns
        -------
        pd.DataFrame
            Trimmed data based on the specified or earliest start date.
        """
        if self.data_models.start_date == "Earliest":
            earliest_dates = data.apply(lambda col: col.dropna().index.min(), axis=0)
            overall_start_date = max(earliest_dates.max(), data.dropna(how='all').index.min()).date()
            logger.info("Using 'Earliest' start date based on data: %s", overall_start_date)
        else:
            specified_start_date = pd.to_datetime(self.data_models.start_date).date()
            overall_start_date = max(specified_start_date, data.dropna(how='all').index.min().date())
            logger.info("Using specified start date: %s", overall_start_date)

        self.data_models.start_date = pd.to_datetime(overall_start_date)

        data.index = pd.to_datetime(data.index).date
        trimmed_data = data.loc[overall_start_date:self.end_date]

        return trimmed_data

    def _parse_data(self, filtered_data):
        """
        Method to parse and organize filtered data into portfolio components.

        Parameters
        ----------
        filtered_data : Dataframe
        """
        tickers_to_check = (
            set(self.data_models.assets_weights.keys()) |
            {self.data_models.cash_ticker, self.data_models.bond_ticker, self.data_models.ma_threshold_asset, self.data_models.benchmark_asset} |
            set(self.data_models.out_of_market_tickers)
        )

        filtered_data = filtered_data.loc[:, filtered_data.columns.intersection(tickers_to_check)]

        self.data_portfolio.trading_data = filtered_data

        self.data_portfolio.assets_data = filtered_data.loc[
            :, filtered_data.columns.intersection(self.data_models.assets_weights.keys())
        ]

        if self.data_models.cash_ticker in filtered_data.columns:
            self.data_portfolio.cash_data = filtered_data[[self.data_models.cash_ticker]]

        if self.data_models.bond_ticker in filtered_data.columns:
            self.data_portfolio.bond_data = filtered_data[[self.data_models.bond_ticker]]

        if self.data_models.ma_threshold_asset in filtered_data.columns:
            self.data_portfolio.ma_threshold_data = filtered_data[[self.data_models.ma_threshold_asset]]

        if self.data_models.benchmark_asset in filtered_data.columns:
            self.data_portfolio.benchmark_data = filtered_data[[self.data_models.benchmark_asset]]

        out_of_market_data = filtered_data.loc[
            :, filtered_data.columns.intersection(self.data_models.out_of_market_tickers)
        ]
        if not out_of_market_data.empty:
            self.data_portfolio.out_of_market_data = out_of_market_data

        logger.info("Data successfully prepared.")
