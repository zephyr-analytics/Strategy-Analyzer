import customtkinter as ctk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from models.backtesting import BacktestStaticPortfolio
from models.monte_carlo_sim import MonteCarloSimulation
import utilities as utilities
from tkinter import filedialog

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
    trading_frequency : ctk.StringVar
        Trading frequency for the backtest (monthly or bi-monthly).
    """

    def __init__(self):
        """
        Initializes the MonteCarloApp with default settings and creates the GUI widgets.
        """
        super().__init__()
        self.title("Backtesting and Monte Carlo Simulation")
        self.geometry("600x500")
        self.assets_weights = {}
        self.start_date = ctk.StringVar(value="2012-01-01")
        self.end_date = ctk.StringVar(value="2024-08-01")
        self.initial_portfolio_value = ctk.DoubleVar(value=10000)
        self.num_simulations = ctk.IntVar(value=1000)
        self.simulation_horizon = ctk.IntVar(value=10)
        self.trading_frequency = ctk.StringVar(value="Monthly")  # Default value
        self.bottom_text = None
        self.weights_filename = ""
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
        
        ctk.CTkLabel(backtesting_tab, text="Trading Frequency").pack()
        trading_options = ["monthly", "bi-monthly"]
        ctk.CTkOptionMenu(backtesting_tab, values=trading_options, variable=self.trading_frequency).pack(pady=5)

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

    def clear_bottom_text(self):
        """
        Clears the text at the bottom of the GUI.
        """
        if self.bottom_text is not None:
            self.bottom_text.pack_forget()
            self.bottom_text = None

    def load_weights_and_update(self):
        """
        Loads the asset weights from a file and updates the assets_weights attribute.
        """
        self.clear_bottom_text()
        self.assets_weights, self.weights_filename = utilities.load_weights()
        if self.assets_weights:
            self.weights_filename = utilities.strip_csv_extension(self.weights_filename)
            self.display_asset_weights()

    def display_asset_weights(self):
        """
        Displays the loaded asset weights in the GUI.
        """
        assets_text = "\n".join([f"{asset}: {weight}" for asset, weight in self.assets_weights.items()])
        self.bottom_text = ctk.CTkLabel(self, text=f"Loaded Assets and Weights from {self.weights_filename}:\n{assets_text}", text_color="blue")
        self.bottom_text.pack(pady=5)

    def run_backtest(self):
        """
        Runs the backtest with the current settings and displays the results.
        """
        self.clear_bottom_text()
        if not self.assets_weights:
            self.bottom_text = ctk.CTkLabel(self, text="Please load asset weights file.", text_color="red")
            self.bottom_text.pack(pady=5)
            return
        
        backtest = BacktestStaticPortfolio(self.assets_weights, self.start_date.get(), self.end_date.get(), self.trading_frequency.get(), output_filename=self.weights_filename)
        backtest.process()
        self.bottom_text = ctk.CTkLabel(self, text="Backtest completed and plots saved.", text_color="green")
        self.bottom_text.pack(pady=5)

    def run_simulation(self):
        """
        Runs the Monte Carlo simulation with the current settings and displays the results.
        """
        self.clear_bottom_text()
        if not self.assets_weights:
            self.bottom_text = ctk.CTkLabel(self, text="Please load asset weights file.", text_color="red")
            self.bottom_text.pack(pady=5)
            return
        backtest = BacktestStaticPortfolio(self.assets_weights, self.start_date.get(), self.end_date.get(), self.trading_frequency.get(), output_filename=self.weights_filename)
        backtest.process()
        initial_value, cagr, annual_volatility = utilities.calculate_portfolio_metrics(backtest)
        monte_carlo = MonteCarloSimulation(initial_value, cagr, annual_volatility, output_filename=self.weights_filename, num_simulations=self.num_simulations.get(), simulation_horizon=self.simulation_horizon.get())
        monte_carlo.process()
        self.bottom_text = ctk.CTkLabel(self, text="Simulation completed and plot saved.", text_color="green")
        self.bottom_text.pack(pady=5)

if __name__ == "__main__":
    app = MonteCarloApp()
    app.mainloop()
