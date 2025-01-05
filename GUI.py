"""
Parent module for GUI.
"""

import multiprocessing

import customtkinter as ctk

from gui import *
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
import utilities as utilities


class PortfolioAnalyzer(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.
    """
    def __init__(self):
        super().__init__()
        self.title("Portfolio Analyzer")

        models_data = ModelsData()
        self.data_models = models_data
        portfolio_data = PortfolioData()
        self.data_portfolio = portfolio_data

        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        icon_path = utilities.resource_path("images/Zephyr Analytics-Clipped.ico")
        self.iconbitmap(icon_path)

        # self.show_acknowledgment_popup()

        self.create_widgets()

    def show_acknowledgment_popup(self):
        """
        Shows the acknowledgment popup and disables the main window until acknowledged.
        """
        AcknowledgmentPopup(self)

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
        center_frame = ctk.CTkFrame(self, fg_color=["#edeaea", "#2b2c2d"])
        center_frame.grid(row=0, column=1, rowspan=1, sticky="nsew")

        # High-Level Tab Control
        self.high_level_tab_control = ctk.CTkTabview(
            center_frame,
            border_color=["#edeaea", "#2b2c2d"],
            fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_unselected_color="#bb8fce",
            segmented_button_selected_color="#8e44ad",
            text_color="#000000",
            segmented_button_selected_hover_color="#8e44ad",
            command=self.on_tab_switch
        )
        self.high_level_tab_control.pack(expand=1, fill="both")

        # # Add Economics Tab
        # economic_tab_frame = self.high_level_tab_control.add("Economics")
        # self.economic_tab = EconomicTab(economic_tab_frame)

        # Add Initial Testing Setup Tab
        setup_tab_frame = self.high_level_tab_control.add("Initial Testing Setup")
        self.setup_tab = SetupTab(setup_tab_frame, models_data=self.data_models, portfolio_data=self.data_portfolio)

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
        # if active_tab == "Economics":
        #     self.economic_tab.update_tab()
        if active_tab == "Initial Testing Setup":
            self.setup_tab.update_tab()
        elif active_tab == "Testing":
            self.testing_tab.update_tab()

def main():
    """
    Main entry point for the application.
    This function ensures that the GUI only runs in the main process.
    """
    app = PortfolioAnalyzer()
    app.mainloop()


if __name__ == "__main__":
    if multiprocessing.current_process().name == "MainProcess":
        multiprocessing.freeze_support()
        main()
