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
        # self.geometry("1920x1080")

        models_data = ModelsData()
        self.data_models = models_data
        portfolio_data = PortfolioData()
        self.data_portfolio = portfolio_data
        models_results = ModelsResults()
        self.results_models = models_results

        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        icon_path = utilities.resource_path("images/Zephyr Analytics-Clipped.ico")
        self.iconbitmap(icon_path)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_top_frame()
        self.create_pages()
        self.create_navigation_menu()
        self.show_page("Strategy Analyzer Tools")

    def build_top_frame(self):
        """
        Builds the top frame with a title and navigation menu.
        """
        self.center_frame = ctk.CTkFrame(self, fg_color=["#edeaea", "#2b2c2d"])
        self.center_frame.grid(row=0, column=0, rowspan=10, columnspan=6, sticky="nsew", padx=10, pady=10)

        self.top_frame = ctk.CTkFrame(self.center_frame, fg_color=["#bb8fce", "#bb8fce"])
        self.top_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.top_frame, text="Strategy Analyzer", font=self.bold_font, anchor="w"
        ).grid(row=0, column=0, padx=10, pady=5)

        spacer = ctk.CTkFrame(self.top_frame, fg_color=["#bb8fce", "#bb8fce"], width=1)
        spacer.grid(row=0, column=1, sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)

    def create_pages(self):
        """
        Creates the pages for the application and stores them in a dictionary.
        """
        self.pages = {}

        # Loading Page
        self.pages["Strategy Analyzer Tools"] = ctk.CTkFrame(self.center_frame, fg_color=["#edeaea", "#2b2c2d"])
        self.pages["Strategy Analyzer Tools"].grid(row=1, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        self.setup_tab_single = LoadingPage(
            self.pages["Strategy Analyzer Tools"],
            models_data=self.data_models,
            portfolio_data=self.data_portfolio
        )

        # Initial Testing Setup Page
        self.pages["Initial Testing Setup"] = ctk.CTkFrame(self.center_frame, fg_color=["#edeaea", "#2b2c2d"])
        self.pages["Initial Testing Setup"].grid(row=1, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        self.setup_tab_single = SetupTab(
            self.pages["Initial Testing Setup"],
            models_data=self.data_models,
            portfolio_data=self.data_portfolio
        )

        # Testing Page
        self.pages["Testing"] = ctk.CTkFrame(self.center_frame, fg_color=["#edeaea", "#2b2c2d"])
        self.pages["Testing"].grid(row=1, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        self.testing_tab_single = TestingTab(
            self.pages["Testing"],
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )

        # Initially hide all pages
        for page in self.pages.values():
            page.grid_forget()

    def create_navigation_menu(self):
        """
        Creates the navigation menu on the top-right of the top frame.
        """
        nav_menu_frame = ctk.CTkFrame(self.top_frame, fg_color=["#bb8fce", "#bb8fce"])
        nav_menu_frame.grid(row=0, column=5, sticky="e", padx=10, pady=5)

        ctk.CTkButton(
            nav_menu_frame,
            text="Initial Testing Setup",
            command=lambda: self.show_page("Initial Testing Setup"),
            fg_color="#8e44ad",
            hover_color="#bb8fce"
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            nav_menu_frame,
            text="Testing",
            command=lambda: self.show_page("Testing"),
            fg_color="#8e44ad",
            hover_color="#bb8fce"
        ).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkButton(
            nav_menu_frame,
            text="Strategy Analyzer Tools",
            command=lambda: self.show_page("Strategy Analyzer Tools"),
            fg_color="#8e44ad",
            hover_color="#bb8fce"
        ).grid(row=0, column=0, padx=5, pady=5)

    def show_page(self, page_name):
        """
        Displays the specified page and hides all other pages.
        """
        for name, page in self.pages.items():
            if name == page_name:
                page.grid()
            else:
                page.grid_forget()

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
