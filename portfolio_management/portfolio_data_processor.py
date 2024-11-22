

import pandas as pd


class PortfolioDataProcessor:
    def __init__(self, file_path=None):
        # TODO there needs to be a data path supplied based on the selected file by the user.
        pass

    def read_data(file_path):
        """
        Reads a CSV file and returns it as a Pandas DataFrame.

        Args:
            file_path (str): The path to the .csv file.

        Returns:
            pd.DataFrame: DataFrame containing the CSV data.
        """
        try:
            df = pd.read_csv(file_path)
            print(f"Successfully loaded data from {file_path}.")
            return df
        except Exception as e:
            print(f"Error loading file: {e}")
            raise

    # TODO this then gets parsed and placed within portfolio_data.
    # TODO create the portfolio_data getter and setter.
    # TODO After the portoflio_data object will get passed to the portoflio analyzer.
    # TODO The portfolio analyzer will offer weighting based on adjusting weights of the strategy for best outcome. 
    # TODO Outcomes will then be judged based on optimization of best return with either least CVaR or least MaxDrawdown.
