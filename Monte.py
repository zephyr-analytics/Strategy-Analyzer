import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Utilities_Backtest import calculate_cagr_monte_carlo, calculate_cagr

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

    def plot_simulation(self, simulation_results):
        """
        Plots the results of the Monte Carlo simulation.

        Parameters
        ----------
        simulation_results : DataFrame
            DataFrame containing the simulated portfolio values.
        """
        # Calculate the statistics for plotting
        average_simulation = simulation_results.mean(axis=1)
        lower_bound = np.percentile(simulation_results, 5, axis=1)
        upper_bound = np.percentile(simulation_results, 95, axis=1)

        # Calculate CAGR for each line
        average_cagr = calculate_cagr_monte_carlo(pd.Series(average_simulation))
        lower_cagr = calculate_cagr_monte_carlo(pd.Series(lower_bound))
        upper_cagr = calculate_cagr_monte_carlo(pd.Series(upper_bound))

        # Get ending values
        average_end_value = average_simulation.iloc[-1]
        lower_end_value = lower_bound[-1]
        upper_end_value = upper_bound[-1]

        # Plot the simulation results
        plt.figure(figsize=(10, 6))
        plt.plot(upper_bound, label=f'Upper Bound (95%) (CAGR: {upper_cagr:.2%}, End Value: ${upper_end_value:,.2f})', color='green', linestyle='--')
        plt.plot(average_simulation, label=f'Average Simulation (CAGR: {average_cagr:.2%}, End Value: ${average_end_value:,.2f})', color='blue', linestyle='-')
        plt.plot(lower_bound, label=f'Lower Bound (5%) (CAGR: {lower_cagr:.2%}, End Value: ${lower_end_value:,.2f})', color='red', linestyle='--')
        plt.fill_between(range(self.simulation_horizon + 1), lower_bound, upper_bound, color='gray', alpha=0.2)

        plt.title('Monte Carlo Simulation of Portfolio Value')
        plt.xlabel('Year')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        plt.savefig('monte_carlo_simulation.png')  # Save the plot as an image file
        plt.close()  # Close the plot to free memory

# Example usage
if __name__ == "__main__":
    from Backtesting import BacktestStaticPortfolio  # Assuming the backtest class is saved in a file named backtest.py

    # Define the assets and time period
    # assets_weights = {'VTI': 0.3, 'IEI': 0.15, 'TLT': 0.4, 'GLD': 0.075, 'DBC': 0.075}
    assets_weights = {'VINIX': 0.75, 'VSCIX': 0.25}
    start_date = '2010-01-01'
    end_date = '2024-08-01'

    # Run the backtest
    backtest = BacktestStaticPortfolio(assets_weights, start_date, end_date)
    backtest.process()

    # Extract the statistics
    initial_value = backtest.get_portfolio_value().iloc[0]
    cagr = calculate_cagr(backtest.get_portfolio_value())
    annual_volatility = backtest._returns.std() * np.sqrt(12)

    # Run Monte Carlo simulation
    monte_carlo = MonteCarloSimulation(initial_value, cagr, annual_volatility)
    simulation_results = monte_carlo.run_simulation()

    # Plot the simulation results
    monte_carlo.plot_simulation(simulation_results)
