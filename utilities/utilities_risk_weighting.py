import numpy as np
import scipy.stats as stats

@staticmethod
def standard_deviation(returns):
    return np.std(returns, ddof=1)

@staticmethod
def square_root_kurtosis(returns):
    return np.sqrt(stats.kurtosis(returns, fisher=False))

@staticmethod
def mean_absolute_deviation(returns):
    return np.mean(np.abs(returns - np.mean(returns)))

@staticmethod
def semi_standard_deviation(returns):
    return np.std([x for x in returns if x < np.mean(returns)], ddof=1)

@staticmethod
def square_root_semi_kurtosis(returns):
    negative_returns = [x for x in returns if x < np.mean(returns)]
    return np.sqrt(stats.kurtosis(negative_returns, fisher=False))

@staticmethod
def first_lower_partial_moment(returns, threshold=0):
    return np.mean(np.maximum(threshold - returns, 0))

@staticmethod
def second_lower_partial_moment(returns, threshold=0):
    return np.sqrt(np.mean(np.square(np.maximum(threshold - returns, 0))))

@staticmethod
def value_at_risk(returns, alpha=0.05):
    return np.percentile(returns, 100 * alpha)

@staticmethod
def conditional_value_at_risk(returns, alpha=0.05):
    var = value_at_risk(returns, alpha)
    return np.mean([x for x in returns if x <= var])

@staticmethod
def entropic_value_at_risk(returns, alpha=0.05):
    lambda_ = np.log(1 / alpha)
    return -np.log(np.mean(np.exp(-lambda_ * returns))) / lambda_

@staticmethod
def worst_realization(returns):
    return np.min(returns)

# These use cumulative returns.

@staticmethod
def maximum_drawdown(cumulative_returns):
    peak = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - peak) / peak
    return np.min(drawdowns)

@staticmethod
def average_drawdown(cumulative_returns):
    peak = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - peak) / peak
    return np.mean(drawdowns)

@staticmethod
def drawdown_at_risk(cumulative_returns, alpha=0.05):
    drawdowns = (cumulative_returns - np.maximum.accumulate(cumulative_returns)) / np.maximum.accumulate(cumulative_returns)
    return np.percentile(drawdowns, 100 * alpha)

@staticmethod
def conditional_drawdown_at_risk(cumulative_returns, alpha=0.05):
    drawdowns = (cumulative_returns - np.maximum.accumulate(cumulative_returns)) / np.maximum.accumulate(cumulative_returns)
    dar = drawdown_at_risk(cumulative_returns, alpha)
    return np.mean([x for x in drawdowns if x <= dar])

@staticmethod
def entropic_drawdown_at_risk(cumulative_returns, alpha=0.05):
    drawdowns = (cumulative_returns - np.maximum.accumulate(cumulative_returns)) / np.maximum.accumulate(cumulative_returns)
    lambda_ = np.log(1 / alpha)
    return -np.log(np.mean(np.exp(-lambda_ * drawdowns))) / lambda_

# These use compounded cumulative returns.

@staticmethod
def maximum_drawdown_relative(compounded_cumulative_returns):
    peak = np.maximum.accumulate(compounded_cumulative_returns)
    drawdowns = (compounded_cumulative_returns - peak) / peak
    return np.min(drawdowns)

@staticmethod
def average_drawdown_relative(compounded_cumulative_returns):
    peak = np.maximum.accumulate(compounded_cumulative_returns)
    drawdowns = (compounded_cumulative_returns - peak) / peak
    return np.mean(drawdowns)

@staticmethod
def drawdown_at_risk_relative(compounded_cumulative_returns, alpha=0.05):
    drawdowns = (compounded_cumulative_returns - np.maximum.accumulate(compounded_cumulative_returns)) / np.maximum.accumulate(compounded_cumulative_returns)
    return np.percentile(drawdowns, 100 * alpha)

@staticmethod
def conditional_drawdown_at_risk_relative(compounded_cumulative_returns, alpha=0.05):
    drawdowns = (compounded_cumulative_returns - np.maximum.accumulate(compounded_cumulative_returns)) / np.maximum.accumulate(compounded_cumulative_returns)
    dar = drawdown_at_risk_relative(compounded_cumulative_returns, alpha)
    return np.mean([x for x in drawdowns if x <= dar])

@staticmethod
def entropic_drawdown_at_risk_relative(compounded_cumulative_returns, alpha=0.05):
    drawdowns = (compounded_cumulative_returns - np.maximum.accumulate(compounded_cumulative_returns)) / np.maximum.accumulate(compounded_cumulative_returns)
    lambda_ = np.log(1 / alpha)
    return -np.log(np.mean(np.exp(-lambda_ * drawdowns))) / lambda_
