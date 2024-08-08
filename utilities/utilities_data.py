import yfinance as yf
import pandas as pd
import os
from tkinter import filedialog
import plotly

def fetch_data(assets_weights, start_date, end_date, bond_ticker='BND', cash_ticker='SHV'):
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
    bond_ticker : str, optional
        The ticker symbol for the bond asset. Default is 'BND'.
    cash_ticker : str, optional
        The ticker symbol for the cash asset. Default is 'SHV'.

    Returns
    -------
    DataFrame
        DataFrame containing the adjusted closing prices of the assets.
    """
    all_tickers = list(assets_weights.keys()) + [bond_ticker, cash_ticker]
    data = yf.download(all_tickers, start=start_date, end=end_date)['Adj Close']
    return data

def load_weights():
    """
    Opens a file dialog to select a CSV file containing asset weights, and loads it into a dictionary.

    Returns
    -------
    dict
        Dictionary containing asset weights.
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        return df.set_index('Ticker')['Weight'].to_dict()
    return {}


def save_html(fig, filename):
    """
    Save the HTML file to the 'artifacts' directory within the current working directory.

    Parameters:
    fig : plotly.graph_objects.Figure
        The figure object to save as an HTML file.
    filename : str
        The name of the HTML file.
    """
    current_directory = os.getcwd()
    artifacts_directory = os.path.join(current_directory, 'artifacts')
    os.makedirs(artifacts_directory, exist_ok=True)
    file_path = os.path.join(artifacts_directory, filename)
    fig.write_html(file_path)
