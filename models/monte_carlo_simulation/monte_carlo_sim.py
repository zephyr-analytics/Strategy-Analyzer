"""
Processor for running MonteCarlo simulations.
"""

import numpy as np
import pandas as pd

import utilities as utilities
from results.results_processor import ResultsProcessor
from models.models_data import ModelsData

class MonteCarloSimulation:
    """
    A class to perform Monte Carlo simulation on the portfolio statistics.

    Attributes
    ----------
    data_models : object
        An instance of the DataModels class that holds all necessary attributes.
    num_simulations : int
        Number of Monte Carlo simulation runs.
    simulation_horizon : int
        Number of years to simulate.
    """

    def __init__(self, data_models: ModelsData):
        """
        Initializes the MonteCarloSimulation with portfolio statistics and simulation parameters.

        Parameters
        ----------
        data_models : object
            An instance of the DataModels class that holds all necessary attributes.
        data : pandas.DataFrame
            Data containing historical prices of the assets.
        num_simulations : int, optional
            Number of Monte Carlo simulation runs (default is 1000).
        simulation_horizon : int, optional
            Number of years to simulate (default is 10).
        """
        self.data_models = data_models
        self.num_simulations = data_models.num_simulations
        self.simulation_horizon = data_models.simulation_horizon
        self.output_filename = data_models.weights_filename
        self.annual_volatility = data_models.annual_volatility
        self.average_annual_return = data_models.average_annual_return
        self.portfolio_returns = data_models.portfolio_returns
        self.initial_portfolio_value = data_models.initial_portfolio_value


    def process(self):
        """
        Encapsulates the entire process of running the Monte Carlo simulation and plotting the results.
        """
        simulation_results = self.run_simulation()
        results_processor = ResultsProcessor(self.data_models)
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
            # TODO this now needs to take into account adding more month each month.
            # TODO this needs to take into account taxes based on a yearly basis.
            random_returns = np.random.normal(self.average_annual_return, self.annual_volatility, self.num_simulations)
            simulation_results[t] = simulation_results[t - 1] * (1 + random_returns)

        return pd.DataFrame(simulation_results)
