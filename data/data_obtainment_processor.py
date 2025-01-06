"""
Module for obtaining and saving data to the raw directory.
"""

import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from logger import logger
import utilities as utilities
from models.models_data import ModelsData

logger = logging.getLogger(__name__)


class DataObtainmentProcessor:
    """
    Class for obtaining and saving data.
    """

    def __init__(self, models_data: ModelsData):
        self.data_models = models_data
        self.weights_filename = self.data_models.weights_filename
        self.end_date = pd.to_datetime(self.data_models.end_date)
        self.asset_weights = self.data_models.assets_weights
        self.cash_ticker = self.data_models.cash_ticker
        self.bond_ticker = self.data_models.bond_ticker
        self.ma_threshold_asset = self.data_models.ma_threshold_asset
        self.benchmark_asset = self.data_models.benchmark_asset
        self.out_of_market_tickers = self.data_models.out_of_market_tickers

    def process(self):
        """
        Main method to fetch and save data to the raw directory.
        """
        try:
            logger.info("Validating raw data file.")
            self.validate_and_update_raw_data()
        except Exception as e:
            logger.error(f"Error occurred during data processing: {e}")
            raise

    def validate_and_update_raw_data(self):
        """
        Ensures that all necessary tickers are present in the raw data file and updates it if needed.
        If the end_date is not within 3 days of the current date, fetch new data rows for all columns.
        """
        file_path = os.path.join(os.getcwd(), "artifacts", "raw", "raw.csv")
        try:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        except FileNotFoundError:
            logger.info("Raw data file not found. Creating a new one.")
            df = pd.DataFrame()

        all_tickers = set(self.asset_weights.keys())

        if self.cash_ticker:
            all_tickers.add(self.cash_ticker)
        if self.bond_ticker:
            all_tickers.add(self.bond_ticker)
        if self.ma_threshold_asset:
            all_tickers.add(self.ma_threshold_asset)
        if self.benchmark_asset:
            all_tickers.add(self.benchmark_asset)
        if self.out_of_market_tickers:
            all_tickers.update(self.out_of_market_tickers.keys())

        missing_tickers = all_tickers - set(df.columns)

        if missing_tickers:
            logger.info("Missing tickers detected. Fetching missing data: %s", missing_tickers)
            new_data = utilities.fetch_data(all_tickers=list(missing_tickers))
            df = pd.concat([df, new_data], axis=1)

        current_date = datetime.now()
        if (self.end_date - current_date).days > 3:
            latest_date_in_df = df.index.max()
            logger.info(f"Fetching data from {latest_date_in_df} to {self.end_date} for all columns.")
            updated_data = utilities.fetch_data(all_tickers=list(df.columns), start_date=latest_date_in_df, end_date=self.end_date)
            df = pd.concat([df, updated_data], axis=0)

        df.to_csv(file_path)
        logger.info(f"Updated raw data saved to {file_path}.")

    def load_raw_data_file(self):
        """
        Loads the raw data file.
        """
        file_path = os.path.join(os.getcwd(), "artifacts", "raw", "raw.csv")
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        return df
