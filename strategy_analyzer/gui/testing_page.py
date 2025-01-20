"""
Module for creating the testing page.
"""

import os
import threading

import customtkinter as ctk

from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.models.models_factory import ModelsFactory
from strategy_analyzer.processing_types import *
from strategy_analyzer.results.models_results import ModelsResults


class TestingTab:
    """
    Handles the layout and functionality of the Testing tab.
    """
    def __init__(self, parent, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results

        self.parent = parent
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        self.theme_mode_var = ctk.StringVar(value=self.data_models.theme_mode)
        self.create_widgets()


    def create_widgets(self):
        """
        Method for creating widgets and packing them to the canvas.
        """
        center_frame = ctk.CTkFrame(self.parent, fg_color=["#edeaea", "#2b2c2d"])
        center_frame.pack()

        self.high_level_tab_control = ctk.CTkTabview(center_frame, fg_color=["#edeaea", "#2b2c2d"])
        self.high_level_tab_control.pack(expand=True, fill="both")

        self.create_testing_tabs(self.high_level_tab_control)

        self.bottom_text_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.bottom_text_frame.pack()

        # self.bottom_text = ctk.CTkFrame(self.bottom_text_frame)
        # self.bottom_text.pack()

        self.bottom_text_result_display = ctk.CTkLabel(self.bottom_text_frame)
        self.bottom_text_result_display.pack()

        copyright_label = ctk.CTkLabel(
            self.parent,
            text="© Zephyr Analytics 2025",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack()


    def create_testing_tabs(self, parent):
        """
        Creates the Testing tab with sub-tabs for SMA, Momentum, etc.

        Parameters
        ----------
        parent : CTKFrame
            The parent window of all tabs and frames.
        """
        self.testing_tab_control = ctk.CTkTabview(
            parent,
            border_color=["#edeaea", "#2b2c2d"],
            fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_fg_color=["#edeaea", "#2b2c2d"],
            segmented_button_unselected_color="#bb8fce",
            segmented_button_selected_color="#8e44ad",
            text_color="#000000",
            segmented_button_selected_hover_color="#8e44ad",
        )

        self.testing_tab_control.grid(row=0, column=0, sticky="nsew")

        self.create_testing_tab("Moving Average Strategies")
        self.create_testing_tab("Momentum Strategies")
        self.create_testing_tab("Momentum In & Out Strategies")
        self.create_testing_tab("Moving Average Crossover Strategies")
        self.create_testing_tab("Machine Learning")


    def create_testing_tab(self, tab_name):
        """
        Creates a single tab with a dropdown menu for selecting Runs enum values
        and integrates plot display functionality.

        Parameters
        ----------
        tab_name : str
            The name of the tab to create.
        """
        tab = self.testing_tab_control.add(tab_name)

        ctk.CTkLabel(
            tab,
            fg_color="transparent",
            text=f"{tab_name} Testing",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)

        if not hasattr(self, 'tab_run_vars'):
            self.tab_run_vars = {}
        self.tab_run_vars[tab_name] = ctk.StringVar(value="Select Run")

        ctk.CTkLabel(
            tab,
            text="Select Run Type:",
            font=ctk.CTkFont(size=14),
        ).pack(pady=5)

        run_options = [run_type.name for run_type in Runs]
        run_dropdown = ctk.CTkOptionMenu(
            tab,
            fg_color="#bb8fce",
            text_color="#000000",
            button_color="#8e44ad",
            button_hover_color="#8e44ad",
            values=run_options,
            variable=self.tab_run_vars[tab_name],
        )
        run_dropdown.pack(pady=10)

        ctk.CTkButton(
            tab,
            text="Run",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=lambda: self.execute_task_for_tab(tab_name),
        ).pack(pady=10)

        ctk.CTkButton(
            tab,
            text="Open Plots Directory",
            fg_color="#bb8fce",
            text_color="#000000",
            hover_color="#8e44ad",
            command=self.open_artifacts_directory,
        ).pack(pady=50)


    def execute_task_for_tab(self, tab_name: str):
        """
        Executes the task based on the selected tab and run type.

        Parameters
        ----------
        tab_name : str
            The name of the tab selected (e.g., "SMA Strategies").
        """
        selected_run = self.tab_run_vars[tab_name].get()

        tab_to_model_map = {
            "Moving Average Strategies": Models.MA,
            "Momentum Strategies": Models.MOMENTUM,
            "Momentum In & Out Strategies": Models.IN_AND_OUT_OF_MARKET,
            "Moving Average Crossover Strategies": Models.MA_CROSSOVER,
            "Machine Learning": Models.MACHINE_LEARNING
        }

        model_enum = tab_to_model_map.get(tab_name)
        run_enum = Runs[selected_run] if selected_run in Runs.__members__ else None

        if not model_enum or not run_enum:
            self.display_result("Invalid model or run type selection.")
            return

        threading.Thread(
            target=self._run_task,
            args=(model_enum, run_enum),
        ).start()


    def _run_task(self, model, run_type):
        """
        Generic task runner for executing a specific model and run type in a separate thread.

        Parameters
        ----------
        model : Models
            The model to run (e.g., Models.SMA).
        run_type : Runs
            The run type (e.g., Runs.BACKTEST, Runs.SIMULATION, Runs.SIGNALS).
        """
        self.clear_message_text()
        try:
            factory = ModelsFactory(
                models_data=self.data_models,
                portfolio_data=self.data_portfolio,
                models_results=self.results_models
            )
            result = factory.run(model, run_type)
            self.parent.after(0, lambda: self.display_result(result))
        finally:
            pass

    def open_artifacts_directory(self):
        """
        Opens the artifacts plot directory on Windows.
        """
        path = os.path.join(os.getcwd(), "artifacts", self.data_models.weights_filename)
        artifacts_dir = path

        try:
            os.startfile(artifacts_dir)
        except Exception as e:
            print(f"Error opening directory: {e}")

    def change_theme(self, selected_theme):
        """
        Changes the theme of the application based on user selection.

        Parameters
        ----------
        selected_theme : str
            The selected theme mode, either "Light" or "Dark".
        """
        ctk.set_appearance_mode(selected_theme)


    def clear_message_text(self):
        """
        Clears the text in the bottom text area.
        """
        self.bottom_text_result_display.destroy()


    # def clear_bottom_text(self):
    #     """
    #     Clears the text at the bottom of the GUI.

    #     Parameters
    #     ----------
    #     None
    #     """
    #     self.bottom_text.destroy()


    # def display_asset_weights(self):
    #     """
    #     Displays the loaded asset weights in the GUI, capped at 10.
    #     """
    #     assets_text = "\n".join(
    #         [f"{asset}: {weight}" for asset, weight in list(self.data_models.assets_weights.items())[:10]]
    #     )
    #     if len(self.data_models.assets_weights) > 10:
    #         assets_text += f"\n... (and {(len(self.data_models.assets_weights)-10)} more)"

    #     self.bottom_text = ctk.CTkLabel(
    #         self.bottom_text_frame,
    #         text=f"Loaded Assets and Weights from: \n\n{self.data_models.weights_filename}:\n{assets_text}",
    #         font=self.bold_font,
    #         fg_color="transparent"
    #     )
    #     self.bottom_text.pack(pady=5)


    def display_result(self, result: str):
        """
        Displays the result of a task in the GUI.

        Parameters
        ----------
        result : str
            The result text to be displayed in the GUI.
        """
        self.bottom_text_result_display = ctk.CTkLabel(
            self.bottom_text_frame,
            text=result, text_color="green" if "completed" in result else "red",
            fg_color="transparent",
        )
        self.bottom_text_result_display.pack(pady=5)


    # def update_tab(self):
    #     """
    #     Method used by GUI to update tab components.
    #     """
    #     self.clear_bottom_text()
    #     self.clear_message_text()
    #     self.display_asset_weights()
