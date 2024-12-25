import numpy as np
import matplotlib.pyplot as plt
from enum import Enum, auto
import scipy.stats as stats

# PortfolioMetrics: Encapsulates all static methods for metrics
class PortfolioMetrics:
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
        var = PortfolioMetrics.value_at_risk(returns, alpha)
        return np.mean([x for x in returns if x <= var])

    @staticmethod
    def entropic_value_at_risk(returns, alpha=0.05):
        lambda_ = np.log(1 / alpha)
        return np.log(np.mean(np.exp(-lambda_ * returns))) / lambda_

    @staticmethod
    def worst_realization(returns):
        return np.min(returns)


# RiskMetrics: Enum to represent all available risk metrics
class RiskMetrics(Enum):
    STD_DEV = auto()
    SQUARE_ROOT_KURTOSIS = auto()
    MEAN_ABSOLUTE_DEVIATION = auto()
    SEMI_STD_DEV = auto()
    SQUARE_ROOT_SEMI_KURTOSIS = auto()
    FIRST_LOWER_PARTIAL_MOMENT = auto()
    SECOND_LOWER_PARTIAL_MOMENT = auto()
    VAR = auto()
    CVAR = auto()
    ENTROPIC_VAR = auto()
    WORST_REALIZATION = auto()


# EfficientFrontierProcessor: Generates and analyzes efficient frontiers
class EfficientFrontierProcessor:
    def __init__(self, returns):
        """
        Initialize the processor with asset returns.
        :param returns: A 2D NumPy array of shape (num_assets, num_time_periods).
        """
        self.returns = returns
        self.num_assets = returns.shape[0]
    
    def generate_random_weights(self, num_portfolios):
        """
        Generate random portfolio weights that sum to 1.
        :param num_portfolios: Number of random portfolios to generate.
        :return: A 2D array of random weights (num_portfolios, num_assets).
        """
        return np.random.dirichlet(np.ones(self.num_assets), size=num_portfolios)
    
    def calculate_portfolio_metrics(self, weights, risk_function):
        """
        Calculate portfolio returns and risk for each portfolio.
        :param weights: A 2D array of portfolio weights (num_portfolios, num_assets).
        :param risk_function: The risk metric function to use.
        :return: Portfolio returns and risks.
        """
        portfolio_returns = weights @ np.mean(self.returns, axis=1)
        portfolio_risks = []
        for w in weights:
            portfolio_return_series = w @ self.returns
            risk = risk_function(portfolio_return_series)
            portfolio_risks.append(risk)
        return portfolio_returns, np.array(portfolio_risks)
    
    def find_efficient_frontier(self, returns, risks):
        """
        Identify the portfolios on the efficient frontier.
        :param returns: Portfolio returns.
        :param risks: Portfolio risks.
        :return: Indices of the portfolios on the efficient frontier.
        """
        sorted_indices = np.argsort(risks)
        efficient_indices = []
        max_return = -np.inf
        for idx in sorted_indices:
            if returns[idx] > max_return:
                efficient_indices.append(idx)
                max_return = returns[idx]
        return efficient_indices

    def plot_all_risk_metrics(self, num_portfolios=1000):
            """
            Plot efficient frontiers for all defined risk metrics.
            :param num_portfolios: Number of random portfolios to generate.
            """
            # Mapping risk metrics to their respective functions
            risk_function_mapping = {
                RiskMetrics.STD_DEV: PortfolioMetrics.standard_deviation,
                RiskMetrics.SQUARE_ROOT_KURTOSIS: PortfolioMetrics.square_root_kurtosis,
                RiskMetrics.MEAN_ABSOLUTE_DEVIATION: PortfolioMetrics.mean_absolute_deviation,
                RiskMetrics.SEMI_STD_DEV: PortfolioMetrics.semi_standard_deviation,
                RiskMetrics.SQUARE_ROOT_SEMI_KURTOSIS: PortfolioMetrics.square_root_semi_kurtosis,
                RiskMetrics.FIRST_LOWER_PARTIAL_MOMENT: PortfolioMetrics.first_lower_partial_moment,
                RiskMetrics.SECOND_LOWER_PARTIAL_MOMENT: PortfolioMetrics.second_lower_partial_moment,
                RiskMetrics.VAR: lambda returns: PortfolioMetrics.value_at_risk(returns, alpha=0.05),
                RiskMetrics.CVAR: lambda returns: PortfolioMetrics.conditional_value_at_risk(returns, alpha=0.05),
                RiskMetrics.ENTROPIC_VAR: lambda returns: PortfolioMetrics.entropic_value_at_risk(returns, alpha=0.05),
                RiskMetrics.WORST_REALIZATION: PortfolioMetrics.worst_realization,
            }

            # Create a grid of subplots
            num_metrics = len(risk_function_mapping)
            num_cols = 3
            num_rows = (num_metrics + num_cols - 1) // num_cols
            fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows), constrained_layout=True)

            # Flatten axes for easier iteration
            axes = axes.flatten()

            for idx, (risk_metric, risk_function) in enumerate(risk_function_mapping.items()):
                # Generate random weights and calculate portfolio metrics
                random_weights = self.generate_random_weights(num_portfolios)
                portfolio_returns, portfolio_risks = self.calculate_portfolio_metrics(random_weights, risk_function)

                # Identify the efficient frontier (optimize for the lowest risk for the highest return)
                efficient_indices = self.find_efficient_frontier(portfolio_returns, portfolio_risks)
                frontier_returns = portfolio_returns[efficient_indices]
                frontier_risks = portfolio_risks[efficient_indices]

                # Find the optimal portfolio (highest return for lowest risk)
                sharpe_ratios = frontier_returns / frontier_risks  # Calculate Sharpe ratios for frontier portfolios
                optimal_idx = efficient_indices[np.argmax(sharpe_ratios)]  # Index of max Sharpe ratio
                optimal_return = portfolio_returns[optimal_idx]
                optimal_risk = portfolio_risks[optimal_idx]

                # Plot on the current axis
                ax = axes[idx]
                ax.scatter(portfolio_risks, portfolio_returns, c=portfolio_returns / portfolio_risks, cmap='viridis', s=10, label='Random Portfolios')
                # ax.scatter(frontier_risks, frontier_returns, color='red', marker='*', s=50, label='Efficient Frontier')
                ax.scatter(optimal_risk, optimal_return, color='blue', marker='*', s=150, edgecolors='black', label='Optimal Portfolio')
                ax.set_title(risk_metric.name.replace('_', ' '))
                ax.set_xlabel('Risk')
                ax.set_ylabel('Return')
                ax.grid(True)
                ax.legend()

            # Hide any unused axes
            for i in range(num_metrics, len(axes)):
                axes[i].axis('off')

            plt.suptitle("Efficient Frontiers for Different Risk Metrics", fontsize=16)
            plt.show()


import yfinance as yf
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt

# Import the previously defined EfficientFrontierProcessor, RiskMetrics, and PortfolioMetrics classes.

# Fetch historical data using yfinance
def fetch_data(tickers, start_date, end_date):
    """
    Fetch historical stock price data from Yahoo Finance.
    :param tickers: List of stock tickers.
    :param start_date: Start date as a string (YYYY-MM-DD).
    :param end_date: End date as a string (YYYY-MM-DD).
    :return: Daily returns as a NumPy array (assets x time periods).
    """
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    daily_returns = data.pct_change().dropna()  # Calculate daily returns
    return daily_returns.to_numpy().T, data.columns.tolist()

# Example Usage
if __name__ == "__main__":
    # Define tickers and date range
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    start_date = "2015-01-01"
    end_date = "2024-11-30"

    # Fetch data
    returns, asset_names = fetch_data(tickers, start_date, end_date)

    # Initialize the processor
    processor = EfficientFrontierProcessor(returns)

    # Generate the efficient frontier with CVaR as the risk metric
    processor.plot_all_risk_metrics(num_portfolios=1000)
