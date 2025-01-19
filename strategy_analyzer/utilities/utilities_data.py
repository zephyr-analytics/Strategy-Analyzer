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
    start_date : str
        The start date for fetching the data.
    end_date : str
        The end date for fetching the data.
    max_retries : int
        Number of retries if the download fails.
    delay : int
        Delay (in seconds) between retries.

    Returns
    -------
    DataFrame
        Adjusted closing prices of the assets.
    """
    session = requests.Session()

    if start_date and end_date is None:
        data = yf.download(all_tickers, timeout=30, session=session, threads=False)['Adj Close']
    else:
        data = yf.download(
            all_tickers, start=start_date, end=end_date, timeout=30, session=session, threads=False
        )['Adj Close']
    session.close()

    return data


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


def load_raw_data_file():
    """
    """
    file_path = os.path.join(os.getcwd(), "artifacts", "raw", "raw.csv")
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


def save_dataframe_to_csv(data, output_filename, processing_type):
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
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame.")

    current_directory = os.getcwd()
    current_date = datetime.now().strftime("%Y-%m-%d")
    artifacts_directory = os.path.join(current_directory, "artifacts", "data", f"{output_filename}")
    os.makedirs(artifacts_directory, exist_ok=True)

    full_path = os.path.join(
        artifacts_directory,
        f"{output_filename}_{current_date}_{processing_type}.csv"
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
    