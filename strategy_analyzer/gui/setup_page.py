"""
Module for creating the setup page.
"""

import tkinter as tk

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import strategy_analyzer.utilities as utilities
from strategy_analyzer.data.data_obtainment_processor import DataObtainmentProcessor
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.data.data_preparation_processor import DataPreparationProcessor
from strategy_analyzer.models.models_data import ModelsData


class SetupTab:
    """
    Handles the layout and functionality of the Initial Testing Setup parent.
    """
    def __init__(self, parent, models_data: ModelsData, portfolio_data: PortfolioData):
        self.data_models = models_data
        self.data_portfolio = portfolio_data

        self.parent = parent
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")
        self.theme_mode_var = ctk.StringVar(value="Light")
        self.chart_frame = None
        self.process(parent=parent)


    def process(self, parent):
        """
        """
        y_padding = 2
        self.create_initial_testing_tab(parent)
        self.build_chart(parent=parent)
        self.build_data_frame(parent=parent, y_padding=y_padding)
        self.build_trade_frame(parent=parent, y_padding=y_padding)
        self.build_moving_avergae_frame(parent=parent, y_padding=y_padding)
        self.build_momentum_frame(parent=parent, y_padding=y_padding)
        self.build_monte_carlo_frame(parent=parent, y_padding=y_padding)
        self.build_bottom_frame(parent=parent)


    def create_initial_testing_tab(self, parent: ctk.CTkFrame):
        """
        Creates the Initial Testing Setup parent with categorized inputs for data, SMA, and momentum settings,
        arranged using grid layout within frames and pack for frame placement.

        Parameters
        ----------
        parent : ctk.CTkFrame
            The frame for the Initial Testing Setup parent.
        """
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 10), padx=10)

        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header_frame,
            text="Configure your portfolio settings below.",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="center"
        ).grid(row=0, column=0, pady=10, sticky="ew")

        theme_label = ctk.CTkLabel(parent, text="Select Theme:", font=self.bold_font)
        theme_label.pack(pady=0)
        mode_dropdown = ctk.CTkOptionMenu(
            parent,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            values=["Light", "Dark"],
            variable=self.theme_mode_var,
            command=self.update_theme_mode
        )
        mode_dropdown.pack(pady=5)


    def build_chart(self, parent):
        """
        Build an empty pie chart during GUI initialization.
        """
        # Create an empty pie chart
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=16, color="gray")
        ax.axis("equal")  # Ensure the pie chart is circular

        # Embed the empty chart in the GUI
        self.chart_frame = ctk.CTkFrame(parent)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def update_chart_with_data(self, data: dict):
        """
        Update the pie chart with the given dictionary of data.

        Parameters
        ----------
        data : dict
            A dictionary with category names as keys and corresponding values.
        """
        # Clear the existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Check if the data is empty
        if not data:
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=16, color="gray")
        else:
            # Create a pie chart with the given data
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(
                data.values(),
                labels=data.keys(),
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={"edgecolor": "black"}
            )
            ax.axis("equal")  # Ensure the pie chart is circular

        # Embed the chart in the GUI
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    def build_data_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        # Data Settings
        data_frame_rows = 0
        data_frame = ctk.CTkFrame(parent, fg_color="transparent")
        data_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(
            data_frame, text="Data Settings", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, columnspan=4, sticky="ew")
        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Setup the initial portfolio composition.", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, columnspan=4, sticky="ew", pady=y_padding)
        data_frame_rows += 1

        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_columnconfigure(1, weight=1)
        data_frame.grid_columnconfigure(2, weight=1)
        data_frame.grid_columnconfigure(3, weight=1)

        # Add widgets dynamically and update row counter
        ctk.CTkLabel(
            data_frame, text="Initial Portfolio Value:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, padx=5, sticky="e")
        initial_portfolio_value_var = ctk.StringVar(value=self.data_models.initial_portfolio_value)
        ctk.CTkEntry(
            data_frame, textvariable=initial_portfolio_value_var
        ).grid(row=data_frame_rows, column=1, padx=5, sticky="w", pady=y_padding)
        initial_portfolio_value_var.trace_add(
            "write", lambda *args: self.update_models_data("initial_portfolio_value", initial_portfolio_value_var)
        )
        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Select In Market Assets:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, sticky="e", padx=5)
        ctk.CTkButton(
            data_frame,
            text="Select .csv File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_weights_and_update
        ).grid(row=data_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)

        ctk.CTkLabel(
            data_frame, text="Select Out of Market Assets:", font=self.bold_font
        ).grid(row=data_frame_rows, column=2, sticky="e", padx=5)
        ctk.CTkButton(
            data_frame,
            text="Select .csv File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_out_of_market_weights_and_update
        ).grid(row=data_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Start Date:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, padx=5, sticky="e")
        start_date_var = ctk.StringVar(value=self.data_models.start_date)
        ctk.CTkEntry(
            data_frame, textvariable=start_date_var
        ).grid(row=data_frame_rows, column=1, padx=5, sticky="w", pady=y_padding)
        start_date_var.trace_add(
            "write", lambda *args: self.update_models_data("start_date", start_date_var)
        )

        ctk.CTkLabel(
            data_frame, text="End Date:", font=self.bold_font
        ).grid(row=data_frame_rows, column=2, padx=5, sticky="e")
        end_date_var = ctk.StringVar(value=self.data_models.end_date)
        ctk.CTkEntry(
            data_frame, textvariable=end_date_var
        ).grid(row=data_frame_rows, column=3, padx=5, sticky="w", pady=y_padding)
        end_date_var.trace_add(
            "write", lambda *args: self.update_models_data("end_date", end_date_var)
        )
        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Cash Ticker:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, sticky="e", padx=5)
        cash_ticker_var = ctk.StringVar(value=self.data_models.cash_ticker)
        ctk.CTkEntry(
            data_frame, textvariable=cash_ticker_var
        ).grid(row=data_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        cash_ticker_var.trace_add(
            "write", lambda *args: self.update_models_data("cash_ticker", cash_ticker_var)
        )

        ctk.CTkLabel(
            data_frame, text="Bond Ticker:", font=self.bold_font
        ).grid(row=data_frame_rows, column=2, sticky="e", padx=5)
        bond_ticker_var = ctk.StringVar()
        ctk.CTkEntry(
            data_frame, textvariable=bond_ticker_var
        ).grid(row=data_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        bond_ticker_var.trace_add(
            "write", lambda *args: self.update_models_data("bond_ticker", bond_ticker_var)
        )
        data_frame_rows += 1

        ctk.CTkButton(
            data_frame,
            text="Obtain Data",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.obtain_data,
        ).grid(row=data_frame_rows, column=0, columnspan=2, padx=5, pady=y_padding)

        ctk.CTkButton(
            data_frame,
            text="Prepare Data",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.prepare_data,
        ).grid(row=data_frame_rows, column=2, columnspan=2, padx=5, pady=y_padding)


    def build_trade_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        trade_frame_rows = 0
        trade_frame = ctk.CTkFrame(parent, fg_color="transparent")
        trade_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(
            trade_frame, text="Trade Settings", font=self.bold_font
        ).grid(row=trade_frame_rows, column=0, columnspan=4, sticky="ew")
        trade_frame_rows += 1

        ctk.CTkLabel(
            trade_frame, text="Sets the trading parameters of the trading model.", font=self.bold_font
        ).grid(row=trade_frame_rows, column=0, columnspan=4, sticky="ew", pady=y_padding)
        trade_frame_rows += 1

        trade_frame.grid_columnconfigure(0, weight=1)
        trade_frame.grid_columnconfigure(1, weight=1)
        trade_frame.grid_columnconfigure(2, weight=1)
        trade_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            trade_frame, text="Benchmark Asset:", font=self.bold_font
        ).grid(row=trade_frame_rows, column=0, sticky="e", padx=5)
        benchmark_asset_var = ctk.StringVar()
        ctk.CTkEntry(
            trade_frame, textvariable=benchmark_asset_var
        ).grid(row=trade_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        benchmark_asset_var.trace_add(
            "write", lambda *args: self.update_models_data("benchmark_asset", benchmark_asset_var)
        )

        ctk.CTkLabel(
            trade_frame, text="Trading Frequency:", font=self.bold_font
        ).grid(row=trade_frame_rows, column=2, sticky="e", padx=5)
        trading_options = ["Monthly", "Bi-Monthly", "Quarterly", "Yearly"]
        trading_freq_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            trade_frame,
            values=trading_options,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=trading_freq_var
        ).grid(row=trade_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        trading_freq_var.trace_add(
            "write", lambda *args: self.update_models_data("trading_frequency", trading_freq_var)
        )


    def build_moving_avergae_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        ma_frame_rows = 0
        ma_frame = ctk.CTkFrame(parent, fg_color="transparent")
        ma_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(
            ma_frame, text="Moving Average Settings", font=self.bold_font
        ).grid(row=ma_frame_rows, column=0, columnspan=4, sticky="ew")
        ma_frame_rows += 1

        ctk.CTkLabel(
            ma_frame, text="Sets the moving average parameters of the trading model.", font=self.bold_font
        ).grid(row=ma_frame_rows, column=0, columnspan=4, sticky="ew", pady=y_padding)
        ma_frame_rows += 1

        ma_frame.grid_columnconfigure(0, weight=1)
        ma_frame.grid_columnconfigure(1, weight=1)
        ma_frame.grid_columnconfigure(2, weight=1)
        ma_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            ma_frame, text="Moving Average Window (days):", font=self.bold_font
        ).grid(row=ma_frame_rows, column=0, sticky="e", padx=5)
        ma_windows = ["21", "42", "63", "84", "105", "126", "147", "168", "189", "210", "231", "252"]
        ma_window_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            ma_frame,
            values=ma_windows,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=ma_window_var
        ).grid(row=ma_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        ma_window_var.trace_add(
            "write", lambda *args: self.update_models_data("ma_window", ma_window_var)
        )

        ctk.CTkLabel(
            ma_frame, text="Moving Average Threshold Asset:", font=self.bold_font
        ).grid(row=ma_frame_rows, column=2, sticky="e", padx=5)
        ma_threshold_asset_var = ctk.StringVar()
        ctk.CTkEntry(
            ma_frame, textvariable=ma_threshold_asset_var
        ).grid(row=ma_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        ma_threshold_asset_var.trace_add(
            "write", lambda *args: self.update_models_data("ma_threshold_asset", ma_threshold_asset_var)
        )
        ma_frame_rows += 1

        ctk.CTkLabel(
            ma_frame, text="Moving Average Type:", font=self.bold_font
        ).grid(row=ma_frame_rows, column=0, sticky="e", padx=5)
        ma_types = ["SMA", "EMA"]
        ma_type_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            ma_frame,
            values=ma_types,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=ma_type_var
        ).grid(row=ma_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        ma_type_var.trace_add(
            "write", lambda *args: self.update_models_data("ma_type", ma_type_var)
        )


    def build_momentum_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        momentum_frame_rows = 0
        momentum_frame = ctk.CTkFrame(parent, fg_color="transparent")
        momentum_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(
            momentum_frame, text="Momentum Settings", font=self.bold_font
        ).grid(row=momentum_frame_rows, column=0, columnspan=4, sticky="ew")
        momentum_frame_rows += 1

        ctk.CTkLabel(
            momentum_frame, text="Sets the momentum parameters of the trading model.", font=self.bold_font
        ).grid(row=momentum_frame_rows, column=0, columnspan=4, sticky="ew", pady=y_padding)
        momentum_frame_rows += 1

        momentum_frame.grid_columnconfigure(0, weight=1)
        momentum_frame.grid_columnconfigure(1, weight=1)
        momentum_frame.grid_columnconfigure(2, weight=1)
        momentum_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            momentum_frame, text="Number of assets to select:", font=self.bold_font
        ).grid(row=momentum_frame_rows, column=0, sticky="e", padx=5)
        num_assets_to_select_var = ctk.StringVar()
        ctk.CTkEntry(
            momentum_frame, textvariable=num_assets_to_select_var
        ).grid(row=momentum_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        num_assets_to_select_var.trace_add(
            "write", lambda *args: self.update_models_data("num_assets_to_select", num_assets_to_select_var)
        )
        momentum_frame_rows += 1

        ctk.CTkLabel(
            momentum_frame, text="Remove Negative Momentum:", font=self.bold_font
        ).grid(row=momentum_frame_rows, column=0, sticky="e", padx=5)
        negative_mom_allowed = ["True", "False"]
        negative_mom_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            momentum_frame,
            values=negative_mom_allowed,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=negative_mom_var
        ).grid(row=momentum_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        negative_mom_var.trace_add(
            "write", lambda *args: self.update_models_data("negative_mom", negative_mom_var)
        )


    def build_monte_carlo_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        monte_carlo_frame_rows = 0
        monte_carlo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        monte_carlo_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(
            monte_carlo_frame, text="Monte Carlo Settings", font=self.bold_font
        ).grid(row=monte_carlo_frame_rows, column=0, columnspan=4, sticky="ew")
        monte_carlo_frame_rows += 1

        ctk.CTkLabel(
            monte_carlo_frame, text="Sets the Monte Carlo parameters of the trading model.", font=self.bold_font
        ).grid(row=monte_carlo_frame_rows, column=0, columnspan=4, sticky="ew", pady=y_padding)
        monte_carlo_frame_rows += 1

        monte_carlo_frame.grid_columnconfigure(0, weight=1)
        monte_carlo_frame.grid_columnconfigure(1, weight=1)
        monte_carlo_frame.grid_columnconfigure(2, weight=1)
        monte_carlo_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            monte_carlo_frame, text="Simulation Horizon:", font=self.bold_font
        ).grid(row=monte_carlo_frame_rows, column=0, sticky="e", padx=5)
        simulation_horizon_entry_var = ctk.StringVar()
        ctk.CTkEntry(
            monte_carlo_frame, textvariable=simulation_horizon_entry_var
        ).grid(row=monte_carlo_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        simulation_horizon_entry_var.trace_add(
            "write", lambda *args: self.update_models_data("simulation_horizon", simulation_horizon_entry_var)
        )

        ctk.CTkLabel(
            monte_carlo_frame, text="Number Simulations To Run:", font=self.bold_font
        ).grid(row=monte_carlo_frame_rows, column=2, sticky="e", padx=5)
        num_simulations_var = ctk.StringVar()
        ctk.CTkEntry(
            monte_carlo_frame, textvariable=num_simulations_var
        ).grid(row=monte_carlo_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        num_simulations_var.trace_add(
            "write", lambda *args: self.update_models_data("num_simulation", num_simulations_var)
        )
        monte_carlo_frame_rows += 1

        ctk.CTkLabel(
            monte_carlo_frame, text="Contribution:", font=self.bold_font
        ).grid(row=monte_carlo_frame_rows, column=0, sticky="e", padx=5)
        contribution_entry_var = ctk.StringVar()
        ctk.CTkEntry(
            monte_carlo_frame, textvariable=contribution_entry_var
        ).grid(row=monte_carlo_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        contribution_entry_var.trace_add(
            "write", lambda *args: self.update_models_data("contribution", contribution_entry_var)
        )

        ctk.CTkLabel(
            monte_carlo_frame, text="Contribution Frequency:", font=self.bold_font
        ).grid(row=monte_carlo_frame_rows, column=2, sticky="e", padx=5)
        contribution_freq = ["Monthly", "Quarterly", "Yearly"]
        contribution_freq_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            monte_carlo_frame,
            values=contribution_freq,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=contribution_freq_var
        ).grid(row=monte_carlo_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        contribution_freq_var.trace_add(
            "write", lambda *args: self.update_models_data("contribution_frequency", contribution_freq_var)
        )


    def build_bottom_frame(self, parent: ctk.CTkFrame):
        """
        """
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=10)
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© Zephyr Analytics 2025",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack()

    def obtain_data(self):
        """
        Method to run data obtainment script.
        """
        data_obtain = DataObtainmentProcessor(models_data=self.data_models)
        data_obtain.process()

    def prepare_data(self):
        """
        Method to run data preparation script.
        """
        data_prepare = DataPreparationProcessor(models_data=self.data_models, portfolio_data=self.data_portfolio)
        data_prepare.process()

    def load_weights_and_update(self):
        """
        Loads the assets and weights from file and updates the attribute.
        """
        self.data_models.assets_weights, self.data_models.weights_filename = utilities.load_weights()
        if self.data_models.assets_weights:
            self.data_models.weights_filename = utilities.strip_csv_extension(
                self.data_models.weights_filename
            )
            self.update_chart_with_data(self.data_models.assets_weights)

    def load_out_of_market_weights_and_update(self):
        """
        Loads the out of market assets and weights from file and updates the attribute.
        """
        self.data_models.out_of_market_tickers, file_name = utilities.load_weights()

    def update_theme_mode(self, *args):
        """
        Updates the theme mode in the data model.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        ctk.set_appearance_mode(self.theme_mode_var.get())
        self.data_models.theme_mode = self.theme_mode_var.get()

    def update_models_data(self, var_name, var_value, *args):
        """
        Dynamically updates the corresponding attribute in the data model based on the provided variable name.

        Parameters
        ----------
        var_name : str
            The name of the attribute in the data model to update.
        var_value : Variable
            The variable from which to get the updated value.
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        value = var_value.get()

        setattr(self.data_models, var_name, value)
