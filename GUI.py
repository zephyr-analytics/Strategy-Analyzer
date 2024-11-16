"""
GUI user interface for running application.
"""

import threading

from datetime import datetime

import customtkinter as ctk
from PIL import Image

import main
import utilities as utilities
from models_data import ModelsData


class PortfolioAnalyzer(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.
    """

    def __init__(self):
        """
        Initializes the PortfolioStrategyAnalyzer.

        Parameters
        ----------
        None
        """
        super().__init__()
        self.title("Portfolio Analyzer")
        self.geometry("1200x700")

        # Initialize ModelsData object
        self.data_models = ModelsData()

        # # Set custom icon
        # icon_path = "C:/Users/monic/OneDrive/Documents/Files for Zephyr Analytics/Zephyr Analytics FF/company_icon.ico"
        # self.iconbitmap(icon_path)

        # Variables for binding to GUI
        self.start_date_var = ctk.StringVar(value=self.data_models.start_date)
        self.end_date_var = ctk.StringVar(value=self.data_models.end_date)
        self.cash_ticker_var = ctk.StringVar(value=self.data_models.cash_ticker)
        self.bond_ticker_var = ctk.StringVar(value=self.data_models.bond_ticker)
        self.trading_frequency_var = ctk.StringVar(value=self.data_models.trading_frequency)
        self.weighting_strategy_var = ctk.StringVar(value=self.data_models.weighting_strategy)
        self.sma_window_var = ctk.StringVar(value=self.data_models.sma_window)
        self.num_simulations_var = ctk.StringVar(value=self.data_models.num_simulations)
        self.simulation_horizon_var = ctk.StringVar(value=self.data_models.simulation_horizon)
        self.theme_mode_var = ctk.StringVar(value=self.data_models.theme_mode)
        self.initial_portfolio_value_var = ctk.StringVar(
            value=self.data_models._initial_portfolio_value
        )
        self.threshold_asset_entry_var = ctk.StringVar(value=self.data_models._threshold_asset)
        self.num_assets_to_select_entry_var = ctk.StringVar(
            value=self.data_models._num_assets_to_select
        )

        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        self.bottom_text = None
        self.create_widgets()

    def create_widgets(self):
        """
        Creates the widgets and layouts for the application.

        Parameters
        ----------
        None
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)

        # Create sidebars
        self.create_sidebars()

        self.bottom_text_frame = ctk.CTkFrame(self, fg_color="#edeaea")
        self.bottom_text_frame.grid(row=1, column=1, columnspan=1, sticky="ew")

        center_frame = ctk.CTkFrame(self, fg_color="#edeaea")
        center_frame.grid(row=0, column=1, rowspan=1, sticky="nsew")

        self.high_level_tab_control = ctk.CTkTabview(
            center_frame, fg_color="#edeaea",
            segmented_button_fg_color="#edeaea",
            segmented_button_unselected_color="#bb8fce",
            segmented_button_selected_color="#8e44ad",
            text_color="#000000",
            segmented_button_selected_hover_color="#8e44ad"
        )
        self.high_level_tab_control.pack(expand=1, fill="both")

        sma_testing_tab = self.high_level_tab_control.add("SMA Strategies")
        self.create_tab_content(sma_testing_tab)

        momentum_testing_tab = self.high_level_tab_control.add("Momentum Strategies")
        self.create_tab_content(momentum_testing_tab)

        in_and_out_momentum_testing_tab = self.high_level_tab_control.add(
            "Momentum In & Out Strategies"
        )
        self.create_tab_content(in_and_out_momentum_testing_tab)

        # machine_learning_testing_tab = self.high_level_tab_control.add(
        #     "Machine Learning Strategies"
        # )
        # self.create_tab_content(machine_learning_testing_tab)

        self.high_level_tab_control.set("SMA Strategies")

        # Add copyright information
        copyright_frame = ctk.CTkFrame(self, fg_color="#edeaea")
        copyright_frame.grid(row=4, column=1, columnspan=1, sticky="ew", pady=(5, 5))

        copyright_label = ctk.CTkLabel(
            copyright_frame,
            text="© Zephyr Analytics 2024",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack(pady=(0, 0))

    def create_sidebars(self):
        """
        Creates shared sidebars that apply to all tabs.
        """
        # Left sidebar
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, rowspan=4, sticky="ns", pady=(20, 0))

        ctk.CTkLabel(
            sidebar,
            text="Strategy Settings",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )).pack(pady=(10, 5))

        ctk.CTkLabel(
            sidebar,
            text="Initial Portfolio Value:",
            font=self.bold_font).pack(pady=(0, 0)
        )

        ctk.CTkEntry(
            sidebar,
            textvariable=self.initial_portfolio_value_var).pack(pady=(0, 5)
        )
        self.initial_portfolio_value_var.trace_add("write", self.update_initial_portfolio_value)

        ctk.CTkLabel(sidebar, text="Start Date:", font=self.bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.start_date_var).pack(pady=(0, 5))
        self.start_date_var.trace_add("write", self.update_start_date)

        ctk.CTkLabel(sidebar, text="End Date:", font=self.bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.end_date_var).pack(pady=(0, 10))
        self.end_date_var.trace_add("write", self.update_end_date)

        ctk.CTkLabel(sidebar, text="Cash Ticker:", font=self.bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.cash_ticker_var).pack(pady=(0, 5))
        self.cash_ticker_var.trace_add("write", self.update_cash_ticker)

        ctk.CTkLabel(sidebar, text="Bond Ticker:", font=self.bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(sidebar, textvariable=self.bond_ticker_var).pack(pady=(0, 10))
        self.bond_ticker_var.trace_add("write", self.update_bond_ticker)

        ctk.CTkLabel(sidebar, text="Trading Frequency:", font=self.bold_font).pack(pady=(0, 0))
        trading_options = ["Monthly", "Bi-Monthly"]
        ctk.CTkOptionMenu(
            sidebar,
            values=trading_options,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.trading_frequency_var).pack(pady=(0, 10)
        )
        self.trading_frequency_var.trace_add("write", self.update_trading_frequency)

        ctk.CTkLabel(sidebar, text="Weighting Strategy:", font=self.bold_font).pack(pady=(0, 0))
        weighting_options = [
            "Use File Weights",
            "Equal Weight",
            "Risk Contribution",
            "Min Volatility",
            "Max Sharpe"
        ]
        ctk.CTkOptionMenu(
            sidebar,
            values=weighting_options,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.weighting_strategy_var).pack(pady=(0, 10)
        )
        self.weighting_strategy_var.trace_add("write", self.update_weighting_strategy)

        ctk.CTkLabel(sidebar, text="SMA Window (days):", font=self.bold_font).pack(pady=(0, 0))
        sma_windows = ["21", "42", "63", "84", "105", "126", "147", "168", "210"]

        ctk.CTkOptionMenu(
            sidebar,
            values=sma_windows,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.sma_window_var).pack(pady=(0, 10)
        )
        self.sma_window_var.trace_add("write", self.update_sma_window)

        ctk.CTkLabel(
            sidebar,
            text="Select portfolio assets:",
            font=self.bold_font).pack(pady=(0, 0)
        )
        ctk.CTkButton(
            sidebar,
            text="Select Asset Weights File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_weights_and_update).pack(pady=(10, 10)
        )

        # Right sidebar
        right_sidebar = ctk.CTkFrame(self, width=200)
        right_sidebar.grid(row=0, column=2, rowspan=4, sticky="ns", pady=(20, 0))

        ctk.CTkLabel(right_sidebar, text="Theme Mode:", font=self.bold_font).pack(pady=(20, 0))
        theme_options = ["Light", "Dark"]
        ctk.CTkOptionMenu(
            right_sidebar,
            values=theme_options,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.theme_mode_var,
            command=self.change_theme).pack(pady=(0, 20), padx=(10, 10)
        )
        self.theme_mode_var.trace_add("write", self.update_theme_mode)

        ctk.CTkLabel(
            right_sidebar,
            text="Select out of market assets:",
            font=self.bold_font).pack(pady=(0, 0)
        )
        ctk.CTkButton(
            right_sidebar,
            text="Select Asset Weights File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_out_of_market_weights_and_update).pack(pady=(10, 10)
        )

        ctk.CTkLabel(right_sidebar, text="Threshold Asset:", font=self.bold_font).pack(pady=(0, 0))
        ctk.CTkEntry(right_sidebar, textvariable=self.threshold_asset_entry_var).pack(pady=(0, 10))
        self.threshold_asset_entry_var.trace_add("write", self.update_threshold_asset)

        ctk.CTkLabel(
            right_sidebar,
            text="Number of assets to select:",
            font=self.bold_font).pack(pady=(0, 0)
        )
        ctk.CTkEntry(
            right_sidebar,
            textvariable=self.num_assets_to_select_entry_var
        ).pack(pady=(0, 10))
        self.num_assets_to_select_entry_var.trace_add("write", self.update_num_assets_to_select)

    def create_tab_content(self, tab):
        """
        Creates the content for the tabs.
        """
        tab_control = ctk.CTkTabview(
            tab,
            border_color="#edeaea",
            fg_color="#edeaea",
            segmented_button_fg_color="#edeaea",
            segmented_button_unselected_color="#bb8fce",
            segmented_button_selected_color="#8e44ad",
            text_color="#000000",
            segmented_button_selected_hover_color="#8e44ad"
        )
        tab_control.pack(expand=1, fill="both")

        self.create_signals_tab(tab_control, self.bold_font)
        self.create_backtesting_tab(tab_control)
        self.create_monte_carlo_tab(tab_control, self.bold_font)

    def create_signals_tab(self, tab_control, bold_font):
        """
        Creates the signals tab with input fields and buttons for generating signals.

        Parameters
        ----------
        tab_control : ctk.CTkTabview
            The tab control widget where the signals tab will be added.
        bold_font : ctk.CTkFont
            The font style to be applied to labels within the tab.
        """
        signals_tab = tab_control.add("Portfolio Signals")
        ctk.CTkLabel(
            signals_tab,
            text="Generate Portfolio Signals",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        ctk.CTkLabel(signals_tab, text="Date for Signals:", font=bold_font).pack(pady=0)
        signal_date = ctk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        ctk.CTkEntry(signals_tab, textvariable=signal_date).pack(pady=(0, 10))
        ctk.CTkButton(
            signals_tab,
            text="Generate Signals",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=lambda: self.run_signals_and_display(signal_date.get())
        ).pack(pady=10)

    def create_backtesting_tab(self, tab_control):
        """
        Creates the backtesting tab with input fields and buttons for running a backtest.

        Parameters
        ----------
        tab_control : ctk.CTkTabview
            The tab control widget where the backtesting tab will be added.
        """
        backtesting_tab = tab_control.add("Portfolio Backtesting")
        ctk.CTkLabel(
            backtesting_tab,
            text="Portfolio Backtesting",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        ctk.CTkButton(
            backtesting_tab,
            text="Run Backtest",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.run_backtest
        ).pack(pady=10)

    def create_monte_carlo_tab(self, tab_control, bold_font):
        """
        Creates the Monte Carlo simulation tab with 
        input fields and buttons for running a simulation.

        Parameters
        ----------
        tab_control : ctk.CTkTabview
            The tab control widget where the Monte Carlo simulation tab will be added.
        bold_font : ctk.CTkFont
            The font style to be applied to labels within the tab.
        """
        monte_carlo_tab = tab_control.add("Monte Carlo Simulation")
        ctk.CTkLabel(
            monte_carlo_tab,
            text="Monte Carlo Simulation",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        ctk.CTkLabel(monte_carlo_tab, text="Number of Simulations:", font=bold_font).pack(pady=0)
        ctk.CTkEntry(monte_carlo_tab, textvariable=self.num_simulations_var).pack(pady=(0, 10))
        self.num_simulations_var.trace_add("write", self.update_num_simulations)

        ctk.CTkLabel(
            monte_carlo_tab,
            text="Simulation Horizon (years):",
            font=bold_font
        ).pack(pady=0)
        ctk.CTkEntry(monte_carlo_tab, textvariable=self.simulation_horizon_var).pack(pady=(0, 10))
        self.simulation_horizon_var.trace_add("write", self.update_simulation_horizon)

        ctk.CTkButton(
            monte_carlo_tab,
            text="Run Simulation",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.run_simulation
        ).pack(pady=10)

    def change_theme(self, selected_theme):
        """
        Changes the theme of the application based on user selection.

        Parameters
        ----------
        selected_theme : str
            The selected theme mode, either "Light" or "Dark".
        """
        ctk.set_appearance_mode(selected_theme)

    def run_backtest(self):
        """
        Task runner for backtesting, selects the correct function based on the active tab.
        """
        self.clear_bottom_text()
        active_tab = self.high_level_tab_control.get()
        if active_tab == "SMA Strategies":
            threading.Thread(target=self._run_backtest_task, args=(main.run_backtest,)).start()
        elif active_tab == "Momentum Strategies":
            threading.Thread(
                target=self._run_backtest_task,
                args=(main.run_momentum_backtest,)
            ).start()
        elif active_tab == "Machine Learning Strategies":
            threading.Thread(
                target=self._run_backtest_task,
                args=(main.run_machine_learning_backtest,)
            ).start()
        elif active_tab == "Momentum In & Out Strategies":
            threading.Thread(
                target=self._run_backtest_task,
                args=(main.run_in_and_out_of_market_backtest,)
            ).start()

    def _run_backtest_task(self, backtest_func):
        """
        Runs the backtest task in a separate thread.

        Parameters
        ----------
        backtest_func : function
            The backtest function to be called.
        """
        result = backtest_func(self.data_models)
        self.after(0, lambda: self.display_result(result))

    def run_simulation(self):
        """
        Task runner for simulations, selects the correct function based on the active tab.
        """
        self.clear_bottom_text()
        active_tab = self.high_level_tab_control.get()
        if active_tab == "SMA Strategies":
            threading.Thread(target=self._run_simulation_task, args=(main.run_simulation,)).start()
        # elif active_tab == "Momentum Strategies":
        #     threading.Thread(
        #         target=self._run_simulation_task,
        #         args=(main.run_momentum_simulation,)
        #     ).start()
        # elif active_tab == "Machine Learning Strategies":
        #     threading.Thread(
        #         target=self._run_simulation_task,
        #         args=(main.run_machine_learning_simulation,)
        #     ).start()

    def _run_simulation_task(self, simulation_func):
        """
        Runs the simulation task in a separate thread.

        Parameters
        ----------
        simulation_func : function
            The simulation function to be called.
        """
        result = simulation_func(self.data_models)
        self.after(0, lambda: self.display_result(result))

    def run_signals_and_display(self, current_date):
        """
        Task runner for signal generation, selects the correct function based on the active tab.
        """
        self.clear_bottom_text()
        active_tab = self.high_level_tab_control.get()
        if active_tab == "SMA Strategies":
            threading.Thread(
                target=self._run_signals_task,
                args=(main.run_signals, current_date)
            ).start()
        elif active_tab == "Momentum Strategies":
            threading.Thread(
                target=self._run_signals_task,
                args=(main.run_momentum_signals, current_date)
            ).start()
        elif active_tab == "Momentum In & Out Strategies":
            threading.Thread(
                target=self._run_signals_task,
                args=(main.run_in_and_out_of_market_signals, current_date)
            ).start()
        elif active_tab == "Machine Learning Strategies":
            threading.Thread(
                target=self._run_signals_task,
                args=(main.run_machine_learning_signals,
                      current_date)
            ).start()

    def _run_signals_task(self, signals_func, current_date):
        """
        Runs the signal generation task in a separate thread.

        Parameters
        ----------
        signals_func : function
            The signal generation function to be called.
        current_date : str
            The date for which to generate signals.
        """
        self.data_models.end_date = current_date
        result = signals_func(self.data_models)
        self.after(0, lambda: self.display_result(result))

    def clear_bottom_text(self):
        """
        Clears the text at the bottom of the GUI.

        Parameters
        ----------
        None
        """
        for widget in self.bottom_text_frame.winfo_children():
            widget.destroy()

    def load_weights_and_update(self):
        """
        Loads the asset weights from a file and updates the assets_weights attribute.

        Parameters
        ----------
        None
        """
        self.clear_bottom_text()
        self.data_models.assets_weights, self.data_models.weights_filename = utilities.load_weights()
        if self.data_models.assets_weights:
            self.data_models.weights_filename = utilities.strip_csv_extension(
                self.data_models.weights_filename
            )
            self.display_asset_weights()

    def load_out_of_market_weights_and_update(self):
        """
        Loads the asset weights from a file and updates the assets_weights attribute.

        Parameters
        ----------
        None
        """
        self.clear_bottom_text()
        self.data_models.out_of_market_tickers, self.file_name = utilities.load_weights()

    def display_asset_weights(self):
        """
        Displays the loaded asset weights in the GUI, capped at 10.

        Parameters
        ----------
        None
        """
        assets_text = "\n".join(
            [f"{asset}: {weight}" for asset, weight in list(self.data_models.assets_weights.items())[:10]]
        )
        if len(self.data_models.assets_weights) > 10:
            assets_text += f"\n... (and {(len(self.data_models.assets_weights)-10)} more)"

        self.bottom_text = ctk.CTkLabel(
            self.bottom_text_frame,
            text=f"Loaded Assets and Weights from: \n\n{self.data_models.weights_filename}:\n{assets_text}",
            text_color="blue",
            fg_color="#edeaea"
        )
        self.bottom_text.pack(pady=5)

    def display_result(self, result):
        """
        Displays the result of a task in the GUI.

        Parameters
        ----------
        result : str
            The result text to be displayed in the GUI.
        """
        self.bottom_text = ctk.CTkLabel(
            self.bottom_text_frame,
            text=result, text_color="green" if "completed" in result else "red"
        )
        self.bottom_text.pack(pady=5)

    def update_start_date(self, *args):
        """
        Updates the start date in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        # _ = args
        self.data_models.start_date = self.start_date_var.get()

    def update_end_date(self, *args):
        """
        Updates the end date in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.end_date = self.end_date_var.get()

    def update_cash_ticker(self, *args):
        """
        Updates the cash ticker in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.cash_ticker = self.cash_ticker_var.get()

    def update_bond_ticker(self, *args):
        """
        Updates the bond ticker in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.bond_ticker = self.bond_ticker_var.get()

    def update_trading_frequency(self, *args):
        """
        Updates the trading frequency in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.trading_frequency = self.trading_frequency_var.get()

    def update_weighting_strategy(self, *args):
        """
        Updates the weighting strategy in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.weighting_strategy = self.weighting_strategy_var.get()

    def update_sma_window(self, *args):
        """
        Updates the SMA window in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.sma_window = self.sma_window_var.get()

    def update_num_simulations(self, *args):
        """
        Updates the number of simulations in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.num_simulations = int(self.num_simulations_var.get())

    def update_simulation_horizon(self, *args):
        """
        Updates the simulation horizon in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.simulation_horizon = int(self.simulation_horizon_var.get())

    def update_initial_portfolio_value(self, *args):
        """
        Updates the initial portfolio value in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.initial_portfolio_value = int(self.initial_portfolio_value_var.get())

    def update_theme_mode(self, *args):
        """
        Updates the theme mode in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.theme_mode = self.theme_mode_var.get()

    def update_threshold_asset(self, *args):
        """
        Updates the threshold asset in the data model based on the entry box.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.threshold_asset = str(self.threshold_asset_entry_var.get())

    def update_num_assets_to_select(self, *args):
        """
        Updates the threshold asset in the data model based on the entry box.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.num_assets_to_select = str(self.num_assets_to_select_entry_var.get())


if __name__ == "__main__":
    app = PortfolioAnalyzer()
    app.mainloop()
