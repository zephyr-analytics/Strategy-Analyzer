"""
Utilities module for adjusting weights.
"""

import numpy as np
import pandas as pd
import yfinance as yf


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
        returns_df,
        weights,
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


def calculate_pe_weighting(weights, cash_ticker=None, bond_ticker=None, benchmark_pe=15, max_weight=0.2):
    """
    Adjust weights based on the deviation of P/E ratios from a benchmark value,
    penalizing both very low (<=0) and very high (>15) P/E ratios, while preserving fixed weights.
    Ensures no position exceeds the specified maximum weight.

    Parameters
    ----------
    weights : dict
        Dictionary of asset weights with tickers as keys.
    cash_ticker : str, optional
        The ticker representing cash in the portfolio.
    bond_ticker : str, optional
        The ticker representing bonds in the portfolio.
    benchmark_pe : float, optional
        The benchmark P/E ratio used for weighting (default is 15).
    max_weight : float, optional
        Maximum allowable weight for any single asset (default is 20%).

    Returns
    -------
    dict
        Dictionary of assets and their adjusted weights based on relative P/E ratios.
    """
    # Identify fixed assets (cash & bonds) and their total weight
    fixed_assets = {cash_ticker, bond_ticker} & set(weights.keys())
    fixed_weight = sum(weights[asset] for asset in fixed_assets if asset in weights)

    # Select only adjustable assets (excluding fixed assets)
    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}
    adjustable_assets = list(adjustable_weights.keys())

    # Fetch P/E ratios for adjustable assets
    pe_ratios = {}
    for ticker in adjustable_assets:
        try:
            stock = yf.Ticker(ticker)
            pe_ratio = stock.info.get('trailingPE', 0)  # Convert NaN to 0
            if pe_ratio is None or np.isnan(pe_ratio):
                pe_ratio = 0  # Set to 0 if unavailable
            pe_ratios[ticker] = pe_ratio
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            pe_ratios[ticker] = 0  # Handle errors gracefully

    # Compute adjusted weights based on relative P/E penalties
    penalties = {}
    for ticker, pe in pe_ratios.items():
        if pe <= 0:  
            penalties[ticker] = 1e-6  # Harsh penalty for negative or zero P/E
        else:
            deviation = abs(pe - benchmark_pe)
            penalties[ticker] = 1 / (1 + deviation)  # More deviation → smaller weight

    # Scale penalties by the original asset weights
    weighted_penalties = {ticker: penalties[ticker] * adjustable_weights[ticker] for ticker in adjustable_weights}
    
    # Normalize to ensure sum of adjustable weights remains correct
    penalty_sum = sum(weighted_penalties.values()) or 1  # Prevent division by zero
    scaled_penalties = {ticker: weighted_penalties[ticker] / penalty_sum for ticker in weighted_penalties}
    
    # Reweight adjustable assets proportionally to total adjustable weight
    total_adjustable_weight = (1 - fixed_weight)
    adjusted_weights = {ticker: scaled_penalties[ticker] * total_adjustable_weight for ticker in scaled_penalties}

    # Include fixed assets with their original weights
    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    # Enforce maximum weight cap of 20%
    excess_weights = {k: max(0, v - max_weight) for k, v in adjusted_weights.items() if v > max_weight}
    excess_total = sum(excess_weights.values())

    if excess_total > 0:
        # Assets that are below the max weight cap
        redistributable_assets = {k: v for k, v in adjusted_weights.items() if v < max_weight}
        redistribution_factor = sum(redistributable_assets.values())

        if redistribution_factor > 0:
            for asset in redistributable_assets:
                adjusted_weights[asset] += (excess_total * (adjusted_weights[asset] / redistribution_factor))

        # Cap the assets exceeding max weight
        for asset in excess_weights:
            adjusted_weights[asset] = max_weight

    # Ensure sum of weights is 1 (small rounding adjustments if necessary)
    total_weight = sum(adjusted_weights.values())
    if not np.isclose(total_weight, 1):
        scaling_factor = 1 / total_weight
        adjusted_weights = {k: v * scaling_factor for k, v in adjusted_weights.items()}
    print(adjusted_weights)
    return adjusted_weights


def calculate_market_cap_weighting(weights, cash_ticker=None, bond_ticker=None, max_weight=0.2):
    """
    Adjust weights based on market capitalization without applying any penalty.
    Ensures no position exceeds the specified maximum weight.

    Parameters
    ----------
    weights : dict
        Dictionary of asset weights with tickers as keys.
    cash_ticker : str, optional
        The ticker representing cash in the portfolio.
    bond_ticker : str, optional
        The ticker representing bonds in the portfolio.
    max_weight : float, optional
        Maximum allowable weight for any single asset (default is 20%).

    Returns
    -------
    dict
        Dictionary of assets and their adjusted market cap weights.
    """
    # Identify fixed assets (cash & bonds) and their total weight
    fixed_assets = {cash_ticker, bond_ticker} & set(weights.keys())
    fixed_weight = sum(weights[asset] for asset in fixed_assets if asset in weights)

    # Select only adjustable assets (excluding fixed assets)
    adjustable_weights = {k: v for k, v in weights.items() if k not in fixed_assets}
    adjustable_assets = list(adjustable_weights.keys())

    # Fetch market capitalizations for adjustable assets
    market_caps = {}
    for ticker in adjustable_assets:
        try:
            stock = yf.Ticker(ticker)
            market_cap = stock.info.get('marketCap', 0)  # Get market cap, default to 0 if unavailable
            if market_cap is None or np.isnan(market_cap):
                market_cap = 0  # Handle missing data
            market_caps[ticker] = market_cap
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            market_caps[ticker] = 0  # Handle errors gracefully

    # Filter out tickers with zero market cap (invalid data)
    valid_market_caps = {k: v for k, v in market_caps.items() if v > 0}
    
    if not valid_market_caps:  # If all market caps are zero, revert to equal weighting
        adjusted_weights = {ticker: (1 - fixed_weight) / len(adjustable_assets) for ticker in adjustable_assets}
    else:
        # Compute raw market cap weights
        total_market_cap = sum(valid_market_caps.values())
        market_cap_weights = {ticker: market_caps[ticker] / total_market_cap for ticker in valid_market_caps}

        # Scale to fit within the adjustable weight allocation
        total_adjustable_weight = 1 - fixed_weight
        adjusted_weights = {ticker: market_cap_weights[ticker] * total_adjustable_weight for ticker in market_cap_weights}

    # Include fixed assets with their original weights
    for asset in fixed_assets:
        adjusted_weights[asset] = weights[asset]

    # Enforce maximum weight cap
    excess_weights = {k: max(0, v - max_weight) for k, v in adjusted_weights.items() if v > max_weight}
    excess_total = sum(excess_weights.values())

    if excess_total > 0:
        # Assets that are below the max weight cap
        redistributable_assets = {k: v for k, v in adjusted_weights.items() if v < max_weight}
        redistribution_factor = sum(redistributable_assets.values())

        if redistribution_factor > 0:
            for asset in redistributable_assets:
                adjusted_weights[asset] += (excess_total * (adjusted_weights[asset] / redistribution_factor))

        # Cap the assets exceeding max weight
        for asset in excess_weights:
            adjusted_weights[asset] = max_weight

    # Ensure sum of weights is 1 (small rounding adjustments if necessary)
    total_weight = sum(adjusted_weights.values())
    if not np.isclose(total_weight, 1):
        scaling_factor = 1 / total_weight
        adjusted_weights = {k: v * scaling_factor for k, v in adjusted_weights.items()}

    return adjusted_weights
