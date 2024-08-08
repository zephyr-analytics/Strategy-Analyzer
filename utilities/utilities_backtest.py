import numpy as np
import pandas as pd


def calculate_cagr(portfolio_value):
    """
    Calculates the Compound Annual Growth Rate (CAGR) of the portfolio.

    Parameters
    ----------
    portfolio_value : Series
        Series containing the portfolio value over time.

    Returns
    -------
    float
        CAGR value.
    """
    total_period = (portfolio_value.index[-1] - portfolio_value.index[0]).days / 365.25
    cagr = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (1 / total_period) - 1
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


def calculate_average_annual_return(returns):
    """
    Calculates the average annual return of the portfolio.

    Parameters
    ----------
    returns : Series
        Series containing the portfolio returns over time.

    Returns
    -------
    float
        Average annual return.
    """
    average_monthly_return = returns.mean()
    average_annual_return = (1 + average_monthly_return) ** 12 - 1
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
    drawdown = (portfolio_value - running_max) / running_max
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
    index = int((1 - confidence_level) * len(sorted_returns))
    var = sorted_returns[index]
    cvar = sorted_returns[:index].mean()
    return var, cvar


def calculate_portfolio_metrics(backtest):
    """
    Calculates the initial portfolio value, CAGR, and annual volatility based on backtest results.

    Parameters
    ----------
    backtest : BacktestStaticPortfolio
        An instance of BacktestStaticPortfolio with completed backtest.

    Returns
    -------
    tuple
        Tuple containing the initial portfolio value, CAGR, and annual volatility.
    """
    initial_value = backtest.get_portfolio_value().iloc[0]
    cagr = calculate_cagr(backtest.get_portfolio_value())
    annual_volatility = backtest._returns.std() * np.sqrt(12)
    return initial_value, cagr, annual_volatility