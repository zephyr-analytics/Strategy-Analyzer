"""
Module for creating the portfolio page.
"""

import customtkinter as ctk
import utilities as utilities
from portfolio_management.portfolio_data import PortfolioData


class PortfolioTab:
    """
    Handles the layout and functionality of the Portfolio Aggregator parent.
    """

    def __init__(self, parent, portfolio_data: PortfolioData):
        self.data_portfolios = portfolio_data
        self.parent = parent
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")
        self.bottom_text_frame = ctk.CTkFrame(self.parent)
        self.upload_status_label = None
        self.create_initial_tab(self.parent)

    def create_initial_tab(self, parent):
        """
        Creates the Portfolio Aggregator tab with inputs for portfolio selection.

        Parameters
        ----------
        parent : ctk.CTkFrame
            The frame for the Portfolio Aggregator tab.
        """
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20), padx=10)

        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header_frame,
            text="Welcome to Portfolio Aggregator by Zephyr Analytics.",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="center"
        ).grid(row=0, column=0, pady=10, sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text="Configure your portfolio settings below.",
            wraplength=800,
            font=ctk.CTkFont(size=14),
            anchor="center"
        ).grid(row=1, column=0, pady=10, sticky="ew")

        # Data Settings Section
        data_frame = ctk.CTkFrame(parent, fg_color="#f5f5f5")
        data_frame.pack(fill="x", pady=10, padx=10)

        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            data_frame,
            text="Select first portfolio to aggregate:",
            font=self.bold_font).grid(row=5, column=0, sticky="e", padx=5
        )

        ctk.CTkButton(
            data_frame,
            text="Select First Portfolio File",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.load_portfolio_and_update
        ).grid(row=5, column=1, sticky="w", padx=5)

        # Status label for upload
        self.upload_status_label = ctk.CTkLabel(
            data_frame,
            text="No file uploaded yet.",
            font=self.bold_font,
            text_color="blue"
        )
        self.upload_status_label.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

        # Footer Section
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=20)

        copyright_label = ctk.CTkLabel(
            self.parent,
            text="© Zephyr Analytics 2024",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack()

    def load_portfolio_and_update(self):
        """
        Loads the first portfolio from a file and updates the status label.
        """
        self.clear_bottom_text()
        portfolio_data = utilities.load_portfolio()
        self.data_portfolios.portfolio_dataframe = portfolio_data
        # print(portfolio_data)

    def clear_bottom_text(self):
        """
        Clears the text at the bottom of the GUI.
        """
        for widget in self.bottom_text_frame.winfo_children():
            widget.destroy()

    def update_tab(self):
        """
        Method used by GUI to update tab components.
        """
        pass
