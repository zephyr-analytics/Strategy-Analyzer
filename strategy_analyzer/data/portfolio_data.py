"""
Getter and Setter class for storing data.
"""

import pandas as pd


class PortfolioData:
    """
    Getter and setter class for storing data for models and backtesting.
    """
    def __init__(self):
        """
        Initializes the Config class with default values for portfolio parameters.
        """
        self._trading_data = pd.DataFrame
        self._assets_data = pd.DataFrame
        self._benchmark_data = pd.DataFrame
        self._bond_data = pd.DataFrame
        self._cash_data = pd.DataFrame
        self._ma_threshold_data = pd.DataFrame
        self._out_of_market_data = pd.DataFrame


    @property
    def assets_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._assets_data

    @assets_data.setter
    def assets_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._assets_data = value


    @property
    def benchmark_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._benchmark_data

    @benchmark_data.setter
    def benchmark_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._benchmark_data = value


    @property
    def bond_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._bond_data

    @bond_data.setter
    def bond_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._bond_data = value


    @property
    def cash_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._cash_data

    @cash_data.setter
    def cash_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._cash_data = value


    @property
    def ma_threshold_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._ma_threshold_data

    @ma_threshold_data.setter
    def ma_threshold_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._ma_threshold_data = value


    @property
    def out_of_market_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._out_of_market_data

    @out_of_market_data.setter
    def out_of_market_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._out_of_market_data = value


    @property
    def trading_data(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._trading_data

    @trading_data.setter
    def trading_data(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._trading_data = value
