import customtkinter as ctk
import os
import threading
import webbrowser
from models_factory import ModelsFactory
from processing_types import *
import utilities as utilities


class TestingTab:
    """
    Handles the layout and functionality of the Testing tab.
    """

    def __init__(self, parent, data_models):
        self.parent = parent
        self.data_models = data_models
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")
        self.artifacts_directory = os.path.join(os.getcwd(), "artifacts")
        self.tab_run_vars = {}
        self.plot_var = None

        self.create_layout()

    def create_layout(self):
        """
        Creates the layout for the Testing tab with sub-tabs for different strategies.
        """
        self.testing_tab_control = ctk.CTkTabview(self.parent)
        self.testing_tab_control.pack(expand=1, fill="both")

        self._add_testing_tab("SMA Strategies")
        self._add_testing_tab("Momentum Strategies")
        self._add_testing_tab("Momentum In & Out Strategies")

    def _add_testing_tab(self, tab_name):
        """
        Adds a strategy-specific tab with dropdowns and action buttons.

        Parameters
        ----------
        tab_name : str
            The name of the tab to create.
        """
        tab = self.testing_tab_control.add(tab_name)

        ctk.CTkLabel(tab, text=f"{tab_name} Testing", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Dropdown for selecting run type
        self._add_run_type_dropdown(tab, tab_name)

        # Button to execute the selected run
        ctk.CTkButton(
            tab,
            text="Run",
            command=lambda: self.execute_task_for_tab(tab_name)
        ).pack(pady=10)

        # Dropdown for selecting and displaying plots
        self._add_plot_display_dropdown(tab)

    def _add_run_type_dropdown(self, tab, tab_name):
        """
        Adds a dropdown for selecting run types in a specific tab.

        Parameters
        ----------
        tab : ctk.CTkTabview
            The parent tab where the dropdown will be added.
        tab_name : str
            The name of the strategy tab.
        """
        if not hasattr(self, 'tab_run_vars'):
            self.tab_run_vars = {}
        self.tab_run_vars[tab_name] = ctk.StringVar(value="Select Run")

        ctk.CTkLabel(tab, text="Select Run Type:", font=ctk.CTkFont(size=14)).pack(pady=5)
        run_options = [run_type.name for run_type in Runs]

        ctk.CTkOptionMenu(
            tab,
            values=run_options,
            variable=self.tab_run_vars[tab_name]
        ).pack(pady=10)

    def _add_plot_display_dropdown(self, tab):
        """
        Adds a dropdown for selecting and displaying plots.

        Parameters
        ----------
        tab : ctk.CTkTabview
            The parent tab where the dropdown will be added.
        """
        ctk.CTkLabel(tab, text="Select Plot:", font=ctk.CTkFont(size=14)).pack(pady=10)

        plot_files = self.get_all_plot_files()
        self.plot_var = ctk.StringVar(value=plot_files[0] if plot_files else "No plots available")

        ctk.CTkOptionMenu(
            tab,
            values=plot_files if plot_files else ["No plots available"],
            variable=self.plot_var
        ).pack(pady=10)

        ctk.CTkButton(
            tab,
            text="Display Plot",
            command=self.update_plot_display
        ).pack(pady=10)

    def get_all_plot_files(self):
        """
        Fetches all .html plot files from the artifacts directory.

        Returns
        -------
        list
            A list of relative file paths to the .html plot files.
        """
        if not os.path.exists(self.artifacts_directory):
            os.makedirs(self.artifacts_directory)

        return [
            os.path.relpath(os.path.join(root, file), self.artifacts_directory)
            for root, _, files in os.walk(self.artifacts_directory)
            for file in files if file.endswith(".html")
        ]

    def update_plot_display(self):
        """
        Opens the selected plot file in the default web browser.
        """
        selected_plot = self.plot_var.get()
        file_path = os.path.join(self.artifacts_directory, selected_plot)

        if not os.path.exists(file_path):
            self._append_to_bottom_text(f"File not found: {file_path}")
            return

        webbrowser.open(f"file://{file_path}")

    def execute_task_for_tab(self, tab_name):
        """
        Executes the task for the selected strategy and run type.

        Parameters
        ----------
        tab_name : str
            The name of the selected tab.
        """
        selected_run = self.tab_run_vars[tab_name].get()

        tab_to_model_map = {
            "SMA Strategies": Models.SMA,
            "Momentum Strategies": Models.MOMENTUM,
            "Momentum In & Out Strategies": Models.IN_AND_OUT_OF_MARKET,
        }

        model_enum = tab_to_model_map.get(tab_name)
        run_enum = Runs[selected_run] if selected_run in Runs.__members__ else None

        if not model_enum or not run_enum:
            self._append_to_bottom_text("Invalid model or run type selection.")
            return

        threading.Thread(target=self._run_task, args=(model_enum, run_enum)).start()

    def _run_task(self, model, run_type):
        """
        Runs the specified model and run type in a separate thread.

        Parameters
        ----------
        model : Models
            The model to run.
        run_type : Runs
            The run type (e.g., BACKTEST, SIMULATION, SIGNALS).
        """
        try:
            factory = ModelsFactory(self.data_models)
            result = factory.run(model, run_type)
            self._append_to_bottom_text(result)
        finally:
            self.get_all_plot_files()

    def _append_to_bottom_text(self, message):
        """
        Appends a message to the bottom text area (if defined).

        Parameters
        ----------
        message : str
            The message to append.
        """
        if hasattr(self, "bottom_text_area"):
            self.bottom_text_area.insert("end", message + "\n")
            self.bottom_text_area.see("end")
