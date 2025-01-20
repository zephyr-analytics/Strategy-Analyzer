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


class LoadingPage:
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
        Method to process through building the Setup Tab.
        """
        pass