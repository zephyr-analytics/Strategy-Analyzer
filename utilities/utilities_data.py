"""
Utilities module for loading and processing data.
"""

import os

from datetime import datetime
from tkinter import filedialog

import pandas as pd
import yfinance as yf


def fetch_data(all_tickers, start_date, end_date):
    """
    Fetches and trims the adjusted closing prices of the assets to the common earliest date,
    while providing information about the earliest common start date and trimmed assets.

    Parameters
    ----------
    all_tickers : list
        List of asset tickers.
    start_date : str
        The start date for fetching the data.
    end_date : str
        The end date for fetching the data.

    Returns
    -------
    tuple
        A tuple containing:
        - DataFrame: Trimmed adjusted closing prices of the assets.
        - str: Message indicating the earliest common start date and the assets causing trimming.
    """
    data = yf.download(all_tickers, start=start_date, end=end_date)['Adj Close']

    original_start_dates = data.apply(lambda col: col.first_valid_index())

    common_start_date = original_start_dates.max()

    trimmed_assets = original_start_dates[original_start_dates < common_start_date].index.tolist()
    
    trimmed_data = data.loc[common_start_date:].dropna(how='any', axis=0)

    message = (
        f"The earliest common start date is {common_start_date.date()}. "
        f"Data reduction was caused by these assets: {', '.join(trimmed_assets) if trimmed_assets else 'None'}."
    )
    
    return trimmed_data, message


def fetch_out_of_market_data(assets_tickers, start_date, end_date):
    """
    Fetches the adjusted closing prices of the assets.

    Parameters
    ----------
    assets_weights : dict
        Dictionary of asset tickers and their corresponding weights in the portfolio.
    start_date : str
        The start date for fetching the data.
    end_date : str
        The end date for fetching the data.

    Returns
    -------
    DataFrame
        DataFrame containing the adjusted closing prices of the assets.
    """
    all_tickers = list(assets_tickers.keys())
    data = yf.download(all_tickers, start=start_date, end=end_date)['Adj Close']
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


def save_html(fig, filename, weights_filename, output_filename, processing_type, num_assets):
    """
    Save the HTML file to the 'artifacts' directory within the current working directory.

    Parameters:
    fig : plotly.graph_objects.Figure
        The figure object to save as an HTML file.
    filename : str
        The name of the HTML file.
    output_filename : str
        The output filename to include in the file path.
    """
    current_directory = os.getcwd()
    current_date = datetime.now().strftime("%Y-%m-%d")
    artifacts_directory = os.path.join(current_directory, 'artifacts', "plots", f"{weights_filename}")
    os.makedirs(artifacts_directory, exist_ok=True)

    file_path = os.path.join(artifacts_directory, f"{output_filename}_{current_date}_{processing_type}_assets{num_assets}_{filename}.html")
    fig.write_html(file_path)


def save_dataframe_to_csv(data, output_filename, processing_type, num_assets):
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

    full_path = os.path.join(artifacts_directory, f"{output_filename}_{current_date}_{processing_type}_assets{num_assets}.csv")

    data.to_csv(full_path, index=True)

