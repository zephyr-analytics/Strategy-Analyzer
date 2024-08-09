import numpy as np
import pandas as pd

import utilities as utilities
from results.results_processor import ResultsProcessor

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

    def __init__(self, initial_portfolio_value, average_annual_return, annual_volatility, output_filename, num_simulations=1000, simulation_horizon=10):
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
        self.output_filename = output_filename

    def process(self):
        """
        Encapsulates the entire process of running the Monte Carlo simulation and plotting the results.
        """
        simulation_results = self.run_simulation()
        results_processor = ResultsProcessor(self.output_filename)
        results_processor.plot_monte_carlo_simulation(simulation_results, self.simulation_horizon, self.output_filename)

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
