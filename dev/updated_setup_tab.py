import customtkinter as ctk
import utilities as utilities


class SetupTab:
    """
    Handles the layout and functionality of the Initial Testing Setup tab.
    """

    def __init__(self, parent, data_models):
        self.parent = parent
        self.data_models = data_models
        self.bold_font = ctk.CTkFont(size=12, weight="bold", family="Arial")

        # Variables for data binding
        self._initialize_variables()
        self.create_layout()

    def _initialize_variables(self):
        """
        Initializes the StringVars for binding to the GUI.
        """
        self.start_date_var = ctk.StringVar(value=self.data_models.start_date)
        self.end_date_var = ctk.StringVar(value=self.data_models.end_date)
        self.cash_ticker_var = ctk.StringVar(value=self.data_models.cash_ticker)
        self.bond_ticker_var = ctk.StringVar(value=self.data_models.bond_ticker)
        self.trading_frequency_var = ctk.StringVar(value=self.data_models.trading_frequency)
        self.sma_window_var = ctk.StringVar(value=self.data_models.sma_window)
        self.num_simulations_var = ctk.StringVar(value=self.data_models.num_simulations)
        self.simulation_horizon_var = ctk.StringVar(value=self.data_models.simulation_horizon)
        self.initial_portfolio_value_var = ctk.StringVar(value=self.data_models._initial_portfolio_value)
        self.threshold_asset_var = ctk.StringVar(value=self.data_models._threshold_asset)
        self.num_assets_to_select_var = ctk.StringVar(value=self.data_models._num_assets_to_select)

    def create_layout(self):
        """
        Creates the layout for the Initial Testing Setup tab.
        """
        self._create_header()
        self._create_section("Data Settings", self._data_settings, padx=10, pady=10)
        self._create_section("SMA Settings", self._sma_settings, padx=10, pady=10)
        self._create_section("Momentum Settings", self._momentum_settings, padx=10, pady=10)
        self._create_section("Monte Carlo Settings", self._monte_carlo_settings, padx=10, pady=10)
        self._create_footer()

    def _create_header(self):
        """
        Creates the header section of the tab.
        """
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20), padx=10)

        ctk.CTkLabel(
            header_frame,
            text="Welcome to Portfolio Analyzer by Zephyr Analytics.",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="center"
        ).pack(pady=10)

        ctk.CTkLabel(
            header_frame,
            text="Configure your portfolio settings below.",
            wraplength=800,
            font=ctk.CTkFont(size=14),
            anchor="center"
        ).pack()

    def _create_section(self, title, content_function, **kwargs):
        """
        Creates a section with a title and content.

        Parameters
        ----------
        title : str
            The section title.
        content_function : function
            The function to populate the section content.
        **kwargs : dict
            Additional arguments for the section frame.
        """
        frame = ctk.CTkFrame(self.parent, fg_color="#f5f5f5")
        frame.pack(fill="x", **kwargs)

        ctk.CTkLabel(frame, text=title, font=self.bold_font).pack(pady=5)
        content_function(frame)

    def _data_settings(self, frame):
        """
        Populates the Data Settings section.
        """
        self._add_label_entry_row(frame, "Start Date:", self.start_date_var, row=0)
        self._add_label_entry_row(frame, "End Date:", self.end_date_var, row=1)
        self._add_label_entry_row(frame, "Cash Ticker:", self.cash_ticker_var, row=2)
        self._add_label_entry_row(frame, "Bond Ticker:", self.bond_ticker_var, row=3)

        ctk.CTkLabel(frame, text="Trading Frequency:", font=self.bold_font).grid(row=4, column=0, sticky="e", padx=5)
        ctk.CTkOptionMenu(
            frame,
            values=["Monthly", "Bi-Monthly"],
            variable=self.trading_frequency_var
        ).grid(row=4, column=1, sticky="ew", padx=5)

        ctk.CTkButton(
            frame,
            text="Select Asset Weights File",
            command=self.load_weights_and_update
        ).grid(row=5, column=1, sticky="e", padx=5)

    def _sma_settings(self, frame):
        """
        Populates the SMA Settings section.
        """
        ctk.CTkLabel(frame, text="SMA Window (days):", font=self.bold_font).grid(row=0, column=0, sticky="e", padx=5)
        ctk.CTkOptionMenu(
            frame,
            values=["21", "42", "63", "84", "105", "126", "147", "168", "210"],
            variable=self.sma_window_var
        ).grid(row=0, column=1, sticky="ew", padx=5)

    def _momentum_settings(self, frame):
        """
        Populates the Momentum Settings section.
        """
        self._add_label_entry_row(frame, "Threshold Asset:", self.threshold_asset_var, row=0)
        self._add_label_entry_row(frame, "Number of Assets to Select:", self.num_assets_to_select_var, row=1)

        ctk.CTkButton(
            frame,
            text="Select Out of Market Assets",
            command=self.load_out_of_market_weights_and_update
        ).grid(row=2, column=1, sticky="ew", padx=5)

    def _monte_carlo_settings(self, frame):
        """
        Populates the Monte Carlo Settings section.
        """
        self._add_label_entry_row(frame, "Simulation Horizon:", self.simulation_horizon_var, row=0)
        self._add_label_entry_row(frame, "Number of Simulations:", self.num_simulations_var, row=1)

    def _create_footer(self):
        """
        Creates the footer section with a Proceed button.
        """
        footer_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=20)

        ctk.CTkButton(
            footer_frame,
            text="Proceed to Testing Tab",
            command=lambda: self.parent.master.high_level_tab_control.set("Testing")
        ).pack(pady=20)

    def _add_label_entry_row(self, frame, label_text, variable, row):
        """
        Adds a label and entry field in a row.

        Parameters
        ----------
        frame : ctk.CTkFrame
            The parent frame.
        label_text : str
            The text for the label.
        variable : ctk.StringVar
            The variable to bind to the entry field.
        row : int
            The grid row for placement.
        """
        ctk.CTkLabel(frame, text=label_text, font=self.bold_font).grid(row=row, column=0, sticky="e", padx=5)
        ctk.CTkEntry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=5)

    # Data-Related Methods
    def load_weights_and_update(self):
        self.data_models.assets_weights, self.data_models.weights_filename = utilities.load_weights()

    def load_out_of_market_weights_and_update(self):
        self.data_models.out_of_market_tickers, _ = utilities.load_weights()

    # Variable Update Methods
    def update_start_date(self, *args): self.data_models.start_date = self.start_date_var.get()
    def update_end_date(self, *args): self.data_models.end_date = self.end_date_var.get()
    def update_cash_ticker(self, *args): self.data_models.cash_ticker = self.cash_ticker_var.get()
    def update_bond_ticker(self, *args): self.data_models.bond_ticker = self.bond_ticker_var.get()
    def update_trading_frequency(self, *args): self.data_models.trading_frequency = self.trading_frequency_var.get()
    def update_sma_window(self, *args): self.data_models.sma_window = self.sma_window_var.get()
    def update_num_simulations(self, *args): self.data_models.num_simulations = int(self.num_simulations_var.get())
    def update_simulation_horizon(self, *args): self.data_models.simulation_horizon = int(self.simulation_horizon_var.get())
    def update_threshold_asset(self, *args): self.data_models.threshold_asset = self.threshold_asset_var.get()
    def update_num_assets_to_select(self, *args): self.data_models.num_assets_to_select = self.num_assets_to_select_var.get()
