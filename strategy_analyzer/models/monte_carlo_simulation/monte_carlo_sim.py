"""
Processor for running MonteCarlo simulations.
"""

import numpy as np
import pandas as pd

from strategy_analyzer.results.simulation_results_processor import SimulationResultsProcessor
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.results.models_results import ModelsResults


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

    def __init__(self, models_data: ModelsData, models_results: ModelsResults):
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
        self.data_models = models_data
        self.results_models = models_results


    def process(self):
        """
        Encapsulates the entire process of running the Monte Carlo simulation and plotting the results.
        """
        self.run_simulation()
        results_processor = SimulationResultsProcessor(models_data=self.data_models, models_results=self.results_models)
        results_processor.process()


    def run_simulation(self):
        """
        Runs the Monte Carlo simulation with optional contributions, accommodating annual simulation periods.

        Parameters
        ----------
        contribution : float
            Amount to be added to the portfolio at each contribution interval.
        contribution_frequency : str
            Frequency of contributions ("monthly", "quarterly", "yearly").

        Returns
        -------
        DataFrame
            DataFrame containing the simulated portfolio values.
        """
        simulation_results = np.zeros((self.data_models.simulation_horizon + 1, self.data_models.num_simulations))
        simulation_results[0] = self.data_models.initial_portfolio_value

        if self.data_models.contribution and self.data_models.contribution_frequency:
            if self.data_models.contribution_frequency == "Monthly":
                contribution = self.data_models.contribution*12
            elif self.data_models.contribution_frequency == "Quarterly":
                contribution = self.data_models.contribution*4
            elif self.data_models.contribution_frequency == "Yearly":
                contribution = self.data_models.contribution
            else:
                raise ValueError("Invalid contribution frequency. Choose from 'monthly', 'quarterly', 'yearly'.")
        else:
            contribution = 0

        for t in range(1, self.data_models.simulation_horizon + 1):
            random_returns = np.random.normal(
                self.results_models.average_annual_return, self.results_models.annual_volatility, self.data_models.num_simulations
            )
            simulation_results[t] = simulation_results[t - 1] * (1 + random_returns)

            simulation_results[t] += contribution
        print(simulation_results)
        self.results_models.simulation_results = simulation_results
