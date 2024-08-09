import customtkinter as ctk
import utilities as utilities
import main

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
        super().__init__()
        self.title("Backtesting and Monte Carlo Simulation")
        self.geometry("1200x600")
        self.assets_weights = {}
        self.start_date = ctk.StringVar(value="2012-01-01")
        self.end_date = ctk.StringVar(value="2024-08-01")
        self.initial_portfolio_value = ctk.DoubleVar(value=10000)
        self.num_simulations = ctk.IntVar(value=1000)
        self.simulation_horizon = ctk.IntVar(value=10)
        self.trading_frequency = ctk.StringVar(value="monthly")
        self.weighting_strategy = ctk.StringVar(value="equal")
        self.bottom_text = None
        self.weights_filename = ""
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)

        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")

        ctk.CTkLabel(sidebar, text="Settings", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(sidebar, text="Start Date").pack(pady=5)
        ctk.CTkEntry(sidebar, textvariable=self.start_date).pack(pady=5)
        
        ctk.CTkLabel(sidebar, text="End Date").pack(pady=5)
        ctk.CTkEntry(sidebar, textvariable=self.end_date).pack(pady=5)
        
        ctk.CTkLabel(sidebar, text="Trading Frequency").pack(pady=5)
        trading_options = ["monthly", "bi-monthly"]
        ctk.CTkOptionMenu(sidebar, values=trading_options, variable=self.trading_frequency).pack(pady=5)
        
        ctk.CTkLabel(sidebar, text="Weighting Strategy").pack(pady=5)
        weighting_options = ["use_file_weights", "equal", "risk_contribution", "min_volatility", "max_sharpe"]
        ctk.CTkOptionMenu(sidebar, values=weighting_options, variable=self.weighting_strategy).pack(pady=5)

        # Add SMA window selection
        ctk.CTkLabel(sidebar, text="SMA Window (days)").pack(pady=5)
        sma_windows = ["21", "42", "63", "84", "105", "126", "147", "168", "210"]
        self.sma_window = ctk.StringVar(value="21")
        ctk.CTkOptionMenu(sidebar, values=sma_windows, variable=self.sma_window).pack(pady=5)

        ctk.CTkButton(sidebar, text="Select Asset Weights File", command=self.load_weights_and_update).pack(pady=10)

        self.bottom_text_frame = ctk.CTkFrame(self)
        self.bottom_text_frame.grid(row=1, column=1, columnspan=1, sticky="ew")

        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, rowspan=1, sticky="nsew")

        tab_control = ctk.CTkTabview(center_frame)
        tab_control.pack(expand=1, fill="both")

        self.create_backtesting_tab(tab_control)
        self.create_monte_carlo_tab(tab_control)
        self.create_signals_tab(tab_control)

        right_sidebar = ctk.CTkFrame(self, width=200)
        right_sidebar.grid(row=0, column=2, rowspan=2, sticky="ns")

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
        ctk.CTkButton(backtesting_tab, text="Run Backtest", command=self.run_backtest).pack(pady=10)
        ctk.CTkButton(backtesting_tab, text="Run All Scenarios", command=self.run_all_weighting_scenarios).pack(pady=10)

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

    def create_signals_tab(self, tab_control):
        """
        Creates the signals tab with input fields and buttons for generating signals.

        Parameters
        ----------
        tab_control : ctk.CTkTabview
            The tab control object to which the signals tab will be added.
        """
        signals_tab = tab_control.add("Signals")
        ctk.CTkLabel(signals_tab, text="Generate Portfolio Signals", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(signals_tab, text="Date for Signals").pack(pady=5)
        signal_date = ctk.StringVar(value="2024-08-01")
        ctk.CTkEntry(signals_tab, textvariable=signal_date).pack(pady=5)
        
        ctk.CTkButton(signals_tab, text="Generate Signals", command=lambda: self.run_signals_and_display(signal_date.get())).pack(pady=10)

    def clear_bottom_text(self):
        """
        Clears the text at the bottom of the GUI.
        """
        for widget in self.bottom_text_frame.winfo_children():
            widget.destroy()

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
        self.bottom_text = ctk.CTkLabel(self.bottom_text_frame, text=f"Loaded Assets and Weights from {self.weights_filename}:\n{assets_text}", text_color="blue")
        self.bottom_text.pack(pady=5)

    def run_backtest(self):
        self.clear_bottom_text()
        result = main.run_backtest(
            self.assets_weights, 
            self.start_date.get(), 
            self.end_date.get(), 
            self.trading_frequency.get(), 
            self.weighting_strategy.get(), 
            self.sma_window.get(), 
            self.weights_filename
        )
        self.bottom_text = ctk.CTkLabel(self.bottom_text_frame, text=result, text_color="green" if "completed" in result else "red")
        self.bottom_text.pack(pady=5)

    def run_simulation(self):
        self.clear_bottom_text()
        result = main.run_simulation(
            self.assets_weights, 
            self.start_date.get(), 
            self.end_date.get(), 
            self.trading_frequency.get(), 
            self.weighting_strategy.get(), 
            self.sma_window.get(), 
            self.weights_filename,
            self.num_simulations.get(), 
            self.simulation_horizon.get()
        )
        self.bottom_text = ctk.CTkLabel(self.bottom_text_frame, text=result, text_color="green" if "completed" in result else "red")
        self.bottom_text.pack(pady=5)

    def run_all_weighting_scenarios(self):
        self.clear_bottom_text()
        result = main.run_all_weighting_scenarios(
            self.assets_weights, 
            self.start_date.get(), 
            self.end_date.get(), 
            self.trading_frequency.get(), 
            self.sma_window.get(), 
            self.weights_filename
        )
        self.bottom_text = ctk.CTkLabel(self.bottom_text_frame, text=result, text_color="green" if "completed" in result else "red")
        self.bottom_text.pack(pady=5)

    def run_signals_and_display(self, current_date):
        self.clear_bottom_text()
        result = main.run_signals(
            self.assets_weights, 
            self.start_date.get(), 
            self.end_date.get(), 
            self.trading_frequency.get(), 
            self.weighting_strategy.get(), 
            self.sma_window.get(), 
            self.weights_filename,
            current_date
        )
        self.bottom_text = ctk.CTkLabel(self.bottom_text_frame, text=result, text_color="green" if "generated" in result else "red")
        self.bottom_text.pack(pady=5)

if __name__ == "__main__":
    app = MonteCarloApp()
    app.mainloop()

