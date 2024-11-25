"""
Module for creating the economic page.
"""

import datetime
import logging

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data as pdr


class EconomicTab:
    def __init__(self, parent):
        self.parent = parent
        self.configure_widgets(self.parent)
        self.update_economic_data()  # Automatically fetch and display economic data
        self.update_plot()  # Automatically load the plot on app start

    def configure_widgets(self, parent):
        """
        Configures the widgets and layout for the EconomicTab using customtkinter.
        """
        # Header Section for Economic Data
        self.header_frame = ctk.CTkFrame(parent)
        self.header_frame.pack(fill="x", pady=10)

        # Labels for headers
        self.current_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.current_row.pack(fill="x", pady=2)
        self.previous_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.previous_row.pack(fill="x", pady=2)

        # Labels for economic data
        self.data_fields = {"current": {}, "previous": {}}
        self.economic_metrics = {
            "GDP": "GDP",  # Real Gross Domestic Product
            "Unemployment Rate": "UNRATE",  # Unemployment Rate
            "Initial Jobless Claims": "ICSA",  # Initial Claims
            "Inflation Rate": "STICKCPIM159SFRBATL",  # Sticky Price CPI (Atlanta Fed)
            "Federal Funds Rate": "FEDFUNDS",  # Federal Funds Effective Rate
        }

        # Metrics where lower values are positive (opposite scale)
        self.opposite_scale_metrics = {"Unemployment Rate", "Initial Jobless Claims", "Inflation Rate"}

        # Add data labels dynamically
        for metric, series_id in self.economic_metrics.items():
            # Current Data Point Row
            c_label = ctk.CTkLabel(self.current_row, text=f"{metric} (Current):", font=("Arial", 16, "bold"))
            c_value_label = ctk.CTkLabel(self.current_row, text="Loading...", font=("Arial", 16, "bold"))
            c_label.pack(side="left", padx=(10, 5))
            c_value_label.pack(side="left", padx=(0, 20))
            self.data_fields["current"][metric] = c_value_label

            # Previous Data Point Row
            p_label = ctk.CTkLabel(self.previous_row, text=f"{metric} (Previous):", font=("Arial", 16, "italic"))
            p_value_label = ctk.CTkLabel(self.previous_row, text="Loading...", font=("Arial", 16, "italic"))
            p_label.pack(side="left", padx=(10, 5))
            p_value_label.pack(side="left", padx=(0, 20))
            self.data_fields["previous"][metric] = p_value_label

        # Matplotlib Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        # Error Label
        self.error_label = ctk.CTkLabel(parent, text="", text_color="red", font=("Arial", 12))
        self.error_label.pack(pady=5)

    def fetch_economic_data(self, series_id):
        """
        Fetches the latest and previous available values for a specific economic series from FRED.
        """
        try:
            data = pdr.DataReader(series_id, "fred", datetime.datetime.now() - datetime.timedelta(days=365))
            latest = data.iloc[-1].values[0]  # Most recent value
            previous = data.iloc[-2].values[0]  # Second most recent value
            return latest, previous
        except Exception as e:
            logging.error(f"Error fetching data for {series_id}: {e}")
            return None, None

    def format_value(self, metric, value):
        """
        Formats the value based on the metric type.
        """
        if value is None:
            return "N/A"

        if metric in ["Federal Funds Rate", "Unemployment Rate", "Inflation Rate"]:
            return f"{value:.2f}%"  # Format as percentage
        elif metric == "Initial Jobless Claims":
            return f"{int(value):,}"  # Format with commas for thousands
        elif metric == "GDP":
            return f"${value:,.0f}B"  # Format as billions
        else:
            return f"{value}"

    def apply_color(self, metric, latest, previous):
        """
        Determines the color based on whether the value has increased or decreased.
        """
        if latest is None or previous is None or latest == previous:
            return "black"  # Default color for unavailable data or no change

        if metric == "Federal Funds Rate":
            return "black"  # Always black for Fed Funds Rate

        if metric in self.opposite_scale_metrics:
            # Opposite scale: green for decrease, red for increase
            return "#006400" if latest < previous else "#8B0000"
        else:
            # Regular scale: green for increase, red for decrease
            return "#006400" if latest > previous else "#8B0000"


    def update_economic_data(self):
        """
        Fetches and updates the economic data fields for both current and previous values.
        """
        for metric, series_id in self.economic_metrics.items():
            latest, previous = self.fetch_economic_data(series_id)
            formatted_latest = self.format_value(metric, latest)
            formatted_previous = self.format_value(metric, previous)

            # Apply dynamic coloring based on the change
            color = self.apply_color(metric, latest, previous)
            self.data_fields["current"][metric].configure(text=f"{formatted_latest}", text_color=color)
            self.data_fields["previous"][metric].configure(text=f"{formatted_previous}")

    def fetch_yield_curve_data(self, date):
        """
        Fetches yield curve data from the FRED database for a specific date range.
        """
        series = [
            "DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2",
            "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"
        ]
        start_date = date - datetime.timedelta(days=7)  # Use a week window to ensure data availability
        end_date = date

        try:
            data = pdr.DataReader(series, "fred", start_date, end_date)
            return data.iloc[-1].dropna()  # Get the most recent data and drop NaNs
        except Exception as e:
            raise ValueError(f"No data available for {date.strftime('%Y-%m-%d')}") from e

    def process_yields(self, yields):
        """
        Processes yield data into maturities and rates for plotting.
        """
        maturities = [
            int(s.lstrip('DGS').replace('MO', '')) / 12 if 'MO' in s else int(s.lstrip('DGS'))
            for s in yields.index
        ]
        rates = yields.values
        return maturities, rates

    def plot_yield_curve(self, yield_data):
        """
        Plots the yield curve for multiple time points with customized styles.
        """
        self.ax.clear()

        for date_label, yields, color, style, linewidth in yield_data:
            maturities, rates = self.process_yields(yields)
            self.ax.plot(maturities, rates, marker='o', linestyle=style, linewidth=linewidth, label=date_label, color=color)

        # Chart formatting
        self.ax.set_title("U.S. Treasury Yield Curve", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Maturity (Years)", fontsize=12)
        self.ax.set_ylabel("Yield (%)", fontsize=12)
        self.ax.legend()
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.tick_params(axis='both', labelsize=10)

        self.canvas.draw()

    def update_plot(self):
        """
        Updates the plot with yield curve data for today, one month ago, six months ago, and one year ago.
        """
        today = datetime.datetime.now()
        time_points = [
            ("Today", today, "black", "-", 2),  # Thicker and solid line for today
            ("1 Month Ago", today - datetime.timedelta(days=30), "#ff7f0e", "--", 1),  # Thinner dashed line
            ("6 Months Ago", today - datetime.timedelta(days=182), "#9467bd", "--", 1),  # Thinner dashed line
            ("1 Year Ago", today - datetime.timedelta(days=365), "#2ca02c", "--", 1),  # Thinner dashed line
        ]

        try:
            self.error_label.configure(text="")  # Clear previous errors
            yield_data = []

            # Fetch data for each time point
            for label, date, color, style, linewidth in time_points:
                try:
                    yields = self.fetch_yield_curve_data(date)
                    yield_data.append((label, yields, color, style, linewidth))
                except ValueError as e:
                    logging.error(f"Error fetching data for {label}: {e}")

            if not yield_data:
                raise ValueError("No yield curve data could be retrieved for any date.")

            # Plot yield curves
            self.plot_yield_curve(yield_data)

        except Exception as e:
            self.error_label.configure(text=f"Error: {str(e)}")
