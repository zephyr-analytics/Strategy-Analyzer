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
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title of the page
        ctk.CTkLabel(self, text="Tactical Asset Page", font=("Arial", 18)).grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10
        )

        # Create a new frame for the information
        information_frame = ctk.CTkFrame(self)
        information_frame.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)

        # Configure rows and columns for the information_frame
        information_frame.grid_rowconfigure([0, 1, 2, 3, 4], weight=1)
        information_frame.grid_columnconfigure(0, weight=1)

        # Title for Momentum Models
        ctk.CTkLabel(information_frame, text="Momentum Models", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky="nsew", padx=5, pady=5
        )

        # Paragraph for Momentum Models
        momentum_text = (
            "\u2022 The relative strength momentum model invests in the best-performing assets in the model based on "
            "each asset's past return.\n"
            "\u2022 The momentum can be based on a single lookback period or multiple weighted lookback periods.\n"
            "\u2022 The model supports using moving averages as a risk control to decide whether investments "
            "should be moved to cash."
        )
        ctk.CTkLabel(information_frame, text=momentum_text, font=("Arial", 12), justify="left", wraplength=600).grid(
            row=1, column=0, sticky="nsew", padx=5, pady=10
        )

        # Title for Moving Average Models
        ctk.CTkLabel(information_frame, text="Moving Average Models", font=("Arial", 14, "bold")).grid(
            row=2, column=0, sticky="nsew", padx=5, pady=5
        )

        # Paragraph for Moving Average Models
        moving_average_text = (
            "\u2022 The moving average tactical asset allocation model is either invested in a specific stock, ETF, "
            "or mutual fund, or is alternatively in cash or other risk-free assets based on the moving average signal.\n"
            "\u2022 The model is invested in the asset when the adjusted close price is greater than the moving average, "
            "and it moves to cash when the adjusted close price is less than the moving average.\n"
            "\u2022 The model supports using moving average cross-over as the signal."
        )
        ctk.CTkLabel(information_frame, text=moving_average_text, font=("Arial", 12), justify="left", wraplength=600).grid(
            row=3, column=0, sticky="nsew", padx=5, pady=10
        )


    def build_settings(self):
        """
        """
        parent = self.settings_frame
        y_padding = 2
        self.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)

        self.create_testing_frame(parent=self)

        self.build_data_frame(parent=parent, y_padding=y_padding)
        self.build_trade_frame(parent=parent, y_padding=y_padding)
        self.build_moving_avergae_frame(parent=parent, y_padding=y_padding)
        self.build_momentum_frame(parent=parent, y_padding=y_padding)

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
        testing_frame.grid(row=2, column=0, columnspan=5, sticky="nsew")
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
