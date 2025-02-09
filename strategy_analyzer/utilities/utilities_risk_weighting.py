"""
Utilities module for adjusting weights.
"""

import numpy as np
import pandas as pd

def validate_and_adjust_weights(weights, max_weight=0.30):
    """
    Ensure that the sum of the weights equals 1 by proportionally adjusting them if necessary.
    Ensures all weights are non-negative and no weight exceeds the maximum threshold.

    Parameters
    ----------
    weights : dict
        Dictionary of asset weights with asset names as keys and weights as values.
    max_weight : float, optional
        Maximum allowable weight per asset (default is 30%).

    Returns
    -------
    dict
        Adjusted weights that sum to exactly 1 and remain within constraints.
    """
    weights = {asset: max(weight, 0) for asset, weight in weights.items()}

    over_weight_assets = {asset: weight for asset, weight in weights.items() if weight > max_weight}

    if over_weight_assets:
        capped_weights = {asset: min(weight, max_weight) for asset, weight in weights.items()}

        total_excess = sum(weights.values()) - sum(capped_weights.values())

        under_weight_assets = {asset: weight for asset, weight in capped_weights.items() if weight < max_weight}
        total_under_weight = sum(under_weight_assets.values())

        if total_under_weight > 0:
            for asset in under_weight_assets:
                capped_weights[asset] += (under_weight_assets[asset] / total_under_weight) * total_excess
        
        weights = capped_weights

    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {asset: weight / total_weight for asset, weight in weights.items()}

    return weights


def calculate_conditional_value_at_risk_weighting(
        returns_df, weights,
        confidence_level=0.95,
        cash_ticker=None,
        bond_ticker=None
):
    """
    Calculate the Conditional Value at Risk (CVaR) for each asset and adjust weights based on contribution to total risk.

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
    fixed_weight = sum(weights[asset] for asset in fixed_assets if asset in weights)

    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}
    adjustable_assets = list(adjustable_weights.keys())

    portfolio_returns = (returns_df[adjustable_assets] * list(adjustable_weights.values())).sum(axis=1)

    portfolio_var_threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
    portfolio_cvar = -portfolio_returns[portfolio_returns <= portfolio_var_threshold].mean() * np.sqrt(252)

    risk_contributions = {}
    for asset in adjustable_assets:
        marginal_cvar = -((returns_df[asset] * adjustable_weights[asset])[portfolio_returns <= portfolio_var_threshold].mean())
        risk_contributions[asset] = max(marginal_cvar / portfolio_cvar, 1e-6)

    adjusted_weights = {asset: (1 / risk) for asset, risk in risk_contributions.items()}

    total_adjustable_weight = sum(adjusted_weights.values())

    if total_adjustable_weight > 0:
        adjusted_weights = {asset: (weight / total_adjustable_weight) * (1 - fixed_weight) for asset, weight in adjusted_weights.items()}

    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    adjusted_weights = validate_and_adjust_weights(adjusted_weights)

    return adjusted_weights
