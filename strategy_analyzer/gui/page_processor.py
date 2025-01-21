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
        self.bottom_text_result_display = ctk.CTkFrame(self)
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
            "BACKTEST": Runs.BACKTEST
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
