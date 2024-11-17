def create_sidebars(self):
    """
    Creates shared sidebars that apply to all tabs.
    """
    # Left sidebar
    sidebar = ctk.CTkFrame(self, width=200)
    sidebar.grid(row=0, column=0, rowspan=4, sticky="ns", pady=(20, 0))

    ctk.CTkLabel(
        sidebar,
        text="Strategy Settings",
        font=ctk.CTkFont(
            size=20,
            weight="bold"
        )).pack(pady=(10, 5))

    ctk.CTkLabel(
        sidebar,
        text="Initial Portfolio Value:",
        font=self.bold_font).pack(pady=(0, 0)
    )

    ctk.CTkEntry(
        sidebar,
        textvariable=self.initial_portfolio_value_var).pack(pady=(0, 5)
    )
    self.initial_portfolio_value_var.trace_add("write", self.update_initial_portfolio_value)

    ctk.CTkLabel(sidebar, text="Start Date:", font=self.bold_font).pack(pady=(0, 0))
    ctk.CTkEntry(sidebar, textvariable=self.start_date_var).pack(pady=(0, 5))
    self.start_date_var.trace_add("write", self.update_start_date)

    ctk.CTkLabel(sidebar, text="End Date:", font=self.bold_font).pack(pady=(0, 0))
    ctk.CTkEntry(sidebar, textvariable=self.end_date_var).pack(pady=(0, 10))
    self.end_date_var.trace_add("write", self.update_end_date)

    ctk.CTkLabel(sidebar, text="Cash Ticker:", font=self.bold_font).pack(pady=(0, 0))
    ctk.CTkEntry(sidebar, textvariable=self.cash_ticker_var).pack(pady=(0, 5))
    self.cash_ticker_var.trace_add("write", self.update_cash_ticker)

    ctk.CTkLabel(sidebar, text="Bond Ticker:", font=self.bold_font).pack(pady=(0, 0))
    ctk.CTkEntry(sidebar, textvariable=self.bond_ticker_var).pack(pady=(0, 10))
    self.bond_ticker_var.trace_add("write", self.update_bond_ticker)

    ctk.CTkLabel(sidebar, text="Trading Frequency:", font=self.bold_font).pack(pady=(0, 0))
    trading_options = ["Monthly", "Bi-Monthly"]
    ctk.CTkOptionMenu(
        sidebar,
        values=trading_options,
        fg_color="#bb8fce",
        text_color="#000000",
        button_color="#8e44ad",
        button_hover_color="#8e44ad",
        variable=self.trading_frequency_var).pack(pady=(0, 10)
    )
    self.trading_frequency_var.trace_add("write", self.update_trading_frequency)

    ctk.CTkLabel(sidebar, text="Weighting Strategy:", font=self.bold_font).pack(pady=(0, 0))
    weighting_options = [
        "Use File Weights",
        "Equal Weight",
        "Risk Contribution",
        "Min Volatility",
        "Max Sharpe"
    ]
    ctk.CTkOptionMenu(
        sidebar,
        values=weighting_options,
        fg_color="#bb8fce",
        text_color="#000000",
        button_color="#8e44ad",
        button_hover_color="#8e44ad",
        variable=self.weighting_strategy_var).pack(pady=(0, 10)
    )
    self.weighting_strategy_var.trace_add("write", self.update_weighting_strategy)

    ctk.CTkLabel(sidebar, text="SMA Window (days):", font=self.bold_font).pack(pady=(0, 0))
    sma_windows = ["21", "42", "63", "84", "105", "126", "147", "168", "210"]

    ctk.CTkOptionMenu(
        sidebar,
        values=sma_windows,
        fg_color="#bb8fce",
        text_color="#000000",
        button_color="#8e44ad",
        button_hover_color="#8e44ad",
        variable=self.sma_window_var).pack(pady=(0, 10)
    )
    self.sma_window_var.trace_add("write", self.update_sma_window)

    ctk.CTkLabel(
        sidebar,
        text="Select portfolio assets:",
        font=self.bold_font).pack(pady=(0, 0)
    )
    ctk.CTkButton(
        sidebar,
        text="Select Asset Weights File",
        fg_color="#bb8fce",
        text_color="#000000",
        hover_color="#8e44ad",
        command=self.load_weights_and_update).pack(pady=(10, 10)
    )

    # Right sidebar
    right_sidebar = ctk.CTkFrame(self, width=200)
    right_sidebar.grid(row=0, column=2, rowspan=4, sticky="ns", pady=(20, 0))

    ctk.CTkLabel(right_sidebar, text="Theme Mode:", font=self.bold_font).pack(pady=(20, 0))
    theme_options = ["Light", "Dark"]
    ctk.CTkOptionMenu(
        right_sidebar,
        values=theme_options,
        fg_color="#bb8fce",
        text_color="#000000",
        button_color="#8e44ad",
        button_hover_color="#8e44ad",
        variable=self.theme_mode_var,
        command=self.change_theme).pack(pady=(0, 20), padx=(10, 10)
    )
    self.theme_mode_var.trace_add("write", self.update_theme_mode)

    ctk.CTkLabel(
        right_sidebar,
        text="Select out of market assets:",
        font=self.bold_font).pack(pady=(0, 0)
    )
    ctk.CTkButton(
        right_sidebar,
        text="Select Asset Weights File",
        fg_color="#bb8fce",
        text_color="#000000",
        hover_color="#8e44ad",
        command=self.load_out_of_market_weights_and_update).pack(pady=(10, 10)
    )

    ctk.CTkLabel(right_sidebar, text="Threshold Asset:", font=self.bold_font).pack(pady=(0, 0))
    ctk.CTkEntry(right_sidebar, textvariable=self.threshold_asset_entry_var).pack(pady=(0, 10))
    self.threshold_asset_entry_var.trace_add("write", self.update_threshold_asset)

    ctk.CTkLabel(
        right_sidebar,
        text="Number of assets to select:",
        font=self.bold_font).pack(pady=(0, 0)
    )
    ctk.CTkEntry(
        right_sidebar,
        textvariable=self.num_assets_to_select_entry_var
    ).pack(pady=(0, 10))
    self.num_assets_to_select_entry_var.trace_add("write", self.update_num_assets_to_select)