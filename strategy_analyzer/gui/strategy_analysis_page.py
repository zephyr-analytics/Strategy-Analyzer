"""
Abstract module for processing momentum trading models.
"""

import customtkinter as ctk

from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.processing_types import *
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.gui.page_processor import PageProcessor


class StrategyAnalysisPage(PageProcessor):
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
        self.grid_rowconfigure([0, 1, 2], weight=1)
        ctk.CTkLabel(self, text="Strategy Analysis Page", font=("Arial", 18)).grid(row=0, column=0, padx=10, pady=10)

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
        testing_frame.grid(row=1, column=0, columnspan=5, sticky="nsew")
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
            command=lambda: self.execute_task(run_type="TUNE", model_type=self.model_types_var.get()),
        ).grid(row=0, column=2)

        ctk.CTkButton(
            testing_frame,
            text="Open Artifacts Directory",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.open_artifacts_directory,
        ).grid(row=0, column=3)
