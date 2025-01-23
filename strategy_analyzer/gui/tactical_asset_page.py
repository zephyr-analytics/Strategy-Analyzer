"""
Abstract module for processing momentum trading models.
"""

import customtkinter as ctk

from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.processing_types import *
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.gui.page_processor import PageProcessor


class TacticalAssetPage(PageProcessor):
    def __init__(self, parent, controller, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        super().__init__(parent, controller, models_data, portfolio_data, models_results)
        self.controller = controller
        self.models_data = models_data
        self.portfolio_data = portfolio_data
        self.models_results = models_results
        self.parent = parent

    def build_frame(self):
        """
        Build the UI components for the BackTestingPage.
        """
        ctk.CTkLabel(self, text="Backtesting Page", font=("Arial", 18)).grid(row=0, column=0, padx=10, pady=10)

    def build_settings(self):
        """
        """
        y_padding = 2
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.create_testing_frame(parent=self)
        self.build_data_frame(parent=self, y_padding=y_padding)
        self.build_trade_frame(parent=self, y_padding=y_padding)
        self.build_moving_avergae_frame(parent=self, y_padding=y_padding)
        self.build_momentum_frame(parent=self, y_padding=y_padding)

    def create_testing_frame(self, parent):
        """
        Creates a single tab with a dropdown menu for selecting Runs enum values
        and integrates plot display functionality.

        Parameters
        ----------
        tab_name : str
            The name of the tab to create.
        """
        testing_frame = ctk.CTkFrame(parent, fg_color="transparent")
        testing_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")
        testing_frame.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        ctk.CTkLabel(
            testing_frame,
            text="Select Model Type:",
            font=ctk.CTkFont(size=14),
        ).grid(row=0, column=0, sticky="e", padx=5)

        model_options = [model_type.name for model_type in Models]
        self.model_types_var = ctk.StringVar()
        run_dropdown = ctk.CTkOptionMenu(
            testing_frame,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            values=model_options,
            variable=self.model_types_var,
        )
        run_dropdown.grid(row=0, column=1, sticky="w", padx=5)

        ctk.CTkButton(
            testing_frame,
            text="Run",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=lambda: self.execute_task(run_type="BACKTEST", model_type=self.model_types_var.get()),
        ).grid(row=0, column=2)

        ctk.CTkButton(
            testing_frame,
            text="Open Artifacts Directory",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.open_artifacts_directory,
        ).grid(row=0, column=3)

    def build_data_frame(self, parent: ctk.CTkFrame, y_padding):
        """
        """
        # Data Settings
        data_frame_rows = 1
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
        ctk.CTkEntry(
            data_frame, textvariable=self.start_date_var
        ).grid(row=data_frame_rows, column=1, padx=5, sticky="w", pady=y_padding)
        self.start_date_var.trace_add(
            "write", lambda *args: self.update_models_data("start_date", self.start_date_var)
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
        trade_frame_rows = 1
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
        ma_frame_rows = 1
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
        momentum_frame_rows = 1
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
