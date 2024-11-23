"""
Getter and Setter class for storing portfolio variables.
"""

from datetime import datetime

import pandas as pd


class PortfolioData:
    def __init__(self):
        """
        Initializes the Config class with default values for portfolio parameters.
        """
        self._portfolio_dataframe = pd.DataFrame


    @property
    def portfolio_dataframe(self):
        """
        Gets the portfolio dataframe.

        Returns
        -------
        portfolio_dataframe
            Dataframe containing data from backtesting.
        """
        return self._portfolio_dataframe

    @portfolio_dataframe.setter
    def portfolio_dataframe(self, value):
        """
        Sets the portfolio dataframe.

        Parameters
        ----------
        value
            Dataframe containing data from backtesting.            
        """
        self._portfolio_dataframe = value


