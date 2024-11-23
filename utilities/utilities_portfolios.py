import pandas as pd
from tkinter import filedialog
import os

def load_portfolio():
    """
    Opens a file dialog to select a portfolio CSV file and loads it into a pandas DataFrame.
    Ensures the first column is treated as the date index and the rest as columns.

    Returns
    -------
    tuple
        A tuple containing:
        - DataFrame: The loaded portfolio data.
        - str: The filename of the uploaded file.

    Raises
    ------
    ValueError
        If the selected file is not a valid CSV or does not contain proper date-indexed data.
    """
    try:
        # Open file dialog to select the CSV file
        file_path = filedialog.askopenfilename(
            title="Select Portfolio File",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return None, None  # User canceled the file dialog

        # Load the CSV file into a DataFrame
        portfolio_data = pd.read_csv(file_path, index_col=0, parse_dates=True)

        # Validate that the index is a DatetimeIndex
        if not isinstance(portfolio_data.index, pd.DatetimeIndex):
            raise ValueError("The first column must contain dates in a recognizable format.")

        # Return the DataFrame and file name
        return portfolio_data

    except Exception as e:
        raise ValueError(f"Failed to load portfolio file: {e}")
