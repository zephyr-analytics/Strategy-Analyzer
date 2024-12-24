"""
Module for obtaining and persisting data.
"""

import os

import pandas as pd
from pandas import to_datetime

import utilities as utilities
from models.models_data import ModelsData


class DataObtainmentProcessor():
    """
    """

    def __init__(self, models_data: ModelsData):
        self.data_models = models_data
        self.weights_filename = self.data_models.weights_filename
        self.start_date = self.data_models.start_date
        self.end_date = self.data_models.end_date
        self.asset_weights = self.data_models.assets_weights
        self.cash_ticker = self.data_models.cash_ticker
        self.bond_ticker = self.data_models.bond_ticker
        self.sma_threshold_asset = self.data_models.sma_threshold_asset

    def process(self):
        """
        """
        file_path = self.check_and_load_data_file()
        data = self.read_data(file_path=file_path)
        dataframe = self.validate_data_file(dataframe=data)
        return dataframe


    def check_and_load_data_file(self):
        """
        Checks if the weights file exists. If not, fetches data, writes it to a file, and returns the path.
        
        Returns:
            str: Path to the existing or newly created file.
        """
        current_directory = os.getcwd()
        data_directory = os.path.join(current_directory, "artifacts", "raw")
        os.makedirs(data_directory, exist_ok=True)

        full_file_path = os.path.join(data_directory, f"{self.weights_filename}.csv")

        if os.path.exists(full_file_path):
            return full_file_path
        else:
            return self.fetch_and_save_data(full_file_path)


    def fetch_and_save_data(self, file_path):
        """
        Fetches the required data and saves it to the given file path.

        Parameters:
            file_path (str): The path where the file should be saved.

        Returns:
            str: The path to the saved file.
        """
        all_tickers = list(self.asset_weights.keys()) + [self.cash_ticker]
        if self.sma_threshold_asset:
            all_tickers.append(self.sma_threshold_asset)
        if self.bond_ticker:
            all_tickers.append(self.bond_ticker)

        df = utilities.fetch_data(
            all_tickers=all_tickers,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        utilities.write_raw_dataframe_to_csv(dataframe=df, file_path=file_path)

        return file_path


    def read_data(self, file_path):
        """
        Reads data from a CSV file, ensures the date column is properly formatted as a datetime index, 
        and returns the resulting DataFrame.

        Parameters
        ----------
        file_path : str
            The path to the CSV file containing the data.

        Returns
        -------
        pd.DataFrame
            The formatted DataFrame with a datetime index.
        """
        data = pd.read_csv(file_path, parse_dates=True, index_col=0)
        data.index = pd.to_datetime(data.index)

        return data


    def validate_data_file(self, dataframe):
        """
        Validate the contents of the loaded DataFrame based on the criteria.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to validate.

        Returns
        -------
        pd.DataFrame
            The validated DataFrame if all conditions are met
        """
        all_tickers = list(self.asset_weights.keys()) + [self.cash_ticker]
        if self.sma_threshold_asset:
            all_tickers.append(self.sma_threshold_asset)
        if self.bond_ticker:
            all_tickers.append(self.bond_ticker)

        all_valid = True

        expected_columns = set(all_tickers)
        actual_columns = set(dataframe.columns)
        if not expected_columns.issubset(actual_columns):
            all_valid = False

        if not pd.api.types.is_datetime64_any_dtype(dataframe.index):
            all_valid = False
        else:
            min_date = dataframe.index.min()
            max_date = dataframe.index.max()

            start_date = to_datetime(self.start_date)
            end_date = to_datetime(self.end_date)

            if abs((min_date - start_date).days) > 5:
                all_valid = False

            if abs((max_date - end_date).days) > 5:
                all_valid = False

        if all_valid:
            return dataframe
        else:
            dataframe = self.handle_failed_validation()
            return dataframe


    def handle_failed_validation(self):
        """
        """
        file_path = self.fetch_and_save_data()
        dataframe = self.read_data(file_path=file_path)

        return dataframe
