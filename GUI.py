import customtkinter as ctk
import numpy as np

from backtesting import BacktestStaticPortfolio
from monte_carlo_sim import MonteCarloSimulation

import utilities as utilities

class MonteCarloApp(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.

    Attributes
    ----------
    assets_weights : dict
        Dictionary containing asset weights for the portfolio.
    start_date : ctk.StringVar
        Start date for the backtest and simulations.
    end_date : ctk.StringVar
        End date for the backtest and simulations.
    initial_portfolio_value : ctk.DoubleVar
        Initial value of the portfolio for simulations.
    num_simulations : ctk.IntVar
        Number of Monte Carlo simulations to run.
    simulation_horizon : ctk.IntVar
        Number of years to simulate in the Monte Carlo simulation.
    """

    def __init__(self):
        """
        Initializes the MonteCarloApp with default settings and creates the GUI widgets.
        """
        super().__init__()

        self.title("Backtesting and Monte Carlo Simulation")
        self.geometry("600x500")

        self.assets_weights = {}
        self.start_date = ctk.StringVar(value="2010-01-01")
        self.end_date = ctk.StringVar(value="2024-08-01")
        self.initial_portfolio_value = ctk.DoubleVar(value=10000)
        self.num_simulations = ctk.IntVar(value=1000)
        self.simulation_horizon = ctk.IntVar(value=10)

        self.create_widgets()

    def create_widgets(self):
        """
        Creates the tabbed layout for the GUI with separate tabs for backtesting and Monte Carlo simulation.
        """
        tab_control = ctk.CTkTabview(self)
        tab_control.pack(expand=1, fill="both")

        self.create_backtesting_tab(tab_control)
        self.create_monte_carlo_tab(tab_control)

    def create_backtesting_tab(self, tab_control):
        """
        Creates the backtesting tab with input fields and buttons for running a backtest.

        Parameters
        ----------
        tab_control : ctk.CTkTabview
            The tab control object to which the backtesting tab will be added.
        """
        backtesting_tab = tab_control.add("Backtesting")

        ctk.CTkLabel(backtesting_tab, text="Backtesting", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        ctk.CTkLabel(backtesting_tab, text="Start Date").pack()
        ctk.CTkEntry(backtesting_tab, textvariable=self.start_date).pack(pady=5)

        ctk.CTkLabel(backtesting_tab, text="End Date").pack()
        ctk.CTkEntry(backtesting_tab, textvariable=self.end_date).pack(pady=5)

        ctk.CTkButton(backtesting_tab, text="Select Asset Weights File", command=self.load_weights_and_update).pack(pady=10)
        ctk.CTkButton(backtesting_tab, text="Run Backtest", command=self.run_backtest).pack(pady=10)

    def create_monte_carlo_tab(self, tab_control):
        """
        Creates the Monte Carlo simulation tab with input fields and buttons for running a simulation.

        Parameters
        ----------
        tab_control : ctk.CTkTabview
            The tab control object to which the Monte Carlo simulation tab will be added.
        """
        monte_carlo_tab = tab_control.add("Monte Carlo Simulation")

        ctk.CTkLabel(monte_carlo_tab, text="Monte Carlo Simulation", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        ctk.CTkLabel(monte_carlo_tab, text="Number of Simulations").pack()
        ctk.CTkEntry(monte_carlo_tab, textvariable=self.num_simulations).pack(pady=5)

        ctk.CTkLabel(monte_carlo_tab, text="Simulation Horizon (years)").pack()
        ctk.CTkEntry(monte_carlo_tab, textvariable=self.simulation_horizon).pack(pady=5)

        ctk.CTkButton(monte_carlo_tab, text="Run Simulation", command=self.run_simulation).pack(pady=10)

    def load_weights_and_update(self):
        """
        Loads the asset weights from a file and updates the assets_weights attribute.
        """
        self.assets_weights = utilities.load_weights()

    def run_backtest(self):
        """
        Runs the backtest with the current settings and displays the results.
        """
        if not self.assets_weights:
            ctk.CTkLabel(self, text="Please load asset weights file.", text_color="red").pack(pady=5)
            return

        backtest = BacktestStaticPortfolio(self.assets_weights, self.start_date.get(), self.end_date.get())
        backtest.process()

        backtest.plot_portfolio_value()
        backtest.plot_var_cvar()

        ctk.CTkLabel(self, text="Backtest completed and plots saved.", text_color="green").pack(pady=5)

    def run_simulation(self):
        """
        Runs the Monte Carlo simulation with the current settings and displays the results.
        """
        if not self.assets_weights:
            ctk.CTkLabel(self, text="Please load asset weights file.", text_color="red").pack(pady=5)
            return

        backtest = BacktestStaticPortfolio(self.assets_weights, self.start_date.get(), self.end_date.get())
        backtest.process()

        initial_value = backtest.get_portfolio_value().iloc[0]
        cagr = utilities.calculate_cagr(backtest.get_portfolio_value())
        annual_volatility = backtest._returns.std() * np.sqrt(12)

        monte_carlo = MonteCarloSimulation(initial_value, cagr, annual_volatility, self.num_simulations.get(), self.simulation_horizon.get())
        simulation_results = monte_carlo.run_simulation()

        monte_carlo.plot_simulation(simulation_results)
        ctk.CTkLabel(self, text="Simulation completed and plot saved.", text_color="green").pack(pady=5)

if __name__ == "__main__":
    app = MonteCarloApp()
    app.mainloop()
