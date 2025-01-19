"""
Utilities module for processing and persisting results.
"""

import os

from datetime import datetime

def save_html(fig, filename, weights_filename, processing_type):
    """
    Save the HTML file to the 'artifacts' directory within the current working directory.

    Parameters:
    fig : plotly.graph_objects.Figure
        The figure object to save as an HTML file.
    filename : str
        The name of the HTML file.
    weights_filename : str
        The name of the directory for weights.
    processing_type : str
        The type of processing to include in the file path.
    """
    current_directory = os.getcwd()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    artifacts_directory = os.path.join(
        current_directory, "artifacts", weights_filename, timestamp
    )

    os.makedirs(artifacts_directory, exist_ok=True)
    file_path = os.path.join(artifacts_directory, f"{processing_type}_{filename}.html")
    fig.write_html(file_path)
