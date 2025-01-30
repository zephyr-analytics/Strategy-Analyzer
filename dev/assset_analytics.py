import pandas as pd
import numpy as np
import plotly.express as px


class AssetContributionProcessor:
    def __init__(self, weights, returns, benchmark_returns=None, factor_exposures=None, covariance_matrix=None):
        """
        Initialize the Asset Contribution Processor.

        Parameters:
        - weights (pd.Series): Asset weights in the portfolio (index: asset names).
        - returns (pd.DataFrame): Asset returns (index: dates, columns: asset names).
        - benchmark_returns (pd.Series): Benchmark returns (optional).
        - factor_exposures (pd.DataFrame): Factor exposures for assets (optional).
        - covariance_matrix (pd.DataFrame): Asset covariance matrix (optional).
        """
        self.weights = weights
        self.returns = returns
        self.benchmark_returns = benchmark_returns
        self.factor_exposures = factor_exposures
        self.covariance_matrix = covariance_matrix

    def calculate_return_contribution(self):
        """Calculate asset contribution to portfolio return."""
        contribution = self.weights * self.returns
        portfolio_return = contribution.sum(axis=1)
        return contribution, portfolio_return

    def calculate_risk_contribution(self):
        """Calculate asset contribution to portfolio risk (volatility)."""
        if self.covariance_matrix is None:
            raise ValueError("Covariance matrix is required for risk contribution.")
        
        portfolio_volatility = np.sqrt(
            self.weights.T @ self.covariance_matrix @ self.weights
        )
        marginal_risk = self.covariance_matrix @ self.weights
        risk_contribution = self.weights * marginal_risk / portfolio_volatility
        return risk_contribution, portfolio_volatility

    def calculate_factor_contribution(self):
        """Calculate contribution of assets to factor exposures."""
        if self.factor_exposures is None:
            raise ValueError("Factor exposures are required for factor contribution.")
        
        factor_contributions = self.weights[:, None] * self.factor_exposures
        return factor_contributions

    def calculate_tracking_error_contribution(self):
        """Calculate contribution to portfolio tracking error."""
        if self.benchmark_returns is None:
            raise ValueError("Benchmark returns are required for tracking error.")
        
        active_returns = self.returns.sub(self.benchmark_returns, axis=0)
        tracking_error = np.sqrt((self.weights * active_returns).var(axis=0).sum())
        tracking_error_contribution = self.weights * active_returns / tracking_error
        return tracking_error_contribution, tracking_error

    def calculate_drawdown_contribution(self):
        """Calculate contribution to portfolio drawdown."""
        cumulative_returns = (1 + self.returns).cumprod()
        max_returns = cumulative_returns.cummax()
        drawdowns = (cumulative_returns - max_returns) / max_returns
        
        drawdown_contribution = self.weights * drawdowns
        max_drawdown = drawdowns.min()
        return drawdown_contribution, max_drawdown

    def calculate_beta_contribution(self):
        """Calculate asset contribution to portfolio beta."""
        betas = self.returns.corrwith(self.returns.mean(axis=1))
        beta_contribution = self.weights * betas
        portfolio_beta = beta_contribution.sum()
        return beta_contribution, portfolio_beta

    def calculate_marginal_risk_contribution(self):
        """Calculate marginal risk contribution."""
        if self.covariance_matrix is None:
            raise ValueError("Covariance matrix is required for marginal risk contribution.")
        
        marginal_risk = self.covariance_matrix @ self.weights
        portfolio_risk = np.sqrt(self.weights.T @ self.covariance_matrix @ self.weights)
        marginal_risk_contribution = marginal_risk / portfolio_risk
        return marginal_risk_contribution

    def calculate_expected_shortfall_contribution(self, percentile=5):
        """Calculate expected shortfall contribution."""
        sorted_returns = self.returns.sort_values(axis=0, ascending=True)
        threshold_index = int(len(sorted_returns) * percentile / 100)
        shortfall_returns = sorted_returns.iloc[:threshold_index]
        expected_shortfall = shortfall_returns.mean(axis=0)
        es_contribution = self.weights * expected_shortfall
        return es_contribution, expected_shortfall.mean()

    def visualize_contributions(self, contribution_df, title, ylabel):
        """
        Visualize contributions using Plotly bar chart.
        
        Parameters:
        - contribution_df (pd.DataFrame or pd.Series): Contribution data (columns or index: asset names).
        - title (str): Chart title.
        - ylabel (str): Y-axis label (for chart hover information).
        """
        fig = px.bar(
            contribution_df.sum(),
            title=title,
            labels={"index": "Assets", "value": ylabel},
            text=contribution_df.sum()
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(showlegend=False, xaxis_title="Assets", yaxis_title=ylabel)
        fig.show()

    def process(self, visualize=True):
        """
        Run all contribution calculations and return results.

        Parameters:
        - visualize (bool): Whether to visualize the results.

        Returns:
        - dict: Results of all contribution calculations.
        """
        results = {}

        # 1. Return Contribution
        return_contribution, portfolio_return = self.calculate_return_contribution()
        results['Return Contribution'] = return_contribution
        results['Portfolio Return'] = portfolio_return
        if visualize:
            self.visualize_contributions(return_contribution, "Asset Contribution to Portfolio Return", "Return Contribution")

        # 2. Risk Contribution
        risk_contribution, portfolio_volatility = self.calculate_risk_contribution()
        results['Risk Contribution'] = risk_contribution
        results['Portfolio Volatility'] = portfolio_volatility
        if visualize:
            self.visualize_contributions(
                pd.DataFrame(risk_contribution, index=self.weights.index, columns=["Risk Contribution"]),
                "Asset Contribution to Portfolio Risk", "Risk Contribution"
            )

        # 3. Factor Contribution
        if self.factor_exposures is not None:
            factor_contribution = self.calculate_factor_contribution()
            results['Factor Contribution'] = factor_contribution
            if visualize:
                self.visualize_contributions(
                    pd.DataFrame(factor_contribution, index=self.weights.index, columns=self.factor_exposures.columns),
                    "Asset Contribution to Factors", "Factor Contribution"
                )

        # 4. Tracking Error Contribution
        if self.benchmark_returns is not None:
            tracking_error_contribution, tracking_error = self.calculate_tracking_error_contribution()
            results['Tracking Error Contribution'] = tracking_error_contribution
            results['Tracking Error'] = tracking_error
            if visualize:
                self.visualize_contributions(
                    pd.DataFrame(tracking_error_contribution, index=self.weights.index, columns=["Tracking Error Contribution"]),
                    "Asset Contribution to Tracking Error", "Tracking Error Contribution"
                )
        
        return results
