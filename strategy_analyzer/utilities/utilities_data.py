"""
Utilities module for loading and processing data.
"""

import os

from datetime import datetime
from tkinter import filedialog

import pandas as pd
import yfinance as yf
import requests


def fetch_data(all_tickers, start_date=None, end_date=None):
    """
    Fetches the adjusted closing prices of the assets within the specified date range.

    Parameters
    ----------
    all_tickers : list
        List of asset tickers.
    start_date : str or None
        The start date for fetching the data (YYYY-MM-DD).
    end_date : str or None
        The end date for fetching the data (YYYY-MM-DD).

    Returns
    -------
    DataFrame
        Adjusted closing prices of the assets.
    """
    data = yf.download(
        tickers=all_tickers,
        start=start_date,
        end=end_date,
        group_by='ticker',
        auto_adjust=False
    )

    # Handle both single and multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        adj_close = pd.concat({ticker: data[ticker]["Adj Close"] for ticker in all_tickers if "Adj Close" in data[ticker]}, axis=1)
    else:
        adj_close = data[["Adj Close"]]
        adj_close.columns = all_tickers if len(all_tickers) == 1 else adj_close.columns

    return adj_close


def load_weights():
    """
    Opens a file dialog to select a CSV file containing asset weights, and loads it into a dictionary.

    Returns
    -------
    dict, str
        Dictionary containing asset weights and the filename.
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        weights = df.set_index('Ticker')['Weight'].to_dict()
        filename = os.path.basename(file_path)
        return weights, filename
    return {}, ""


def load_raw_data_file(filename) -> pd.DataFrame:
    """
    Loads raw data file for portfolio.

    Parameters
    ----------
    filename : str
        String representing the portfolio name.
    """
    file_path = os.path.join(os.getcwd(), "artifacts", f"{filename}", "raw_data", f"{filename}.csv")
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

    return df


def read_data(file_path: str):
    """
    Reads a CSV file from the 'artifacts/raw' directory and returns a DataFrame.

    Parameters
    ----------
    weights_filename : str
        String representing the filename to be selected from directory.

    Returns
    -------
    Dataframe
        Dataframe of data used for model creation.
    """
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return df


def strip_csv_extension(filename):
    """
    Strips the .csv extension from the given filename.

    Parameters
    ----------
    filename : str
        The filename from which to remove the .csv extension.

    Returns
    -------
    str
        The filename without the .csv extension.
    """
    return os.path.splitext(filename)[0]


def save_dataframe_to_csv(data, weights_filename, processing_type):
    """
    Saves a pandas DataFrame to a CSV file in a structured directory with metadata in the file name.

    Parameters:
        data (pd.DataFrame): The DataFrame to save.
        output_filename (str): A descriptor for the output file.
        trading_frequency (str): The trading frequency to include in the file name.
        num_assets_to_select (int): The number of assets to include in the file name.

    Returns:
        str: The full path of the saved file.
    """
    current_directory = os.getcwd()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    artifacts_directory = os.path.join(
        current_directory, "artifacts", weights_filename, processing_type
    )
    os.makedirs(artifacts_directory, exist_ok=True)

    full_path = os.path.join(
        artifacts_directory,
        f"{timestamp}_{weights_filename}_{processing_type}.csv"
    )

    data.to_csv(full_path, index=True)


def write_raw_dataframe_to_csv(dataframe, file_path):
    """
    Writes a DataFrame to a .csv file.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to write to a CSV file.
    file_path : str
        The file path where the CSV will be saved.
    include_index : bool, optional, default=True
        Whether to include the DataFrame index in the CSV file.

    Returns
    -------
    None
    """
    dataframe.to_csv(file_path, index=True)
    