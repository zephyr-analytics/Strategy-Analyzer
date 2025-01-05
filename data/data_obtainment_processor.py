"""
Module for obtaining and saving data to the raw directory.
"""

import os
from logger import logger
import utilities as utilities
from models.models_data import ModelsData

class DataObtainmentProcessor:
    """
    Class for obtaining and saving data.
    """

    def __init__(self, models_data: ModelsData):
        self.data_models = models_data
        self.weights_filename = self.data_models.weights_filename
        self.start_date = self.data_models.start_date
        self.end_date = self.data_models.end_date
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
            logger.info(f"Obtaining Data for {self.weights_filename}.")
            self.fetch_and_save_data()
        except Exception as e:
            logger.error(f"Error occurred during data processing: {e}")
            raise

    def fetch_and_save_data(self):
        """
        Fetches the required data and saves it to the raw directory.
        """
        all_tickers = list(self.asset_weights.keys())

        if self.cash_ticker:
            all_tickers.append(self.cash_ticker)
        if self.bond_ticker:
            all_tickers.append(self.bond_ticker)
        if self.ma_threshold_asset:
            all_tickers.append(self.ma_threshold_asset)
        if self.benchmark_asset:
            all_tickers.append(self.benchmark_asset)
        if self.out_of_market_tickers:
            all_tickers.extend(self.out_of_market_tickers.keys())

        data_directory = os.path.join(os.getcwd(), "artifacts", "raw")
        os.makedirs(data_directory, exist_ok=True)

        file_path = os.path.join(data_directory, f"{self.weights_filename}.csv")

        logger.info("Fetching data for tickers: %s", all_tickers)
        df = utilities.fetch_data(
            all_tickers=all_tickers,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        utilities.write_raw_dataframe_to_csv(dataframe=df, file_path=file_path)
        logger.info(f"Data successfully saved to {file_path}.")
