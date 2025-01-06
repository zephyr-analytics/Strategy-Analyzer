"""
Getter and Setter class for storing environment variables.
"""

from datetime import datetime

import pandas as pd


class ModelsData:
    def __init__(self):
        """
        Initializes the Config class with default values for portfolio parameters.
        """
        self._assets_weights = {}
        self._adjusted_weights = {}
        self._bond_ticker = ""
        self._buy_and_hold_values = pd.Series
        self._buy_and_hold_returns = pd.Series
        self._cash_ticker = "SHV"
        self._end_date = datetime.today().strftime('%Y-%m-%d')
        self._initial_portfolio_value = 10000
        self._num_simulations = 1000
        self._simulation_horizon = 10
        self._ma_window = "21"
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
        self._max_distance = 1.5
        self._ma_threshold_asset = ""
        self._num_assets_to_select = 1
        self._standard_deviation = None
        self._out_of_market_tickers = {}
        self._processing_type = str
        self._benchmark_asset = ""
        self._benchmark_values = pd.Series
        self._benchmark_returns = pd.Series
        self._contribution = None
        self._contribution_frequency = None
        self._return_metric = None
        self._risk_metric = None
        self._risk_tolerance = float(0.10)
        self._negative_mom = True
        self._ma_type = str
        self._fast_ma_period = ""
        self._slow_ma_period = ""


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


    @property
    def adjusted_weights(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._adjusted_weights

    @adjusted_weights.setter
    def adjusted_weights(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._adjusted_weights = value


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


    @property
    def ma_window(self):
        """
        Gets the SMA (Simple Moving Average) window for the backtest or simulation.

        Returns:
            int: The SMA window in days.
        """
        return self._ma_window

    @ma_window.setter
    def ma_window(self, value):
        """
        Sets the SMA (Simple Moving Average) window for the backtest or simulation.

        Args:
            value (int): The SMA window in days.
        """
        self._ma_window = value


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
    def max_distance(self):
        """
        # TODO write the docstrings.
        """
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        """
        # TODO write the docstrings.
        """
        self._max_distance = value


    @property
    def ma_threshold_asset(self):
        """
        Gets the sma threshold asset value used for portfolio management.

        Returns:
            str: The sam threshold asset as a string.
        """
        return self._ma_threshold_asset

    @ma_threshold_asset.setter
    def ma_threshold_asset(self, value):
        """
        Sets the sma threshold asset value used for portfolio management.

        Args:
            value (str): The asset ticker symbol to be set as the sma threshold asset.
        """
        self._ma_threshold_asset = value


    @property
    def num_assets_to_select(self):
        """
        Gets the threshold asset value used for portfolio management.

        Returns:
            str: The threshold asset as a string.
        """
        return self._num_assets_to_select

    @num_assets_to_select.setter
    def num_assets_to_select(self, value):
        """
        Sets the threshold asset value used for portfolio management.

        Args:
            value (str): The asset ticker symbol to be set as the threshold asset.
        """
        self._num_assets_to_select = value


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
    def out_of_market_tickers(self):
        """
        Gets the asset weights.

        Returns:
            dict: A dictionary containing the asset weights.
        """
        return self._out_of_market_tickers

    @out_of_market_tickers.setter
    def out_of_market_tickers(self, value):
        """
        Sets the asset weights.

        Args:
            value (dict): A dictionary containing the asset weights.
        """
        self._out_of_market_tickers = value


    @property
    def processing_type(self):
        """
        Gets the processing type.

        Returns:
            str: String representing the processing type.
        """
        return self._processing_type

    @processing_type.setter
    def processing_type(self, value):
        """
        Sets the processing type.

        Args:
            value (str): String representing the processing type.
        """
        self._processing_type = value


    @property
    def benchmark_asset(self):
        """
        Gets the benchmark_asset.

        Returns:
            str: String representing the benchmark_asset.
        """
        return self._benchmark_asset

    @benchmark_asset.setter
    def benchmark_asset(self, value):
        """
        Sets the benchmark_asset.

        Args:
            value (str): String representing the benchmark_asset.
        """
        self._benchmark_asset = value


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
    def contribution(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._contribution

    @contribution.setter
    def contribution(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._contribution = value


    @property
    def contribution_frequency(self):
        """
        Gets the contribution frequency.

        Returns:
            str: String representing the contribution frequency.
        """
        return self._contribution_frequency

    @contribution_frequency.setter
    def contribution_frequency(self, value):
        """
        Sets the contribution frequency.

        Args:
            value (str): String representing the contribution frequency.
        """
        self._contribution_frequency = value


    @property
    def risk_metric(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._risk_metric

    @risk_metric.setter
    def risk_metric(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._risk_metric = value


    @property
    def return_metric(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._return_metric

    @return_metric.setter
    def return_metric(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._return_metric = value


    @property
    def risk_tolerance(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._risk_tolerance

    @risk_tolerance.setter
    def risk_tolerance(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._risk_tolerance = value


    @property
    def negative_mom(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._negative_mom

    @negative_mom.setter
    def negative_mom(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._negative_mom = value


    @property
    def ma_type(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._ma_type

    @ma_type.setter
    def ma_type(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._ma_type = value


    @property
    def fast_ma_period(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._fast_ma_period

    @fast_ma_period.setter
    def fast_ma_period(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._fast_ma_period = value


    @property
    def slow_ma_period(self):
        """
        Gets the contribution.

        Returns:
            int: Integer representing the contribution.
        """
        return self._slow_ma_period

    @slow_ma_period.setter
    def slow_ma_period(self, value):
        """
        Sets the contribution.

        Args:
            value (int): Integer representing the contribution.
        """
        self._slow_ma_period = value
