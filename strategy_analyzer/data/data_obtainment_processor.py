"""
Module for obtaining and saving data to the raw directory.
"""

import logging
import os
from datetime import datetime, timedelta

import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.models.models_data import ModelsData

logger = logging.getLogger(__name__)

class DataObtainmentProcessor:
    """
    Class for obtaining and saving data.
    """
    def __init__(self, models_data: ModelsData):
        self.data_models = models_data
        self.end_date = datetime.now() + timedelta(days=1)
        # TODO when pulling a single asset that asset needs to be relabeled from Adj Close to the ticker symbol.

    def process(self):
        """
        Main method to fetch and save data to the raw directory.
        """
        try:
            logger.info("Validating raw data file.")
            self.validate_and_update_raw_data()
        except Exception as e:
            logger.error("Error occurred during data processing: %s", e)
            raise

    def validate_and_update_raw_data(self):
        """
        Ensures that all necessary tickers are present in the raw data file and updates it if needed.
        If the end_date is not within 3 days of the current date, fetch new data rows for all columns.
        """
        file_dir = os.path.join(os.getcwd(), "artifacts", "raw")
        file_path = os.path.join(file_dir, "raw.csv")

        os.makedirs(file_dir, exist_ok=True)

        try:
            df = utilities.load_raw_data_file()
        except FileNotFoundError:
            logger.info("Raw data file not found. Creating a new one.")
            df = pd.DataFrame()

        all_tickers = set(self.data_models.assets_weights.keys())

        if self.data_models.cash_ticker:
            all_tickers.add(self.data_models.cash_ticker)
        if self.data_models.bond_ticker:
            all_tickers.add(self.data_models.bond_ticker)
        if self.data_models.ma_threshold_asset:
            all_tickers.add(self.data_models.ma_threshold_asset)
        if self.data_models.benchmark_asset:
            all_tickers.add(self.data_models.benchmark_asset)
        if self.data_models.out_of_market_tickers:
            all_tickers.update(self.data_models.out_of_market_tickers.keys())

        missing_tickers = all_tickers - set(df.columns)

        if missing_tickers:
            logger.info("Missing tickers detected. Fetching missing data: %s", missing_tickers)
            new_data = utilities.fetch_data(all_tickers=list(missing_tickers))
            df = pd.concat([df, new_data], axis=1)

        current_date = datetime.now()
        if (self.end_date - current_date).days > 3:
            latest_date_in_df = df.index.max()
            logger.info("Fetching data from %s to %s for all columns.", latest_date_in_df, self.end_date)
            updated_data = utilities.fetch_data(
                all_tickers=list(df.columns),
                start_date=latest_date_in_df,
                end_date=self.end_date
            )
            df = pd.concat([df, updated_data], axis=0)

        df.to_csv(file_path)
        logger.info("Updated raw data saved to %s.", file_path)
