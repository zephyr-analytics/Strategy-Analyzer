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

logger = logging.getLogger(__name__)


class PageProcessor(ABC, ctk.CTkFrame):
    def __init__(self, parent, controller, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        super().__init__(master=parent)
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results

        self.controller = controller
        self.parent = parent

        self.process()

    def process(self):
        """
        """
        self.build_frame()

    @abstractmethod
    def build_frame(self):
        """
        """
