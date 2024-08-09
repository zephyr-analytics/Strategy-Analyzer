from scipy.optimize import minimize
import numpy as np

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
