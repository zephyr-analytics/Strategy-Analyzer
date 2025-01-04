"""
Utilities module for calculating portfolio statistics.
"""

import numpy as np

import pandas as pd

def calculate_cagr(portfolio_value, trading_frequency):
    """
    Calculates the Compound Annual Growth Rate (CAGR) of the portfolio.

    Parameters
    ----------
    portfolio_value : Series
        Series containing the portfolio value over time.
    trading_frequency : str, optional
        The frequency of trades. Either 'monthly' or 'bi-monthly'. Default is 'monthly'.

    Returns
    -------
    float
        CAGR value.
    """
    if trading_frequency == "Monthly":
        periods_per_year = 12
    elif trading_frequency == "Bi-Monthly":
        periods_per_year = 6
    elif trading_frequency == "Quarterly":
        periods_per_year = 4
    elif trading_frequency == "Yearly":
        periods_per_year = 1
    else:
        raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")

    total_periods = len(portfolio_value) - 1
    total_years = total_periods / periods_per_year

    cagr = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (1 / total_years) - 1
    return cagr


def calculate_cagr_monte_carlo(portfolio_value):
    """
    Calculates the Compound Annual Growth Rate (CAGR) of the portfolio for Monte Carlo simulation.

    Parameters
    ----------
    portfolio_value : Series
        Series containing the portfolio value over time.

    Returns
    -------
    float
        CAGR value.
    """
    total_period = len(portfolio_value) - 1
    cagr = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (1 / total_period) - 1
    return cagr


def calculate_average_annual_return(returns, trading_frequency):
    """
    Calculates the average annual return of the portfolio.

    Parameters
    ----------
    returns : Series
        Series containing the portfolio returns over time.
    trading_frequency : str, optional
        The frequency of trades. Either 'monthly' or 'bi-monthly'. Default is 'monthly'.

    Returns
    -------
    float
        Average annual return.
    """
    average_periodic_return = returns.mean()

    if trading_frequency == "Monthly":
        average_annual_return = (1 + average_periodic_return) ** 12 - 1
    elif trading_frequency == "Bi-Monthly":
        average_annual_return = (1 + average_periodic_return) ** 6 - 1
    elif trading_frequency == "Quarterly":
        average_annual_return = (1 + average_periodic_return) ** 4 - 1
    elif trading_frequency == "Yearly":
        average_annual_return = average_periodic_return
    else:
        raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")

    return average_annual_return


def calculate_max_drawdown(portfolio_value):
    """
    Calculates the maximum drawdown of the portfolio.

    Parameters
    ----------
    portfolio_value : Series
        Series containing the portfolio value over time.

    Returns
    -------
    float
        Maximum drawdown value.
    """
    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value / running_max) - 1
    max_drawdown = drawdown.min()
    return max_drawdown


def calculate_var_cvar(returns, confidence_level=0.95):
    """
    Calculates the Value at Risk (VaR) and Conditional Value at Risk (CVaR) of the portfolio.

    Parameters
    ----------
    returns : Series
        Series containing the portfolio returns over time.
    confidence_level : float, optional
        The confidence level for calculating VaR and CVaR. Default is 0.95.

    Returns
    -------
    tuple
        Tuple containing VaR and CVaR values.
    """
    sorted_returns = np.sort(returns.dropna())
    index = int(np.floor((1 - confidence_level) * len(sorted_returns)))
    index = max(0, min(index, len(sorted_returns) - 1))
    var = sorted_returns[index]
    cvar = sorted_returns[:index + 1].mean()

    return var, cvar


def calculate_annual_volatility(trading_frequency, portfolio_returns):
    """
    Calculates the annual volatility based on backtest results.

    Parameters
    ----------
    backtest : BacktestStaticPortfolio
        An instance of BacktestStaticPortfolio with completed backtest.

    Returns
    -------
    float
        The annual volatility of the portfolio.
    """
    if trading_frequency == "Monthly":
        annual_volatility = portfolio_returns.std() * np.sqrt(12)
    elif trading_frequency == "Bi-Monthly":
        annual_volatility = portfolio_returns.std() * np.sqrt(6)
    elif trading_frequency == "Quarterly":
        annual_volatility = portfolio_returns.std() * np.sqrt(4)
    elif trading_frequency == "Yearly":
        annual_volatility = portfolio_returns.std()
    else:
        raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")

    return annual_volatility


def calculate_standard_deviation(returns: pd.Series) -> FloatingPointError:
    """
    Calculates the standard deviation of the portfolio returns.

    Parameters
    ----------
    returns : Series
        Series containing the portfolio returns over time.

    Returns
    -------
    float
        Standard deviation of returns.
    """
    return returns.std()
