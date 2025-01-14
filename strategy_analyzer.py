"""
Parent module for GUI.
"""

import multiprocessing

import customtkinter as ctk

import strategy_analyzer.utilities as utilities
from strategy_analyzer.gui import *
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.results.models_results import ModelsResults


class StrategyAnalyzer(ctk.CTk):
    """
    A GUI application for running backtests and Monte Carlo simulations on investment portfolios.
    """
    def __init__(self):
        super().__init__()
        self.title("Strategy Analyzer")
        self.geometry("1920x1080")
        models_data = ModelsData()
        self.data_models = models_data
        portfolio_data = PortfolioData()
        self.data_portfolio = portfolio_data
        models_results = ModelsResults()
        self.results_models = models_results

        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        icon_path = utilities.resource_path("images/Zephyr Analytics-Clipped.ico")
        self.iconbitmap(icon_path)

        # self.show_acknowledgment_popup()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
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

        center_frame = ctk.CTkFrame(self, fg_color=["#edeaea", "#2b2c2d"])
        center_frame.grid(row=0, column=1, rowspan=1, columnspan=3, sticky="nsew")

        self.high_level_tab_control = ctk.CTkTabview(
            center_frame,
            border_color=["#edeaea", "#2b2c2d"],
            fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_unselected_color="#bb8fce",
            segmented_button_selected_color="#8e44ad",
            text_color="#000000",
            segmented_button_selected_hover_color="#8e44ad"
        )
        self.high_level_tab_control.pack(expand=1, fill="both", anchor="w")

        # multi_portfolio_tab_frame = self.high_level_tab_control.add("Multi Portfolio")
        # self.multi_portfolio_tab_control = ctk.CTkTabview(
        #     multi_portfolio_tab_frame,
        #     border_color=["#edeaea", "#2b2c2d"],
        #     fg_color=["#edeaea", "#2b2c2d"],
        #     segmented_button_fg_color=["#edeaea", "#2b2c2d"],
        #     segmented_button_unselected_color="#bb8fce",
        #     segmented_button_selected_color="#8e44ad",
        #     text_color="#000000",
        #     segmented_button_selected_hover_color="#8e44ad"
        # )
        # self.multi_portfolio_tab_control.pack(expand=1, fill="both", anchor="w")

        single_portfolio_tab_frame = self.high_level_tab_control.add("Single Portfolio")
        self.single_portfolio_tab_control = ctk.CTkTabview(
            single_portfolio_tab_frame,
            border_color=["#edeaea", "#2b2c2d"],
            fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_unselected_color="#bb8fce",
            segmented_button_selected_color="#8e44ad",
            text_color="#000000",
            segmented_button_selected_hover_color="#8e44ad"
        )
        self.single_portfolio_tab_control.pack(expand=1, fill="both", anchor="w")

        # setup_tab_frame = self.multi_portfolio_tab_control.add("Initial Testing Setup")
        # self.setup_tab = SetupTab(setup_tab_frame, models_data=self.data_models, portfolio_data=self.data_portfolio)

        # testing_tab_frame = self.multi_portfolio_tab_control.add("Testing")
        # self.testing_tab = TestingTab(
        #     testing_tab_frame,
        #     models_data=self.data_models,
        #     portfolio_data=self.data_portfolio,
        #     models_results=self.results_models
        # )

        setup_tab_frame_single = self.single_portfolio_tab_control.add("Initial Testing Setup")
        self.setup_tab_single = SetupTab(setup_tab_frame_single, models_data=self.data_models, portfolio_data=self.data_portfolio)

        testing_tab_frame_single = self.single_portfolio_tab_control.add("Testing")
        self.testing_tab_single = TestingTab(
            testing_tab_frame_single,
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )

        self.high_level_tab_control.set("Single Portfolio")

    def on_close(self):
        """
        Method for cleaning up when closing down the GUI.
        """
        print("Cleaning up resources...")
        self.data_models = None
        self.data_portfolio = None
        self.results_models = None
        self.quit()
        self.destroy()

def main():
    """
    Main entry point for the application.
    This function ensures that the GUI only runs in the main process.
    """
    app = StrategyAnalyzer()
    app.mainloop()


if __name__ == "__main__":
    if multiprocessing.current_process().name == "MainProcess":
        multiprocessing.freeze_support()
        main()
