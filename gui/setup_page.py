"""
Module for creating the setup page.
"""

import tkinter as tk
from datetime import datetime

import customtkinter as ctk

import utilities as utilities
from models.models_data import ModelsData


class SetupTab:
    """
    Handles the layout and functionality of the Initial Testing Setup parent.
    """

    def __init__(self, parent, models_data: ModelsData):
        self.data_models = models_data

        self.parent = parent
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        self.start_date_var = ctk.StringVar(value=self.data_models.start_date)
        self.end_date_var = ctk.StringVar(value=self.data_models.end_date)
        self.cash_ticker_var = ctk.StringVar(value=self.data_models.cash_ticker)
        self.bond_ticker_var = ctk.StringVar(value=self.data_models.bond_ticker)
        self.trading_frequency_var = ctk.StringVar(value=self.data_models.trading_frequency)
        self.weighting_strategy_var = ctk.StringVar(value=self.data_models.weighting_strategy)
        self.sma_window_var = ctk.StringVar(value=self.data_models.sma_window)
        self.num_simulations_var = ctk.StringVar(value=self.data_models.num_simulations)
        self.simulation_horizon_entry_var = ctk.StringVar(value=self.data_models.simulation_horizon)
        self.benchmark_asset_entry_var = ctk.StringVar(value=self.data_models.benchmark_asset)
        self.contribution_entry_var = ctk.StringVar(value=self.data_models.contribution)
        self.contribution_frequency_var = ctk.StringVar(value=self.data_models.contribution_frequency)
        # TODO this needs to be added to the UI.
        self.theme_mode_var = ctk.StringVar(value=self.data_models.theme_mode)
        self.initial_portfolio_value_var = ctk.StringVar(
            value=self.data_models._initial_portfolio_value
        )
        self.threshold_asset_entry_var = ctk.StringVar(value=self.data_models.threshold_asset)
        self.num_assets_to_select_entry_var = ctk.StringVar(
            value=self.data_models.num_assets_to_select
        )

        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")
        self.bottom_text_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.create_initial_testing_tab(self.parent)


    def create_initial_testing_tab(self, parent):
        """
        Creates the Initial Testing Setup parent with categorized inputs for data, SMA, and momentum settings,
        arranged using grid layout within frames and pack for frame placement.

        Parameters
        ----------
        parent : ctk.CTkFrame
            The frame for the Initial Testing Setup parent.
        """
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20), padx=10)

        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header_frame,
            text="Welcome to Portfolio Analyzer by Zephyr Analytics.",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="center"
        ).grid(row=0, column=0, pady=10, sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text="Configure your portfolio settings below.",
            wraplength=800,
            font=ctk.CTkFont(size=14),
            anchor="center"
        ).grid(row=1, column=0, pady=10, sticky="ew")


        # Data Settings
        data_frame = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        data_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(data_frame, text="Data Settings", font=self.bold_font).grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_columnconfigure(1, weight=1)
        data_frame.grid_columnconfigure(2, weight=1)
        data_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(data_frame, text="Initial Portfolio Value:", font=self.bold_font).grid(row=1, column=0, padx=5, sticky="e")
        ctk.CTkEntry(data_frame, textvariable=self.initial_portfolio_value_var).grid(row=1, column=1, padx=5, sticky="w")
        self.initial_portfolio_value_var.trace_add("write", self.update_initial_portfolio_value)

        ctk.CTkLabel(data_frame, text="Start Date:", font=self.bold_font).grid(row=2, column=0, padx=5, sticky="e")
        start_date_entry = ctk.CTkEntry(data_frame, textvariable=self.start_date_var)
        start_date_entry.grid(row=2, column=1, padx=5, sticky="w")
        start_date_entry.bind("<FocusOut>", self.update_start_date)

        ctk.CTkLabel(data_frame, text="End Date:", font=self.bold_font).grid(row=2, column=2, padx=5, sticky="e")
        end_date_entry = ctk.CTkEntry(data_frame, textvariable=self.end_date_var)
        end_date_entry.grid(row=2, column=3, padx=5, sticky="w")
        end_date_entry.bind("<FocusOut>", self.update_end_date)

        ctk.CTkLabel(data_frame, text="Cash Ticker:", font=self.bold_font).grid(row=3, column=0, sticky="e", padx=5)
        ctk.CTkEntry(data_frame, textvariable=self.cash_ticker_var).grid(row=3, column=1, sticky="w", padx=5)
        self.cash_ticker_var.trace_add("write", self.update_cash_ticker)

        ctk.CTkLabel(data_frame, text="Bond Ticker:", font=self.bold_font).grid(row=3, column=2, sticky="e", padx=5)
        ctk.CTkEntry(data_frame, textvariable=self.bond_ticker_var).grid(row=3, column=3, sticky="w", padx=5)
        self.bond_ticker_var.trace_add("write", self.update_bond_ticker)

        ctk.CTkLabel(data_frame, text="Threshold Asset:", font=self.bold_font).grid(row=4, column=0, sticky="e", padx=5)
        ctk.CTkEntry(data_frame, textvariable=self.threshold_asset_entry_var).grid(row=4, column=1, sticky="w", padx=5)
        self.threshold_asset_entry_var.trace_add("write", self.update_threshold_asset)

        ctk.CTkLabel(data_frame, text="Benchmark Asset:", font=self.bold_font).grid(row=4, column=2, sticky="e", padx=5)
        ctk.CTkEntry(data_frame, textvariable=self.benchmark_asset_entry_var).grid(row=4, column=3, sticky="w", padx=5)
        self.benchmark_asset_entry_var.trace_add("write", self.update_benchmark_asset)

        ctk.CTkLabel(data_frame, text="Trading Frequency:", font=self.bold_font).grid(row=5, column=0, sticky="e", padx=5)
        trading_options = ["Monthly", "Bi-Monthly"]
        ctk.CTkOptionMenu(
            data_frame,
            values=trading_options,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.trading_frequency_var
        ).grid(row=5, column=1, sticky="w", padx=5)
        self.trading_frequency_var.trace_add("write", self.update_trading_frequency)

        ctk.CTkLabel(
            data_frame,
            text="Select portfolio assets:",
            font=self.bold_font).grid(row=5, column=2, sticky="e", padx=5
        )
        ctk.CTkButton(
            data_frame,
            text="Select Asset Weights File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_weights_and_update).grid(row=5, column=3, sticky="w", padx=5
        )


        # SMA Settings
        sma_frame = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        sma_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(sma_frame, text="SMA Settings", font=self.bold_font).grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        sma_frame.grid_columnconfigure(0, weight=1)
        sma_frame.grid_columnconfigure(1, weight=1)
        sma_frame.grid_columnconfigure(2, weight=1)
        sma_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(sma_frame, text="SMA Window (days):", font=self.bold_font).grid(row=1, column=0, sticky="e", padx=5)
        sma_windows = ["21", "42", "63", "84", "105", "126", "147", "168", "210"]
        ctk.CTkOptionMenu(
            sma_frame,
            values=sma_windows,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.sma_window_var
        ).grid(row=1, column=1, sticky="w", padx=5)
        self.sma_window_var.trace_add("write", self.update_sma_window)


        # Momentum Settings
        momentum_frame = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        momentum_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(momentum_frame, text="Momentum Settings", font=self.bold_font).grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        momentum_frame.grid_columnconfigure(0, weight=1)
        momentum_frame.grid_columnconfigure(1, weight=1)
        momentum_frame.grid_columnconfigure(2, weight=1)
        momentum_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(momentum_frame, text="Number of assets to select:", font=self.bold_font).grid(row=2, column=0, sticky="e", padx=5)
        ctk.CTkEntry(momentum_frame, textvariable=self.num_assets_to_select_entry_var).grid(row=2, column=1, sticky="w", padx=5)
        self.num_assets_to_select_entry_var.trace_add("write", self.update_num_assets_to_select)

        ctk.CTkLabel(
            momentum_frame,
            text="Select out of market assets:",
            font=self.bold_font).grid(row=3, column=0, sticky="e", padx=5
        )
        ctk.CTkButton(
            momentum_frame,
            text="Select Asset Weights File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_out_of_market_weights_and_update).grid(row=3, column=1, sticky="w", padx=5
        )


        # Monte Carlo Settings
        monte_carlo_frame = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        monte_carlo_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(monte_carlo_frame, text="Monte Carlo Settings", font=self.bold_font).grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        monte_carlo_frame.grid_columnconfigure(0, weight=1)
        monte_carlo_frame.grid_columnconfigure(1, weight=1)
        monte_carlo_frame.grid_columnconfigure(2, weight=1)
        monte_carlo_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(monte_carlo_frame, text="Simulation Horizon:", font=self.bold_font).grid(row=1, column=0, sticky="e", padx=5)
        ctk.CTkEntry(monte_carlo_frame, textvariable=self.simulation_horizon_entry_var).grid(row=1, column=1, sticky="w", padx=5)
        self.simulation_horizon_entry_var.trace_add("write", self.update_simulation_horizon)

        ctk.CTkLabel(monte_carlo_frame, text="Number Simulations To Run:", font=self.bold_font).grid(row=1, column=2, sticky="e", padx=5)
        ctk.CTkEntry(monte_carlo_frame, textvariable=self.num_simulations_var).grid(row=1, column=3, sticky="w", padx=5)
        self.num_simulations_var.trace_add("write", self.update_num_simulations)

        ctk.CTkLabel(monte_carlo_frame, text="Contribution:", font=self.bold_font).grid(row=2, column=0, sticky="e", padx=5)
        ctk.CTkEntry(monte_carlo_frame, textvariable=self.contribution_entry_var).grid(row=2, column=1, sticky="w", padx=5)
        self.contribution_entry_var.trace_add("write", self.update_contribution)

        ctk.CTkLabel(monte_carlo_frame, text="Contribution Frequency:", font=self.bold_font).grid(row=2, column=2, sticky="e", padx=5)
        contribution_freq = ["Monthly", "Quarterly", "Yearly"]
        ctk.CTkOptionMenu(
            monte_carlo_frame,
            values=contribution_freq,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=self.contribution_frequency_var
        ).grid(row=2, column=3, sticky="w", padx=5)
        self.contribution_frequency_var.trace_add("write", self.update_contribution_frequency)


        self.bottom_text_frame.pack(padx=5, pady=5)
        # Footer Section
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=20)
        # Add copyright info
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© Zephyr Analytics 2024",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack()


    def clear_bottom_text(self):
        """
        Clears the text at the bottom of the GUI.

        Parameters
        ----------
        None
        """
        for widget in self.bottom_text_frame.winfo_children():
            widget.destroy()

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

    def update_start_date(self, *args):
        """
        Validates the start date format when the user moves focus away.
        """
        _ = args
        start_date_input = self.start_date_var.get()
        try:
            datetime.strptime(start_date_input, "%Y-%m-%d")
            self.data_models.start_date = start_date_input
        except ValueError:
            message = "Invalid Date Format\nThe start date must be in the format YYYY-MM-DD."
            self.show_error_popup(message=message)

    def update_end_date(self, *args):
        """
        Updates the end date in the data model and checks that it is greater than the start date.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        end_date_input = self.end_date_var.get()
        try:
            end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
            if hasattr(self.data_models, 'start_date') and self.data_models.start_date:
                start_date = datetime.strptime(self.data_models.start_date, "%Y-%m-%d")
                if end_date <= start_date:
                    message = "The end date must be greater than the start date."
                    self.show_error_popup(message=message)
                    return None

            self.data_models.end_date = end_date_input
        except ValueError:
            message = "Invalid Date Format\nThe end date must be in the format YYYY-MM-DD."
            self.show_error_popup(message=message)

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
        self.data_models.simulation_horizon = int(self.simulation_horizon_entry_var.get())

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

    def update_benchmark_asset(self, *args):
        """
        Updates the benchmark asset in the data model based on the entry box.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.benchmark_asset = str(self.benchmark_asset_entry_var.get())

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

    def update_contribution(self, *args):
        """
        Updates the contribution in the data model based on the entry box.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.contribution = int(self.contribution_entry_var.get())

    def update_contribution_frequency(self, *args):
        """
        Updates the contribution frequency in the data model based on the entry box.

        Parameters
        ----------
        *args : tuple
            Additional arguments passed by the trace method.
        """
        _ = args
        self.data_models.contribution_frequency = str(self.contribution_frequency_var.get())

    def show_error_popup(self, message):
        """
        Displays a popup error message for failed validation checks.

        Parameters
        ----------
        message : str
            String representing the error message to display.
        """
        popup = ctk.CTkToplevel(self.parent)
        popup.title("Error")
        popup.geometry("300x150")

        label = ctk.CTkLabel(
            popup,
            text=f"{message}",
            wraplength=250,
        )
        label.pack(pady=20)

        button = ctk.CTkButton(
            popup,
            text="OK",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",command=popup.destroy
        )
        button.pack(pady=10)

    def update_tab(self):
        """
        Method used by GUI to update tab components.
        """
        pass
