"""
Module for obtaining and saving data to the raw directory.
"""

import datetime
import logging
import os
from datetime import datetime, timedelta

import pandas as pd
import pandas_datareader.data as web

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
            self.load_inflation_data()
        except Exception as e:
            logger.error("Error occurred during data processing: %s", e)
            raise

    def validate_and_update_raw_data(self):
        """
        Ensures that all necessary tickers are present in the raw data file and updates it if needed.
        If the end_date is not within 3 days of the current date, fetch new data rows for all columns.
        """
        file_dir = os.path.join(os.getcwd(), "artifacts", self.data_models.weights_filename, "raw_data")
        file_path = os.path.join(file_dir, f"{self.data_models.weights_filename}.csv")

        os.makedirs(file_dir, exist_ok=True)

        try:
            df = utilities.load_raw_data_file(filename=self.data_models.weights_filename)
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

    def load_inflation_data(self):
        """
        Load inflation data from a CSV file if it exists.
        If not, fetch it from FRED, save it, and then load it.
        Returns:
            pd.DataFrame: A DataFrame with inflation data.
        """
        csv_dir = os.path.join(os.getcwd(), "artifacts", "inflation_data")
        csv_file = "inflation_data.csv"
        csv_file_path = os.path.join(csv_dir, csv_file)

        if os.path.exists(csv_file_path):
            print("Loading data from existing CSV file...")
            infaltion_data =  pd.read_csv(csv_file_path, parse_dates=["DATE"], index_col="DATE")
            self.data_models.inflation_data = infaltion_data
        else:
            print("File not found. Fetching data from FRED...")
            infaltion_data = self.fetch_and_save_inflation_data()
            self.data_models.inflation_data = infaltion_data

    def fetch_and_save_inflation_data(self):
        """
        Fetch inflation data from FRED, save it to a CSV file, and return the data.
        Returns:
            pd.DataFrame: A DataFrame with fetched inflation data.
        """
        csv_dir = os.path.join(os.getcwd(), "artifacts", "inflation_data")
        csv_file = "inflation_data.csv"
        csv_file_path = os.path.join(csv_dir, csv_file)

        fred_series_id = "FPCPITOTLZGUSA"
        start_date = datetime(1990, 1, 1)
        end_date = datetime(2024, 1, 1)

        inflation_data = web.DataReader(fred_series_id, 'fred', start_date, end_date)
        inflation_data.rename(columns={fred_series_id: "inflation_data"}, inplace=True)

        inflation_data.index = pd.to_datetime(inflation_data.index)
        inflation_data.index.name = "DATE"

        monthly_dates = pd.date_range(start=inflation_data.index.min(), end=inflation_data.index.max(), freq="M")

        inflation_monthly = pd.DataFrame(index=monthly_dates)
        inflation_monthly.index.name = "DATE"

        inflation_monthly["inflation_data"] = inflation_monthly.index.to_series().apply(
            lambda x: inflation_data.loc[inflation_data.index.year == x.year, "inflation_data"].values[0]
            if x.year in inflation_data.index.year else None
        )

        inflation_monthly["inflation_rate"] = (1 + inflation_monthly["inflation_data"] / 100) ** (1 / 12) - 1

        inflation_monthly.reset_index(inplace=True)
        inflation_monthly.rename(columns={"index": "DATE"}, inplace=True)
        os.makedirs(csv_dir, exist_ok=True)
        inflation_monthly.to_csv(csv_file_path, index=False)
        print(f"Data saved to {csv_file_path}")

        return inflation_monthly
