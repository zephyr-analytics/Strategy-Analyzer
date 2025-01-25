"""
Abstract module for processing momentum trading models.
"""

import os
import threading
import logging
from datetime import datetime
from abc import ABC, abstractmethod

import customtkinter as ctk
import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.data.data_obtainment_processor import DataObtainmentProcessor
from strategy_analyzer.data.data_preparation_processor import DataPreparationProcessor
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.processing_types import *
from strategy_analyzer.models.models_factory import ModelsFactory
from strategy_analyzer.results.models_results import ModelsResults

logger = logging.getLogger(__name__)


class PageProcessor(ABC, ctk.CTkFrame):
    def __init__(self, parent, controller, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        super().__init__(master=parent)
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")
        self.controller = controller
        self.parent = parent
        self.start_date_var = ctk.StringVar(value=self.data_models.start_date)
        self.bottom_text_result_display = ctk.CTkFrame(self)
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=3, column=0, columnspan=5, sticky="nsew")
        self.settings_frame.grid_columnconfigure([0, 1, 2], weight=1)
        self.settings_frame.grid_rowconfigure([0, 1], weight=1)
        self.process()

    def process(self):
        """
        """
        self.build_frame()
        self.build_settings()

    @abstractmethod
    def build_frame(self):
        """
        """

    @abstractmethod
    def build_settings(self):
        """
        """

    def obtain_data(self):
        """
        Method to run data obtainment script.
        """
        self.data_models.start_date = self.start_date_var.get()
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
        assets_weights, weights_filename = utilities.load_weights()
        self.data_models.assets_weights = assets_weights
        self.data_models.weights_filename = weights_filename
        if self.data_models.assets_weights:
            self.data_models.weights_filename = utilities.strip_csv_extension(
                self.data_models.weights_filename
            )

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

    def execute_task(self, run_type, model_type):
        """
        Executes the task based on the selected tab and run type.

        Parameters
        ----------
        tab_name : str
            The name of the tab selected (e.g., "SMA Strategies").
        """
        model_map = {
            "MA": Models.MA,
            "MOMENTUM": Models.MOMENTUM,
            "IN_AND_OUT_OF_MARKET": Models.IN_AND_OUT_OF_MARKET,
            "MA_CROSSOVER": Models.MA_CROSSOVER,
            "MACHINE_LEARNING": Models.MACHINE_LEARNING
        }

        run_map = {
            "BACKTEST": Runs.BACKTEST,
            "SIGNALS": Runs.SIGNALS,
            "TUNE": Runs.PARAMETER_TUNE,
            "SIMULATION": Runs.SIMULATION
        }

        model_enum = model_map.get(model_type)
        run_enum = run_map.get(run_type)
        print(model_enum)
        print(run_enum)

        if not model_enum or not run_enum:
            self.display_result("Invalid model or run type selection.")
            return

        threading.Thread(
            target=self._run_task,
            args=(model_enum, run_enum),
        ).start()

    def _run_task(self, model, run_type):
        """
        Generic task runner for executing a specific model and run type in a separate thread.

        Parameters
        ----------
        model : Models
            The model to run (e.g., Models.SMA).
        run_type : Runs
            The run type (e.g., Runs.BACKTEST, Runs.SIMULATION, Runs.SIGNALS).
        """
        self.clear_message_text()
        try:
            factory = ModelsFactory(
                models_data=self.data_models,
                portfolio_data=self.data_portfolio,
                models_results=self.results_models
            )
            result = factory.run(model, run_type)
            self.after(0, lambda: self.display_result(result))
        finally:
            pass

    def open_artifacts_directory(self):
        """
        Opens the artifacts plot directory on Windows.
        """
        path = os.path.join(os.getcwd(), "artifacts", self.data_models.weights_filename)
        artifacts_dir = path

        try:
            os.startfile(artifacts_dir)
        except Exception as e:
            print(f"Error opening directory: {e}")
    
    def clear_message_text(self):
        """
        Clears the text in the bottom text area.
        """
        self.bottom_text_result_display.destroy()

    def display_result(self, result: str):
        """
        Displays the result of a task in the GUI.

        Parameters
        ----------
        result : str
            The result text to be displayed in the GUI.
        """
        self.bottom_text_result_display.destroy()
        self.bottom_text_result_display = ctk.CTkFrame(self)
        self.bottom_text_result_display.grid(row=3, column=3)
        self.bottom_text_result = ctk.CTkLabel(
            self.bottom_text_result_display,
            text=result, text_color="green" if "completed" in result else "red",
            fg_color="transparent",
        )
        self.bottom_text_result.grid(row=0, column=0)

    def build_data_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        # Data Settings
        data_frame_rows = 0
        data_frame = ctk.CTkFrame(parent, fg_color="transparent")
        data_frame.grid(row=data_frame_rows, column=0, padx=10, pady=10, sticky="nsew")

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

        data_frame_rows += 1

        initial_portfolio_value_var = ctk.StringVar(value=self.data_models.initial_portfolio_value)
        ctk.CTkEntry(
            data_frame, textvariable=initial_portfolio_value_var
        ).grid(row=data_frame_rows, column=0, padx=5, sticky="nsew", pady=y_padding)
        initial_portfolio_value_var.trace_add(
            "write", lambda *args: self.update_models_data("initial_portfolio_value", initial_portfolio_value_var)
        )

        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Trading Assets:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(
            data_frame, text="Out of Market Assets:", font=self.bold_font
        ).grid(row=data_frame_rows, column=1, sticky="nsew", padx=5)

        data_frame_rows += 1

        ctk.CTkButton(
            data_frame,
            text="Select .csv File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_weights_and_update
        ).grid(row=data_frame_rows, column=0, sticky="nsew", padx=5, pady=y_padding)

        ctk.CTkButton(
            data_frame,
            text="Select .csv File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_out_of_market_weights_and_update
        ).grid(row=data_frame_rows, column=1, sticky="nsew", padx=5, pady=y_padding)

        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Start Date:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, padx=5, sticky="nsew")
        ctk.CTkLabel(
            data_frame, text="End Date:", font=self.bold_font
        ).grid(row=data_frame_rows, column=1, padx=5, sticky="nsew")

        data_frame_rows += 1

        ctk.CTkEntry(
            data_frame, textvariable=self.start_date_var
        ).grid(row=data_frame_rows, column=0, padx=5, sticky="nsew", pady=y_padding)
        self.start_date_var.trace_add(
            "write", lambda *args: self.update_models_data("start_date", self.start_date_var)
        )
        end_date_var = ctk.StringVar(value=self.data_models.end_date)
        ctk.CTkEntry(
            data_frame, textvariable=end_date_var
        ).grid(row=data_frame_rows, column=1, padx=5, sticky="nsew", pady=y_padding)
        end_date_var.trace_add(
            "write", lambda *args: self.update_models_data("end_date", end_date_var)
        )

        data_frame_rows += 1

        ctk.CTkLabel(
            data_frame, text="Cash Ticker:", font=self.bold_font
        ).grid(row=data_frame_rows, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(
            data_frame, text="Bond Ticker:", font=self.bold_font
        ).grid(row=data_frame_rows, column=1, sticky="nsew", padx=5)

        data_frame_rows += 1

        cash_ticker_var = ctk.StringVar(value=self.data_models.cash_ticker)
        ctk.CTkEntry(
            data_frame, textvariable=cash_ticker_var
        ).grid(row=data_frame_rows, column=0, sticky="nsew", padx=5, pady=y_padding)
        cash_ticker_var.trace_add(
            "write", lambda *args: self.update_models_data("cash_ticker", cash_ticker_var)
        )
        bond_ticker_var = ctk.StringVar()
        ctk.CTkEntry(
            data_frame, textvariable=bond_ticker_var
        ).grid(row=data_frame_rows, column=1, sticky="nsew", padx=5, pady=y_padding)
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
        ).grid(row=data_frame_rows, column=0, padx=5, pady=y_padding)

        ctk.CTkButton(
            data_frame,
            text="Prepare Data",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.prepare_data,
        ).grid(row=data_frame_rows, column=1, padx=5, pady=y_padding)


    def build_trade_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        trade_frame_rows = 0
        trade_frame = ctk.CTkFrame(parent, fg_color="transparent")
        trade_frame.grid(row=trade_frame_rows, column=1, padx=10, pady=10, sticky="nsew")
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
        ma_frame.grid(row=ma_frame_rows, column=2, padx=10, pady=10, sticky="nsew")
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
        ma_frame_rows += 1

        ctk.CTkLabel(
            ma_frame, text="Sets the moving average parameters for MA Crossover.", font=self.bold_font
        ).grid(row=ma_frame_rows, column=0, columnspan=4, sticky="ew", pady=y_padding)
        ma_frame_rows += 1

        ctk.CTkLabel(
            ma_frame, text="Slow Moving Average:", font=self.bold_font
        ).grid(row=ma_frame_rows, column=0, sticky="e", padx=5)
        slow_ma = ["21", "42", "63", "84", "105", "126", "147", "168", "189", "210", "231", "252"]
        slow_ma_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            ma_frame,
            values=slow_ma,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=slow_ma_var
        ).grid(row=ma_frame_rows, column=1, sticky="w", padx=5, pady=y_padding)
        slow_ma_var.trace_add(
            "write", lambda *args: self.update_models_data("slow_ma_period", slow_ma_var)
        )

        ctk.CTkLabel(
            ma_frame, text="Fast Moving Average:", font=self.bold_font
        ).grid(row=ma_frame_rows, column=2, sticky="e", padx=5)
        fast_ma = ["21", "42", "63", "84", "105", "126", "147", "168", "189", "210", "231", "252"]
        fast_ma_var = ctk.StringVar()
        ctk.CTkOptionMenu(
            ma_frame,
            values=fast_ma,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            variable=fast_ma_var
        ).grid(row=ma_frame_rows, column=3, sticky="w", padx=5, pady=y_padding)
        fast_ma_var.trace_add(
            "write", lambda *args: self.update_models_data("fast_ma_period", fast_ma_var)
        )

    def build_momentum_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        momentum_frame_rows = 0
        momentum_frame = ctk.CTkFrame(parent, fg_color="transparent")
        momentum_frame.grid(row=momentum_frame_rows, column=3, padx=10, pady=10, sticky="nsew")
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
        monte_carlo_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
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
