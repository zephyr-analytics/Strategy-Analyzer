import numpy as np
import pandas as pd
import plotly.graph_objects as go

import utilities as utilities

class MonteCarloSimulation:
    """
    A class to perform Monte Carlo simulation on the portfolio statistics.

    Attributes
    ----------
    initial_portfolio_value : float
        Initial value of the portfolio.
    average_annual_return : float
        Average annual return of the portfolio.
    annual_volatility : float
        Annual volatility (standard deviation) of the portfolio returns.
    num_simulations : int
        Number of Monte Carlo simulation runs.
    simulation_horizon : int
        Number of years to simulate.
    """

    def __init__(self, initial_portfolio_value, average_annual_return, annual_volatility, num_simulations=1000, simulation_horizon=10):
        """
        Initializes the MonteCarloSimulation with portfolio statistics and simulation parameters.

        Parameters
        ----------
        initial_portfolio_value : float
            Initial value of the portfolio.
        average_annual_return : float
            Average annual return of the portfolio.
        annual_volatility : float
            Annual volatility (standard deviation) of the portfolio returns.
        num_simulations : int, optional
            Number of Monte Carlo simulation runs (default is 1000).
        simulation_horizon : int, optional
            Number of years to simulate (default is 10).
        """
        self.initial_portfolio_value = initial_portfolio_value
        self.average_annual_return = average_annual_return
        self.annual_volatility = annual_volatility
        self.num_simulations = num_simulations
        self.simulation_horizon = simulation_horizon

    def run_simulation(self):
        """
        Runs the Monte Carlo simulation.

        Returns
        -------
        DataFrame
            DataFrame containing the simulated portfolio values.
        """
        simulation_results = np.zeros((self.simulation_horizon + 1, self.num_simulations))
        simulation_results[0] = self.initial_portfolio_value

        for t in range(1, self.simulation_horizon + 1):
            random_returns = np.random.normal(self.average_annual_return, self.annual_volatility, self.num_simulations)
            simulation_results[t] = simulation_results[t - 1] * (1 + random_returns)

        return pd.DataFrame(simulation_results)

    def plot_simulation(self, simulation_results, filename='monte_carlo_simulation.html'):
        """
        Plots the results of the Monte Carlo simulation.

        Parameters
        ----------
        simulation_results : DataFrame
            DataFrame containing the simulated portfolio values.
        """
        average_simulation = simulation_results.mean(axis=1)
        lower_bound = np.percentile(simulation_results, 2.5, axis=1)
        upper_bound = np.percentile(simulation_results, 97.5, axis=1)

        average_cagr = utilities.calculate_cagr_monte_carlo(pd.Series(average_simulation))
        lower_cagr = utilities.calculate_cagr_monte_carlo(pd.Series(lower_bound))
        upper_cagr = utilities.calculate_cagr_monte_carlo(pd.Series(upper_bound))

        average_end_value = pd.Series(average_simulation).iloc[-1]
        lower_end_value = pd.Series(lower_bound).iloc[-1]
        upper_end_value = pd.Series(upper_bound).iloc[-1]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(self.simulation_horizon + 1)), 
            y=average_simulation, 
            mode='lines', 
            name=f'Average Simulation (CAGR: {average_cagr:.2%}, End Value: ${average_end_value:,.2f})', 
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=list(range(self.simulation_horizon + 1)), 
            y=lower_bound, 
            mode='lines', 
            name=f'Lower Bound (2.5%) (CAGR: {lower_cagr:.2%}, End Value: ${lower_end_value:,.2f})', 
            line=dict(color='red', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=list(range(self.simulation_horizon + 1)), 
            y=upper_bound, 
            mode='lines', 
            name=f'Upper Bound (97.5%) (CAGR: {upper_cagr:.2%}, End Value: ${upper_end_value:,.2f})', 
            line=dict(color='green', dash='dash')
        ))
        fig.update_layout(
            title='Monte Carlo Simulation of Portfolio Value',
            xaxis_title='Year',
            yaxis_title='Portfolio Value ($)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        utilities.save_html(fig, filename)
