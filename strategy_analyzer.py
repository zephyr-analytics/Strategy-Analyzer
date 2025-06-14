"""
Parent module for GUI.
"""

import multiprocessing

import customtkinter as ctk
from PIL import Image

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
        self.resizable(False, False)

        models_data = ModelsData()
        self.data_models = models_data
        portfolio_data = PortfolioData()
        self.data_portfolio = portfolio_data
        models_results = ModelsResults()
        self.results_models = models_results
        self.theme_mode_var = ctk.StringVar(value="Light")

        self.pages = {}
        self.bold_font = ctk.CTkFont(size=14, weight="bold", family="Arial")
        self.text_font = ctk.CTkFont(size=14, family="Arial")
        self.label_font = ctk.CTkFont(size=26, family="Copperplate Gothic Bold")
        self.title_font = ctk.CTkFont(size=20, family="Copperplate Gothic Bold")

        icon_path = utilities.resource_path("images/Zephyr Analytics-Clipped.ico")
        self.iconbitmap(icon_path)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.process()

    def process(self):
        """
        """
        # self.show_acknowledgment_popup()
        self.build_top_frame()
        self.create_strategy_analyzer_tools_page()
        self.create_individual_pages()
        self.create_navigation_menu()
        self.build_bottom_frame()
        self.show_page("Strategy Analyzer Tools")

    def show_acknowledgment_popup(self):
        """
        Shows the acknowledgment popup and disables the main window until acknowledged.
        """
        AcknowledgmentPopup(self)

    def build_top_frame(self):
        """
        Builds the top frame with a title and a large image using CTkImage for high-DPI displays.
        """
        self.center_frame = ctk.CTkFrame(self, fg_color=["#edeaea", "#2b2c2d"])
        self.center_frame.grid(row=0, column=0, sticky="nsew")

        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)

        self.top_frame = ctk.CTkFrame(self.center_frame, fg_color=["black", "black"])
        self.top_frame.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)

        self.top_frame.grid_columnconfigure(0, weight=1)

        image_path = utilities.resource_path("images/Zephyr Analytics-01.png")
        image = Image.open(image_path)

        self.ctk_image = ctk.CTkImage(image, size=(300, 100))

        image_label = ctk.CTkLabel(self.top_frame, image=self.ctk_image, text="", bg_color="black")
        image_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        title_label = ctk.CTkLabel(
            self.top_frame, text="Strategy Analyzer", font=self.label_font, anchor="center", text_color="white",
        )
        title_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")


    def create_strategy_analyzer_tools_page(self):
        """
        Creates the Strategy Analyzer Tools page and sets it as the main page.
        """
        page_name = "Strategy Analyzer Tools"
        page_frame = ctk.CTkFrame(self.center_frame, fg_color=["#edeaea", "#2b2c2d"])
        page_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        page_frame.grid_rowconfigure(0, weight=1)
        page_frame.grid_rowconfigure(1, weight=1)
        page_frame.grid_rowconfigure(2, weight=1)
        page_frame.grid_columnconfigure(0, weight=1)
        page_frame.grid_columnconfigure(1, weight=1)

        self.create_section(
            page_frame, "Backtest Portfolio", 0, 0,
            "Backtest a portfolio asset allocation and compare historical and realized returns and risk characteristics against various lazy portfolios.",
            "Backtest Portfolio"
        )
        self.create_section(
            page_frame, "Tactical Asset Allocation", 0, 1,
            "Compare and test tactical allocation models based on moving averages, momentum, market valuation, and volatility targeting.",
            "Tactical Asset Allocation"
        )
        self.create_section(
            page_frame, "Monte Carlo Simulation", 1, 0,
            "Run Monte Carlo simulations for the specified portfolio based on historical or forecasted returns to test long-term expected portfolio growth and survival, and the capability to meet financial goals and liabilities.",
            "Monte Carlo Simulation"
        )
        self.create_section(
            page_frame, "Signals Creation", 1, 1,
            "Generate the latest trading signals based on the trading model.",
            "Signals Creation"
        )
        self.create_section(
            page_frame, "Strategy Analysis", 2, 0,
            "Analyze the performance and characteristics of investment strategies.",
            "Strategy Analysis"
        )
        self.create_section(
            page_frame, "Asset Analytics", 2, 1,
            "Coming Soon!",
            "Asset Analytics"
        )

        self.pages[page_name] = page_frame

    def create_individual_pages(self):
        """
        Creates individual pages using imported page classes.
        """
        self.pages["Backtest Portfolio"] = BackTestingPage(
            parent=self.center_frame,
            controller=self,
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        self.pages["Tactical Asset Allocation"] = TacticalAssetPage(
            parent=self.center_frame,
            controller=self,
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        self.pages["Monte Carlo Simulation"] = MonteCarloSimPage(
            parent=self.center_frame,
            controller=self,
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        self.pages["Signals Creation"] = SignalsCreationPage(
            parent=self.center_frame,
            controller=self,
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        self.pages["Strategy Analysis"] = StrategyAnalysisPage(
            parent=self.center_frame,
            controller=self,
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        # self.pages["Asset Analytics"] = AssetAnalyticsPage(self.center_frame, self)

        for page in self.pages.values():
            page.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            page.grid_remove()

    def create_section(self, parent, title, row, col, description, page_name):
        """
        Helper function to create a section with a title, description, and button.
        """
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        section_frame.grid_rowconfigure(2, weight=1)
        section_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(section_frame, text=title, font=self.title_font).grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        ctk.CTkLabel(
            section_frame, text=description, wraplength=400, font=self.text_font,
        ).grid(row=1, column=0, sticky="nsew")
        ctk.CTkButton(
            section_frame,
            text=f"Open {title}",
            fg_color="#8e44ad",
            hover_color="#bb8fce",
            command=lambda: self.show_page(page_name)
        ).grid(row=2, column=0, pady=(5, 0))

    def create_navigation_menu(self):
        """
        Creates the navigation menu on the top-right of the top frame with horizontal buttons.
        """
        nav_menu_frame = ctk.CTkFrame(self.top_frame, fg_color=["black", "black"])
        nav_menu_frame.grid(row=0, column=5, sticky="e", padx=10, pady=5)

        nav_menu_frame.grid_rowconfigure(0, weight=1)
        nav_menu_frame.grid_columnconfigure((0, len(self.pages) - 1), weight=1)

        for i, page_name in enumerate(self.pages.keys()):
            ctk.CTkButton(
                nav_menu_frame,
                text=page_name,
                command=lambda name=page_name: self.show_page(name),
                fg_color="#8e44ad",
                hover_color="#bb8fce"
            ).grid(row=0, column=i, sticky="ew", padx=5, pady=5)

        mode_dropdown = ctk.CTkOptionMenu(
            nav_menu_frame,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            values=["Light", "Dark"],
            variable=self.theme_mode_var,
            command=self.update_theme_mode
        )
        mode_dropdown.grid(row=0, column=7, sticky="ew", padx=5, pady=5)

    def build_bottom_frame(self):
        """
        """
        footer_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        footer_frame.grid(row=3, column=0, columnspan=6)
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© Zephyr Analytics 2025",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.grid(row=0, column=0)
    
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

    def show_page(self, page_name):
        """
        Displays the specified page and hides all other pages.
        """
        for name, page in self.pages.items():
            if name == page_name:
                page.grid()
            else:
                page.grid_remove()

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
    """
    app = StrategyAnalyzer()
    app.mainloop()


if __name__ == "__main__":
    if multiprocessing.current_process().name == "MainProcess":
        multiprocessing.freeze_support()
        main()
