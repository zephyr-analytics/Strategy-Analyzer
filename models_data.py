"""
Getter and Setter class for storing environment variables.
"""

import pandas as pd

class ModelsData:
    def __init__(self):
        """
        Initializes the Config class with default values for portfolio parameters.
        """
        self._assets_weights = {}
        self._bond_ticker = "BND"
        self._cash_ticker = "SGOV"
        self._end_date = "2024-01-01"
        self._initial_portfolio_value = 10000
        self._num_simulations = 1000
        self._simulation_horizon = 10
        self._sma_window = "21"
        self._start_date = "2010-01-01"
        self._theme_mode = "Light"
        self._trading_frequency = "Monthly"
        self._weighting_strategy = "Use File Weights"
        self._weights_filename = ""
        self._portfolio_values = pd.Series
        self._portfolio_returns = pd.Series
        self._cagr = None
        self._average_annual_return = None
        self._max_drawdown = None
        self._var = None
        self._cvar = None
        self._annual_volatility = None
        self._max_distance = 0.75

    # Getter and Setter for assets_weights
    @property
    def assets_weights(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._assets_weights

    @assets_weights.setter
    def assets_weights(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._assets_weights = value

    # Getter and Setter for bond_ticker
    @property
    def bond_ticker(self):
        """
        Gets the bond ticker symbol.

        Returns:
            str: The bond ticker symbol.
        """
        return self._bond_ticker

    @bond_ticker.setter
    def bond_ticker(self, value):
        """
        Sets the bond ticker symbol.

        Args:
            value (str): The bond ticker symbol.
        """
        self._bond_ticker = value

    # Getter and Setter for cash_ticker
    @property
    def cash_ticker(self):
        """
        Gets the cash ticker symbol.

        Returns:
            str: The cash ticker symbol.
        """
        return self._cash_ticker

    @cash_ticker.setter
    def cash_ticker(self, value):
        """
        Sets the cash ticker symbol.

        Args:
            value (str): The cash ticker symbol.
        """
        self._cash_ticker = value

    # Getter and Setter for end_date
    @property
    def end_date(self):
        """
        Gets the end date for the backtest or simulation.

        Returns:
            str: The end date in YYYY-MM-DD format.
        """
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        """
        Sets the end date for the backtest or simulation.

        Args:
            value (str): The end date in YYYY-MM-DD format.
        """
        self._end_date = value

    # Getter and Setter for initial_portfolio_value
    @property
    def initial_portfolio_value(self):
        """
        Gets the initial value of the portfolio.

        Returns:
            float: The initial portfolio value.
        """
        return self._initial_portfolio_value

    @initial_portfolio_value.setter
    def initial_portfolio_value(self, value):
        """
        Sets the initial value of the portfolio.

        Args:
            value (float): The initial portfolio value.
        """
        self._initial_portfolio_value = value

    # Getter and Setter for num_simulations
    @property
    def num_simulations(self):
        """
        Gets the number of simulations to run.

        Returns:
            int: The number of simulations.
        """
        return self._num_simulations

    @num_simulations.setter
    def num_simulations(self, value):
        """
        Sets the number of simulations to run.

        Args:
            value (int): The number of simulations.
        """
        self._num_simulations = value

    # Getter and Setter for simulation_horizon
    @property
    def simulation_horizon(self):
        """
        Gets the simulation horizon in years.

        Returns:
            int: The simulation horizon in years.
        """
        return self._simulation_horizon

    @simulation_horizon.setter
    def simulation_horizon(self, value):
        """
        Sets the simulation horizon in years.

        Args:
            value (int): The simulation horizon in years.
        """
        self._simulation_horizon = value

    # Getter and Setter for sma_window
    @property
    def sma_window(self):
        """
        Gets the SMA (Simple Moving Average) window for the backtest or simulation.

        Returns:
            int: The SMA window in days.
        """
        return self._sma_window

    @sma_window.setter
    def sma_window(self, value):
        """
        Sets the SMA (Simple Moving Average) window for the backtest or simulation.

        Args:
            value (int): The SMA window in days.
        """
        self._sma_window = value

    # Getter and Setter for start_date
    @property
    def start_date(self):
        """
        Gets the start date for the backtest or simulation.

        Returns:
            str: The start date in YYYY-MM-DD format.
        """
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        """
        Sets the start date for the backtest or simulation.

        Args:
            value (str): The start date in YYYY-MM-DD format.
        """
        self._start_date = value

    # Getter and Setter for theme_mode
    @property
    def theme_mode(self):
        """
        Gets the theme mode for the application (e.g., Light or Dark).

        Returns:
            str: The theme mode.
        """
        return self._theme_mode

    @theme_mode.setter
    def theme_mode(self, value):
        """
        Sets the theme mode for the application.

        Args:
            value (str): The theme mode (e.g., Light or Dark).
        """
        self._theme_mode = value

    # Getter and Setter for trading_frequency
    @property
    def trading_frequency(self):
        """
        Gets the trading frequency (e.g., Monthly, Bi-Monthly).

        Returns:
            str: The trading frequency.
        """
        return self._trading_frequency

    @trading_frequency.setter
    def trading_frequency(self, value):
        """
        Sets the trading frequency (e.g., Monthly, Bi-Monthly).

        Args:
            value (str): The trading frequency.
        """
        self._trading_frequency = value

    # Getter and Setter for weighting_strategy
    @property
    def weighting_strategy(self):
        """
        Gets the weighting strategy for the portfolio.

        Returns:
            str: The weighting strategy.
        """
        return self._weighting_strategy

    @weighting_strategy.setter
    def weighting_strategy(self, value):
        """
        Sets the weighting strategy for the portfolio.

        Args:
            value (str): The weighting strategy.
        """
        self._weighting_strategy = value

    # Getter and Setter for weights_filename
    @property
    def weights_filename(self):
        """
        Gets the filename of the weights file.

        Returns:
            str: The filename of the weights file.
        """
        return self._weights_filename

    @weights_filename.setter
    def weights_filename(self, value):
        """
        Sets the filename of the weights file.

        Args:
            value (str): The filename of the weights file.
        """
        self._weights_filename = value

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
        return self._annual_volatility
    
    @annual_volatility.setter
    def annual_volatility(self, value):
        self._annual_volatility = value

    @property
    def max_distance(self):
        return self._max_distance
    
    @max_distance.setter
    def max_distance(self, value):
        self._max_distance = value