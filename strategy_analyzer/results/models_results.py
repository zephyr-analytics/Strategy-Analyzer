"""
Getter and Setter class for storing environment variables.
"""

import pandas as pd


class ModelsResults:
    """
    Getter and setter class for storing model results.
    """
    def __init__(self):
        """
        Initializes the Config class with default values for portfolio parameters.
        """
        self._buy_and_hold_values = pd.Series
        self._buy_and_hold_returns = pd.Series
        self._portfolio_values = pd.Series
        self._portfolio_returns = pd.Series
        self._cagr = None
        self._average_annual_return = None
        self._max_drawdown = None
        self._var = None
        self._cvar = None
        self._annual_volatility = None
        self._standard_deviation = None
        self._benchmark_asset = ""
        self._benchmark_values = None
        self._benchmark_returns = None
        self._contribution = None
        self._contribution_frequency = None
        self._adjusted_weights = {}
        self._latest_weights = None
        self._simulation_results = None
        self._taxed_returns = None
        self._portfolio_values_non_con = None

    @property
    def adjusted_weights(self):
        """
        Gets the buy and hold values.

        Returns:
            str: The bond ticker symbol.
        """
        return self._adjusted_weights

    @adjusted_weights.setter
    def adjusted_weights(self, value):
        """
        Sets the buy and hold values.

        Args:
            value (str): The bond ticker symbol.
        """
        self._adjusted_weights = value


    @property
    def buy_and_hold_values(self):
        """
        Gets the buy and hold values.

        Returns:
            str: The bond ticker symbol.
        """
        return self._buy_and_hold_values

    @buy_and_hold_values.setter
    def buy_and_hold_values(self, value):
        """
        Sets the buy and hold values.

        Args:
            value (str): The bond ticker symbol.
        """
        self._buy_and_hold_values = value


    @property
    def buy_and_hold_returns(self):
        """
        Gets the buy and hold portfolio returns.

        Returns:
            str: The bond ticker symbol.
        """
        return self._buy_and_hold_returns

    @buy_and_hold_returns.setter
    def buy_and_hold_returns(self, value):
        """
        Sets the buy and hold portfolio returns.

        Args:
            value (str): The bond ticker symbol.
        """
        self._buy_and_hold_returns = value


    @property
    def portfolio_values(self):
        """
        Getter method for portfolio value.

        Returns
        -------
        Series
            The series of portfolio values.
        """
        return self._portfolio_values

    @portfolio_values.setter
    def portfolio_values(self, value):
        """
        Setter method for portfolio value.
        
        Parameters
        ----------
        portfolio_value : Series
            The series of portfolio values to be set.
        """
        self._portfolio_values = value


    @property
    def portfolio_returns(self):
        """
        Getter method for returns.

        Returns
        -------
        Series
            The series of portfolio returns.
        """
        return self._portfolio_returns

    @portfolio_returns.setter
    def portfolio_returns(self, value):
        """
        Setter method for returns.
        
        Parameters
        ----------
        returns : Series
            The series of portfolio returns to be set.
        """
        self._portfolio_returns = value


    @property
    def cagr(self):
        """
        Getter method for CAGR.

        Returns
        -------
        float
            The CAGR value.
        """
        return self._cagr

    @cagr.setter
    def cagr(self, value):
        """
        Setter method for CAGR.

        Parameters
        ----------
        value : float
            The CAGR value to be set.
        """
        self._cagr = value


    @property
    def average_annual_return(self):
        """
        Getter method for average annual return.

        Returns
        -------
        float
            The average annual return value.
        """
        return self._average_annual_return

    @average_annual_return.setter
    def average_annual_return(self, value):
        """
        Setter method for average annual return.

        Parameters
        ----------
        value : float
            The average annual return value to be set.
        """
        self._average_annual_return = value


    @property
    def max_drawdown(self):
        """
        Getter method for max drawdown.

        Returns
        -------
        float
            The maximum drawdown value.
        """
        return self._max_drawdown

    @max_drawdown.setter
    def max_drawdown(self, value):
        """
        Setter method for max drawdown.

        Parameters
        ----------
        value : float
            The maximum drawdown value to be set.
        """
        self._max_drawdown = value


    @property
    def var(self):
        """
        Getter method for Value at Risk (VaR).

        Returns
        -------
        float
            The VaR value.
        """
        return self._var

    @var.setter
    def var(self, value):
        """
        Setter method for Value at Risk (VaR).

        Parameters
        ----------
        value : float
            The VaR value to be set.
        """
        self._var = value


    @property
    def cvar(self):
        """
        Getter method for Conditional Value at Risk (CVaR).

        Returns
        -------
        float
            The CVaR value.
        """
        return self._cvar

    @cvar.setter
    def cvar(self, value):
        """
        Setter method for Conditional Value at Risk (CVaR).

        Parameters
        ----------
        value : float
            The CVaR value to be set.
        """
        self._cvar = value


    @property
    def annual_volatility(self):
        """
        # TODO write the docstrings.
        """
        return self._annual_volatility

    @annual_volatility.setter
    def annual_volatility(self, value):
        """
        # TODO write the docstrings.
        """
        self._annual_volatility = value


    @property
    def standard_deviation(self):
        """
        Gets the threshold asset value used for portfolio management.

        Returns:
            str: The threshold asset as a string.
        """
        return self._standard_deviation

    @standard_deviation.setter
    def standard_deviation(self, value):
        """
        Sets the threshold asset value used for portfolio management.

        Args:
            value (str): The asset ticker symbol to be set as the threshold asset.
        """
        self._standard_deviation = value


    @property
    def benchmark_values(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_values.
        """
        return self._benchmark_values

    @benchmark_values.setter
    def benchmark_values(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_values.
        """
        self._benchmark_values = value


    @property
    def benchmark_returns(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_asset.
        """
        return self._benchmark_returns

    @benchmark_returns.setter
    def benchmark_returns(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_asset.
        """
        self._benchmark_returns = value


    @property
    def latest_weights(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_asset.
        """
        return self._latest_weights

    @latest_weights.setter
    def latest_weights(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_asset.
        """
        self._latest_weights = value


    @property
    def simulation_results(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_asset.
        """
        return self._simulation_results

    @simulation_results.setter
    def simulation_results(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_asset.
        """
        self._simulation_results = value


    @property
    def taxed_returns(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_asset.
        """
        return self._taxed_returns

    @taxed_returns.setter
    def taxed_returns(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_asset.
        """
        self._taxed_returns = value


    @property
    def portfolio_values_non_con(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_asset.
        """
        return self._portfolio_values_non_con

    @portfolio_values_non_con.setter
    def portfolio_values_non_con(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_asset.
        """
        self._portfolio_values_non_con = value
