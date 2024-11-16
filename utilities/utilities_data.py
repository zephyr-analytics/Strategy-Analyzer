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
    Fetches the adjusted closing prices of the assets.

    Parameters
    ----------
    all_assets : list
        List of asset tickers.
    start_date : str
        The start date for fetching the data.
    end_date : str
        The end date for fetching the data.

    Returns
    -------
    DataFrame
        DataFrame containing the adjusted closing prices of the assets.
    """
    data = yf.download(all_tickers, start=start_date, end=end_date)['Adj Close']
    return data


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


def save_html(fig, filename, output_filename):
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
    artifacts_directory = os.path.join(current_directory, 'artifacts')
    os.makedirs(artifacts_directory, exist_ok=True)
    
    file_path = os.path.join(artifacts_directory, f"{output_filename}_{current_date}_{filename}.html")
    fig.write_html(file_path)
