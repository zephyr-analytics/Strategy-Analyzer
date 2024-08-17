"""
Utilities module for helper methods of processors.
"""

from scipy.optimize import minimize
import numpy as np

def adjusted_weights(assets_weights, data, bond_ticker, cash_ticker, weighting_strategy, sma_period, current_date):
    """
    Adjusts the weights of the assets based on their SMA and the selected weighting strategy.

    Parameters
    ----------
    current_date : datetime
        The current date for which the weights are being adjusted.

    Returns
    -------
    dict
        Dictionary of adjusted asset weights.
    """
    if weighting_strategy == 'Use File Weights':
        new_weights = assets_weights.copy()
    elif weighting_strategy == 'Equal Weight':
        new_weights = equal_weighting(assets_weights)
    elif weighting_strategy == 'Risk Contribution':
        new_weights = risk_contribution_weighting(data.cov(), assets_weights)
    elif weighting_strategy == 'Min Volatility':
        weights = min_volatility_weighting(data.cov())
        new_weights = dict(zip(assets_weights.keys(), weights))
    elif weighting_strategy == 'Max Sharpe':
        returns = data.pct_change().mean()
        weights = max_sharpe_ratio_weighting(data.cov(), returns)
        new_weights = dict(zip(assets_weights.keys(), weights))
    else:
        raise ValueError("Invalid weighting strategy")
    for ticker in assets_weights.keys():
        if data.loc[:current_date, ticker].iloc[-1] < data.loc[:current_date, ticker].rolling(sma_period).mean().iloc[-1]:
            if data.loc[:current_date, bond_ticker].iloc[-1] < data.loc[:current_date, bond_ticker].rolling(sma_period).mean().iloc[-1]:
                new_weights[ticker] = 0
                new_weights[cash_ticker] = new_weights.get(cash_ticker, 0) + assets_weights[ticker]
            else:
                new_weights[ticker] = 0
                new_weights[bond_ticker] = new_weights.get(bond_ticker, 0) + assets_weights[ticker]
    total_weight = sum(new_weights.values())
    for ticker in new_weights:
        new_weights[ticker] /= total_weight
    print(f"Adjusted Weights on {current_date}: {new_weights}")
    return new_weights

def equal_weighting(assets_weights):
    """
    Returns equal weights for all assets in the portfolio.
    """
    num_assets = len(assets_weights)
    return {asset: 1.0 / num_assets for asset in assets_weights}

def risk_contribution_weighting(cov_matrix, assets_weights):
    """
    Returns weights based on risk contribution to the portfolio.
    """
    cov_matrix = cov_matrix.loc[assets_weights.keys(), assets_weights.keys()]

    def risk_contribution(weights, cov_matrix):
        portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        marginal_contrib = np.dot(cov_matrix, weights)
        risk_contrib = weights * marginal_contrib / portfolio_var
        return risk_contrib.sum()
    num_assets = len(assets_weights)
    initial_weights = np.ones(num_assets) / num_assets
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    bounds = tuple((0, 1) for asset in assets_weights)
    result = minimize(risk_contribution, initial_weights, args=(cov_matrix,), method='SLSQP', bounds=bounds, constraints=constraints)
    return dict(zip(assets_weights.keys(), result.x))


def min_volatility_weighting(cov_matrix):
    """
    Returns weights that minimize portfolio volatility.
    """
    num_assets = len(cov_matrix)
    def portfolio_volatility(weights, cov_matrix):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    initial_weights = np.ones(num_assets) / num_assets
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}
    bounds = tuple((0, 1) for _ in range(num_assets))
    result = minimize(portfolio_volatility, initial_weights, args=(cov_matrix,), method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x


def max_sharpe_ratio_weighting(cov_matrix, returns):
    """
    Returns weights that maximize the Sharpe ratio.
    """
    num_assets = len(cov_matrix)
    def negative_sharpe_ratio(weights, returns, cov_matrix, risk_free_rate=0.01):
        portfolio_return = np.sum(returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(portfolio_return - risk_free_rate) / portfolio_volatility
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    bounds = tuple((0, 1) for asset in range(num_assets))
    result = minimize(negative_sharpe_ratio, num_assets * [1. / num_assets,], args=(returns, cov_matrix), method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x
