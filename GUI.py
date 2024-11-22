"""
Module for managing GUI and initialization.
"""

import customtkinter as ctk

from gui import *
from models.models_data import ModelsData

class PortfolioAnalyzer(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.
    """

    def __init__(self):
        super().__init__()
        self.title("Portfolio Analyzer")
        self.geometry("1200x800")
        data_models = ModelsData()
        self.data_models = data_models

        # Variables for binding to GUI
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        self.create_widgets()

    def create_widgets(self):
        """
        Creates the widgets and layouts for the application.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)

        # Central Frame
        center_frame = ctk.CTkFrame(self, fg_color="#edeaea")
        center_frame.grid(row=0, column=1, rowspan=1, sticky="nsew")

        # High-Level Tab Control
        self.high_level_tab_control = ctk.CTkTabview(center_frame, command=self.on_tab_switch)
        self.high_level_tab_control.pack(expand=1, fill="both")

        # Add Initial Testing Setup Tab
        setup_tab_frame = self.high_level_tab_control.add("Initial Testing Setup")
        self.setup_tab = SetupTab(setup_tab_frame, models_data=self.data_models)

        # Add Testing Tab
        testing_tab_frame = self.high_level_tab_control.add("Testing")
        self.testing_tab = TestingTab(testing_tab_frame, models_data=self.data_models)

        # Set initial tab
        self.high_level_tab_control.set("Initial Testing Setup")

    def on_tab_switch(self):
        """
        Callback for tab switching.
        Determines the active tab and calls the update_tab method of the respective tab.
        """
        active_tab = self.high_level_tab_control.get()
        if active_tab == "Initial Testing Setup":
            self.setup_tab.update_tab()
        elif active_tab == "Testing":
            self.testing_tab.update_tab()


if __name__ == "__main__":
    app = PortfolioAnalyzer()
    app.mainloop()
