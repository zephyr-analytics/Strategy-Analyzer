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
    total_period_years = (portfolio_value.index[-1] - portfolio_value.index[0]).days / 365.25
    
    if trading_frequency == 'monthly':
        periods_per_year = 12
    elif trading_frequency == 'bi-monthly':
        periods_per_year = 6
    else:
        raise ValueError("Invalid trading frequency. Choose 'monthly' or 'bi-monthly'.")

    total_periods = len(portfolio_value) - 1
    total_years = total_periods / periods_per_year

    cagr = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (1 / total_years) - 1
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
    
    if trading_frequency == 'monthly':
        average_annual_return = (1 + average_periodic_return) ** 12 - 1
    elif trading_frequency == 'bi-monthly':
        average_annual_return = (1 + average_periodic_return) ** 6 - 1
    else:
        raise ValueError("Invalid trading frequency. Choose 'monthly' or 'bi-monthly'.")

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
    cagr = calculate_cagr(backtest.get_portfolio_value(), backtest.trading_frequency)
    if backtest.trading_frequency == 'monthly':
        annual_volatility = backtest._returns.std() * np.sqrt(12)
    elif backtest.trading_frequency == 'bi-monthly':
        annual_volatility = backtest._returns.std() * np.sqrt(6)
    else:
        raise ValueError("Invalid trading frequency. Choose 'monthly' or 'bi-monthly'.")

    return initial_value, cagr, annual_volatility
