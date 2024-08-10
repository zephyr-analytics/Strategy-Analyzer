import customtkinter as ctk
import utilities as utilities
import main

class MonteCarloApp(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.
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
        self.trading_frequency = ctk.StringVar(value="Monthly")
        self.weighting_strategy = ctk.StringVar(value="Use File Weights")
        self.cash_ticker = ctk.StringVar(value="SGOV")
        self.bond_ticker = ctk.StringVar(value="BND")
        self.theme_mode = ctk.StringVar(value="Light")
        self.bottom_text = None
        self.weights_filename = ""
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)

        bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")

        ctk.CTkLabel(sidebar, text="Strategy Settings", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 5))
        
        ctk.CTkLabel(sidebar, text="Start Date:", font = bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.start_date).pack(pady=(0, 5))
        
        ctk.CTkLabel(sidebar, text="End Date:", font = bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.end_date).pack(pady=(0, 10))

        ctk.CTkLabel(sidebar, text="Cash Ticker:", font = bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.cash_ticker).pack(pady=(0, 5))
        
        ctk.CTkLabel(sidebar, text="Bond Ticker:", font = bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.bond_ticker).pack(pady=(0, 10))
        
        ctk.CTkLabel(sidebar, text="Trading Frequency:", font = bold_font).pack(pady=(0, 0))
        trading_options = ["Monthly", "Bi-Monthly"]
        ctk.CTkOptionMenu(sidebar, values=trading_options, variable=self.trading_frequency).pack(pady=(0, 10))
        
        ctk.CTkLabel(sidebar, text="Weighting Strategy:", font = bold_font).pack(pady=(0, 0))
        weighting_options = ["Use File Weights", "Equal Weight", "Risk Contribution", "Min Volatility", "Max Sharpe"]
        ctk.CTkOptionMenu(sidebar, values=weighting_options, variable=self.weighting_strategy).pack(pady=(0, 10))

        ctk.CTkLabel(sidebar, text="SMA Window (days):", font = bold_font).pack(pady=(0, 0))
        sma_windows = ["21", "42", "63", "84", "105", "126", "147", "168", "210"]
        self.sma_window = ctk.StringVar(value="21")
        ctk.CTkOptionMenu(sidebar, values=sma_windows, variable=self.sma_window).pack(pady=(0, 10))

        ctk.CTkButton(sidebar, text="Select Asset Weights File", command=self.load_weights_and_update).pack(pady=(10, 10))

        self.bottom_text_frame = ctk.CTkFrame(self)
        self.bottom_text_frame.grid(row=1, column=1, columnspan=1, sticky="ew")

        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, rowspan=1, sticky="nsew")

        tab_control = ctk.CTkTabview(center_frame)
        tab_control.pack(expand=1, fill="both")

        self.create_backtesting_tab(tab_control)
        self.create_monte_carlo_tab(tab_control)
        self.create_signals_tab(tab_control)

        # New frame for the copyright text
        self.copyright_frame = ctk.CTkFrame(self)
        self.copyright_frame.grid(row=2, column=1, columnspan=1, sticky="ew")
        ctk.CTkLabel(self.copyright_frame, text="© Dash Global Analytics added 2024", font=ctk.CTkFont(size=10)).pack(pady=5)

        right_sidebar = ctk.CTkFrame(self, width=200)
        right_sidebar.grid(row=0, column=2, rowspan=2, sticky="ns")

        # Adding theme selection menu to right sidebar
        ctk.CTkLabel(right_sidebar, text="Theme Mode:", font=bold_font).pack(pady=(20, 0))
        theme_options = ["Light", "Dark"]
        ctk.CTkOptionMenu(right_sidebar, values=theme_options, variable=self.theme_mode, command=self.change_theme).pack(pady=(5, 20))

    def change_theme(self, selected_theme):
        """
        Changes the theme of the application based on user selection.
        """
        ctk.set_appearance_mode(selected_theme)

    def create_backtesting_tab(self, tab_control):
        """
        Creates the backtesting tab with input fields and buttons for running a backtest.
        """
        backtesting_tab = tab_control.add("Backtesting")
        ctk.CTkLabel(backtesting_tab, text="Backtesting", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkButton(backtesting_tab, text="Run Backtest", command=self.run_backtest).pack(pady=10)
        ctk.CTkButton(backtesting_tab, text="Run All Scenarios", command=self.run_all_weighting_scenarios).pack(pady=10)

    def create_monte_carlo_tab(self, tab_control):
        """
        Creates the Monte Carlo simulation tab with input fields and buttons for running a simulation.
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
        """
        signals_tab = tab_control.add("Generate Signals")
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
            self.weights_filename,
            self.bond_ticker.get(), 
            self.cash_ticker.get()  
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
            self.simulation_horizon.get(),
            self.bond_ticker.get(),  
            self.cash_ticker.get() 
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
            self.weights_filename,
            self.bond_ticker.get(), 
            self.cash_ticker.get() 
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
            current_date,
            self.bond_ticker.get(), 
            self.cash_ticker.get() 
        )
        self.bottom_text = ctk.CTkLabel(self.bottom_text_frame, text=result, text_color="green" if "generated" in result else "red")
        self.bottom_text.pack(pady=5)

if __name__ == "__main__":
    app = MonteCarloApp()
    app.mainloop()
