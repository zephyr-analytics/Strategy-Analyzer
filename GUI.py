"""
GUI user interface for running application.
"""

import customtkinter as ctk

from gui import *
from models_data import ModelsData

class PortfolioAnalyzer(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.
    """

    def __init__(self):
        super().__init__()
        self.title("Portfolio Analyzer")
        self.geometry("1200x700")
        self.data_models = ModelsData()

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
        self.high_level_tab_control = ctk.CTkTabview(center_frame)
        self.high_level_tab_control.pack(expand=1, fill="both")

        # Add Initial Testing Setup Tab
        setup_tab_frame = self.high_level_tab_control.add("Initial Testing Setup")
        self.setup_tab = SetupTab(setup_tab_frame, data_models=self.data_models)

        # Add Testing Tab
        testing_tab_frame = self.high_level_tab_control.add("Testing")
        self.testing_tab = TestingTab(testing_tab_frame, data_models=self.data_models)

        # Set initial tab
        self.high_level_tab_control.set("Initial Testing Setup")


if __name__ == "__main__":
    app = PortfolioAnalyzer()
    app.mainloop()
