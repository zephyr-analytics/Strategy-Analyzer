"""
Abstract module for processing momentum trading models.
"""

import datetime
import logging
from datetime import datetime
from abc import ABC, abstractmethod

import customtkinter as ctk
import pandas as pd

import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.processing_types import *
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.gui.page_processor import PageProcessor

logger = logging.getLogger(__name__)


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
        ctk.CTkButton(self, text="Run Backtest", command=self.run_backtest).grid(row=1, column=0, padx=10, pady=10)

    def run_backtest(self):
        logger.info("Running backtest...")
        print("Backtest logic goes here.")
