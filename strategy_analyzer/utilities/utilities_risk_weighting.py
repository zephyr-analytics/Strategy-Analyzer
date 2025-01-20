"""
Utilities module for adjusting weights.
"""

import numpy as np


def validate_weights(weights):
    """
    Validate that the sum of the weights equals 1.

    Parameters
    ----------
    weights : dict
        Dictionary of asset weights with asset names as keys and weights as values.

    Raises
    ------
    ValueError
        If the sum of the weights does not equal 1.
    """
    total_weight = sum(weights.values())
    if not np.isclose(total_weight, 1.0):
        raise ValueError(f"The sum of weights must equal 1. Current sum: {total_weight}")


def calculate_standard_deviation_weighting(returns_df, weights, cash_ticker=None, bond_ticker=None):
    """
    Calculate the standard deviation for each asset and adjust weights based on contribution to total risk.

    Parameters
    ----------
    returns_df : pandas.DataFrame
        DataFrame of daily percentage returns with assets as columns.
    weights : dict
        Dictionary of asset weights with asset names as keys and weights as values.
    cash_ticker : str, optional
        The ticker representing cash in the portfolio.
    bond_ticker : str, optional
        The ticker representing bonds in the portfolio.

    Returns
    -------
    dict
        Dictionary of assets and their adjusted weights based on standard deviation.
    """
    fixed_assets = {cash_ticker, bond_ticker} & set(weights.keys())
    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}

    portfolio_std = np.sqrt((
        returns_df[list(adjustable_weights.keys())] * list(adjustable_weights.values())
    ).sum(axis=1).var() * 252)
    risk_contributions = {
        asset: (returns_df[asset].std() * np.sqrt(252)) / portfolio_std for asset in adjustable_weights
    }
    total_risk_contribution = sum(risk_contributions.values())
    adjusted_weights = {asset: (1 - (risk / total_risk_contribution)) for asset, risk in risk_contributions.items()}
    adjusted_weights = {asset: weight / sum(adjusted_weights.values()) for asset, weight in adjusted_weights.items()}

    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    validate_weights(adjusted_weights)
    return adjusted_weights


def calculate_value_at_risk_weighting(returns_df, weights, confidence_level=0.95, cash_ticker=None, bond_ticker=None):
    """
    Calculate the Value at Risk (VaR) for each asset and adjust weights accordingly based on contribution to total risk.

    Parameters
    ----------
    returns_df : pandas.DataFrame
        DataFrame of daily percentage returns with assets as columns.
    weights : dict
        Dictionary of asset weights with asset names as keys and weights as values.
    confidence_level : float, optional
        Confidence level for VaR calculation (default is 0.95).
    cash_ticker : str, optional
        The ticker representing cash in the portfolio.
    bond_ticker : str, optional
        The ticker representing bonds in the portfolio.

    Returns
    -------
    dict
        Dictionary of assets and their adjusted weights based on VaR.
    """
    fixed_assets = {cash_ticker, bond_ticker} & set(weights.keys())
    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}

    portfolio_var = np.percentile((
        returns_df[list(adjustable_weights.keys())] * list(adjustable_weights.values())
    ).sum(axis=1), (1 - confidence_level) * 100) * np.sqrt(252)
    risk_contributions = {asset: (
        -np.percentile(returns_df[asset], (1 - confidence_level) * 100) * np.sqrt(252)
    ) / portfolio_var for asset in adjustable_weights}
    total_risk_contribution = sum(risk_contributions.values())
    adjusted_weights = {asset: (1 - (risk / total_risk_contribution)) for asset, risk in risk_contributions.items()}
    adjusted_weights = {asset: weight / sum(adjusted_weights.values()) for asset, weight in adjusted_weights.items()}

    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    validate_weights(adjusted_weights)
    return adjusted_weights


def calculate_conditional_value_at_risk_weighting(
        returns_df, weights,
        confidence_level=0.95,
        cash_ticker=None,
        bond_ticker=None
):
    """
    Calculate the Conditional Value at Risk for each asset and adjust weights based on contribution to total risk.

    Parameters
    ----------
    returns_df : pandas.DataFrame
        DataFrame of daily percentage returns with assets as columns.
    weights : dict
        Dictionary of asset weights with asset names as keys and weights as values.
    confidence_level : float, optional
        Confidence level for CVaR calculation (default is 0.95).
    cash_ticker : str, optional
        The ticker representing cash in the portfolio.
    bond_ticker : str, optional
        The ticker representing bonds in the portfolio.

    Returns
    -------
    dict
        Dictionary of assets and their adjusted weights based on CVaR.
    """
    fixed_assets = {cash_ticker, bond_ticker} & set(weights.keys())
    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}

    portfolio_cvar = (returns_df[list(adjustable_weights.keys())] * list(adjustable_weights.values())).sum(axis=1)
    portfolio_cvar = portfolio_cvar[
        portfolio_cvar <= np.percentile(portfolio_cvar, (1 - confidence_level) * 100)
    ].mean() * np.sqrt(252)
    risk_contributions = {}
    for asset in adjustable_weights:
        daily_var = -np.percentile(returns_df[asset], (1 - confidence_level) * 100)
        cvar = -returns_df[asset][returns_df[asset] <= daily_var].mean() * np.sqrt(252)
        risk_contributions[asset] = cvar / portfolio_cvar
    total_risk_contribution = sum(risk_contributions.values())
    adjusted_weights = {asset: (1 - (risk / total_risk_contribution)) for asset, risk in risk_contributions.items()}
    adjusted_weights = {asset: weight / sum(adjusted_weights.values()) for asset, weight in adjusted_weights.items()}

    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    validate_weights(adjusted_weights)
    return adjusted_weights


def calculate_max_drawdown_weighting(returns_df, weights, cash_ticker=None, bond_ticker=None):
    """
    Calculate the maximum drawdown for each asset and adjust weights accordingly based on contribution to total risk.

    Parameters
    ----------
    returns_df : pandas.DataFrame
        DataFrame of daily percentage returns with assets as columns.
    weights : dict
        Dictionary of asset weights with asset names as keys and weights as values.
    cash_ticker : str, optional
        The ticker representing cash in the portfolio.
    bond_ticker : str, optional
        The ticker representing bonds in the portfolio.

    Returns
    -------
    dict
        Dictionary of assets and their adjusted weights based on max drawdown.
    """
    fixed_assets = {cash_ticker, bond_ticker} & set(weights.keys())
    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}

    portfolio_drawdown = (
        returns_df[list(adjustable_weights.keys())] * list(adjustable_weights.values())
    ).sum(axis=1)
    cumulative_returns = (1 + portfolio_drawdown).cumprod()
    running_max = cumulative_returns.cummax()
    portfolio_max_drawdown = ((cumulative_returns - running_max) / running_max).min()

    risk_contributions = {}
    for asset in adjustable_weights:
        cumulative_returns = (1 + returns_df[asset]).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        risk_contributions[asset] = max_drawdown / portfolio_max_drawdown
    total_risk_contribution = sum(risk_contributions.values())
    adjusted_weights = {asset: (1 - (risk / total_risk_contribution)) for asset, risk in risk_contributions.items()}
    adjusted_weights = {asset: weight / sum(adjusted_weights.values()) for asset, weight in adjusted_weights.items()}

    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    validate_weights(adjusted_weights)
    return adjusted_weights
