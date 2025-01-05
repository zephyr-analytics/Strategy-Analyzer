"""
Module for obtaining and persisting data.
"""

import os
import time
from datetime import timedelta

import pandas as pd
from pandas import to_datetime

import utilities as utilities
from models.models_data import ModelsData


class DataObtainmentProcessor:
    """
    Class for obtaining and persisting data with retry mechanisms and validation.
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
        Main method to check, load, and validate data.
        """
        file_path = self.check_and_load_data_file()
        data = self.read_data(file_path=file_path)
        dataframe = self.validate_data_file(dataframe=data)
        return dataframe

    def retry(func):
        """
        Decorator to retry a function up to 3 times with exponential backoff.
        """
        def wrapper(*args, **kwargs):
            retries = 3
            delay = 5
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        print("All retry attempts failed.")
                        raise
        return wrapper

    @retry
    def check_and_load_data_file(self):
        """
        Checks if the weights file exists. If not, fetches data, writes it to a file, and returns the path.
        """
        current_directory = os.getcwd()
        data_directory = os.path.join(current_directory, "artifacts", "raw")
        os.makedirs(data_directory, exist_ok=True)

        full_file_path = os.path.join(data_directory, f"{self.weights_filename}.csv")

        if os.path.exists(full_file_path):
            print("File found.")
            return full_file_path
        else:
            print("File not found. Fetching data...")
            return self.fetch_and_save_data(full_file_path)

    @retry
    def fetch_and_save_data(self, file_path):
        """
        Fetches the required data and saves it to the given file path.
        """
        all_tickers = list(self.asset_weights.keys()) + [self.cash_ticker]

        optional_assets = [
            self.ma_threshold_asset,
            self.bond_ticker,
            self.benchmark_asset,
        ]

        all_tickers.extend(asset for asset in optional_assets if asset)

        if self.out_of_market_tickers:
            all_tickers.extend(self.out_of_market_tickers.keys())

        df = utilities.fetch_data(
            all_tickers=all_tickers,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        utilities.write_raw_dataframe_to_csv(dataframe=df, file_path=file_path)
        print(f"Data successfully saved to {file_path}.")

        return file_path

    @retry
    def read_data(self, file_path):
        """
        Reads data from a CSV file, ensures the date column is properly formatted as a datetime index,
        drops duplicate index values, and sorts the index.
        """
        data = pd.read_csv(file_path, parse_dates=True, index_col=0)
        data.index = pd.to_datetime(data.index)

        data = data[~data.index.duplicated(keep='first')].sort_index()

        print("Data loaded successfully with duplicates removed and index sorted.")
        return data

    @retry
    def validate_data_file(self, dataframe):
        """
        Validates the contents of the loaded DataFrame. Handles missing columns, misaligned date ranges,
        and ensures no duplicate data is introduced during fetching or appending. Allows a ±5-day variance.
        """
        dataframe = dataframe[~dataframe.index.duplicated(keep='first')].sort_index()

        start_date_buffered = to_datetime(self.start_date) - timedelta(days=5)
        end_date_buffered = to_datetime(self.end_date) + timedelta(days=5)

        print(f"Validating data range with a ±5-day buffer: {start_date_buffered} to {end_date_buffered}")

        all_tickers = list(self.asset_weights.keys()) + [self.cash_ticker]
        optional_assets = [self.ma_threshold_asset, self.bond_ticker, self.benchmark_asset]
        all_tickers.extend(asset for asset in optional_assets if asset)

        if self.out_of_market_tickers:
            all_tickers.extend(self.out_of_market_tickers.keys())

        expected_columns = set(all_tickers)
        actual_columns = set(dataframe.columns)
        missing_columns = expected_columns - actual_columns

        if missing_columns:
            print(f"Missing columns detected: {missing_columns}. Fetching missing data...")
            missing_data = utilities.fetch_data(
                all_tickers=list(missing_columns),
                start_date=start_date_buffered,
                end_date=end_date_buffered,
            )

            dataframe = dataframe.combine_first(missing_data).sort_index()

            file_path = os.path.join(os.getcwd(), "artifacts", "raw", f"{self.weights_filename}.csv")
            utilities.write_raw_dataframe_to_csv(dataframe=dataframe, file_path=file_path)
            print(f"Missing data added and saved to {file_path}.")

        if dataframe.index.min() > start_date_buffered or dataframe.index.max() < end_date_buffered:
            print(f"Data range misaligned. Adjusting to match {start_date_buffered} to {end_date_buffered}...")

            missing_start = dataframe.index.min() > start_date_buffered
            missing_end = dataframe.index.max() < end_date_buffered

            if missing_start or missing_end:
                missing_dates_data = utilities.fetch_data(
                    all_tickers=list(expected_columns),
                    start_date=start_date_buffered if missing_start else dataframe.index.min(),
                    end_date=end_date_buffered if missing_end else dataframe.index.max(),
                )

                dataframe = dataframe.combine_first(missing_dates_data).sort_index()

        dataframe = dataframe.loc[start_date_buffered:end_date_buffered]

        file_path = os.path.join(os.getcwd(), "artifacts", "raw", f"{self.weights_filename}.csv")
        utilities.write_raw_dataframe_to_csv(dataframe=dataframe, file_path=file_path)
        print(f"Date range adjusted and saved to {file_path}.")

        if not pd.api.types.is_datetime64_any_dtype(dataframe.index):
            raise ValueError("Index validation failed. The index must be of datetime type.")

        print("Validation passed.")
        return dataframe
