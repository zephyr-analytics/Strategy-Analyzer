"""
Module for acknowledgement window.
"""

import customtkinter as ctk
from PIL import Image, ImageTk

import strategy_analyzer.utilities as utilities


class AcknowledgmentPopup(ctk.CTkToplevel):
    """
    A popup window that requires the user to acknowledge before proceeding.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Acknowledgment Required")
        self.geometry("1000x800")

        self.grab_set()
        self.add_image()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.center_window()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        message = (
            "The Software may provide certain financial market data, quotes, price forecasts, other "
            "forecasts, news, research, predictions, and opinions or other financial information "
            "(collectively \"Information\") that has been independently obtained by certain financial "
            "market information services, financial and research publishers, various securities markets "
            "including stock exchanges and their affiliates, asset managers, investment bankers, and other "
            "providers (collectively the \"Information Providers\") or has been obtained by Zephyr Analytics "
            "from other sources, including computer algorithms that may include guessing or other sources of "
            "random information.\n\n"
            "All data and Information is provided \"as is\" and the Information is intended solely as general "
            "information for educational and entertainment purposes only and is neither professional "
            "stockbroker advice for any investment nor a substitute for other professional advice and services "
            "from qualified financial services providers familiar with your financial situation.\n\n"
            "Decisions based on Information contained within the Software are your sole responsibility. "
            "Always seek the advice of your financial advisor or other qualified financial services provider "
            "regarding any investment.\n\n"
            "The Information is provided with the understanding that Zephyr Analytics is not engaged in "
            "rendering professional services or advice and is not a registered investment advisor.\n\n"
            "Your use of the Software is subject to this disclaimer: Zephyr Analytics assumes no responsibility "
            "for any consequences relating directly or indirectly to any action or inaction you take based on "
            "the Information or other material on this Software.\n\n"
            "Zephyr Analytics does not guarantee or certify the accuracy, completeness, timeliness, or correct "
            "sequencing of the Information made available through Zephyr Analytics, the Information Providers, "
            "or any other third party transmitting the Information (the \"Information Transmitters\").\n\n"
            "You agree that Zephyr Analytics, the Information Providers, and the Information Transmitters shall "
            "not be liable in any way for the accuracy, completeness, timeliness, or correct sequencing of the "
            "Information, or for any decision made or action taken by you relying upon the Information.\n\n"
            "You further agree that Zephyr Analytics, the Information Providers, and the Information Transmitters "
            "will not be liable in any way for the interruption or cessation in the providing of any data, "
            "Information, or other aspect of the Software.\n\n"
            "Zephyr Analytics is not responsible for, and makes no warranties regarding, the access, speed, or "
            "availability of the Internet in general or the Software in particular.\n\n"
            "Zephyr Analytics reserves the right to modify or discontinue, temporarily or permanently, all or "
            "any portion of the Software with or without notice."
        )

        self.text_area = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Arial", 12),
            width=600,
            height=500
        )
        self.text_area.insert("1.0", message)
        self.text_area.configure(state="disabled")
        self.text_area.grid(row=1, column=0, padx=10, sticky="nsew")

        self.ack_button = ctk.CTkButton(
            self,
            text="I Acknowledge",
            command=self.on_acknowledge,
            fg_color="#8e44ad",
            hover_color="#bb8fce",
        )
        self.ack_button.grid(row=2, column=0, pady=10)

    def add_image(self):
        """
        Adds an image to the top of the popup and ensures it is larger using CTkImage for high-DPI displays.
        """
        image_path = utilities.resource_path("images/Zephyr Analytics-01.png")
        image = Image.open(image_path)

        # Create a CTkImage with the desired size
        self.ctk_image = ctk.CTkImage(image, size=(500, 200))  # Adjust the size as needed

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add the image label
        image_label = ctk.CTkLabel(self, image=self.ctk_image, text="", bg_color="black")
        image_label.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


    def center_window(self):
        """
        Centers the popup window on the parent window.
        """
        self.update_idletasks()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()

        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()

        x = parent_x + (parent_width // 2) - (popup_width // 2)
        y = parent_y + (parent_height // 2) - (popup_height // 2)

        self.geometry(f"+{x}+{y}")

    def on_acknowledge(self):
        """
        Handles the acknowledgment action and closes the popup.
        """
        self.grab_release()
        self.destroy()

    def on_close(self):
        """
        Handles the case where the user closes the popup without acknowledgment.
        """
        self.parent.destroy()
        self.destroy()
