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
        self.update_economic_data()
        self.update_plot()


    def configure_widgets(self, parent):
        """
        Configures the widgets and layout for the EconomicTab using customtkinter.
        """
        self.header_frame = ctk.CTkFrame(parent)
        self.header_frame.pack(fill="x", pady=10)

        self.current_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.current_row.pack(fill="x", pady=2)
        self.previous_row = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.previous_row.pack(fill="x", pady=2)

        self.data_fields = {"current": {}, "previous": {}}
        self.economic_metrics = {
            "GDP": "GDP",
            "Unemployment Rate": "UNRATE",
            "Initial Jobless Claims": "ICSA",
            "Inflation Rate": "STICKCPIM159SFRBATL",
            "Federal Funds Rate": "FEDFUNDS",
        }

        self.opposite_scale_metrics = {"Unemployment Rate", "Initial Jobless Claims", "Inflation Rate"}

        for metric, series_id in self.economic_metrics.items():
            c_label = ctk.CTkLabel(self.current_row, text=f"{metric} (Current):", font=("Arial", 16, "bold"))
            c_value_label = ctk.CTkLabel(self.current_row, text="Loading...", font=("Arial", 16, "bold"))
            c_label.pack(side="left", padx=(10, 5))
            c_value_label.pack(side="left", padx=(0, 20))
            self.data_fields["current"][metric] = c_value_label

            p_label = ctk.CTkLabel(self.previous_row, text=f"{metric} (Previous):", font=("Arial", 16, "italic"))
            p_value_label = ctk.CTkLabel(self.previous_row, text="Loading...", font=("Arial", 16, "italic"))
            p_label.pack(side="left", padx=(10, 5))
            p_value_label.pack(side="left", padx=(0, 20))
            self.data_fields["previous"][metric] = p_value_label

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        self.error_label = ctk.CTkLabel(parent, text="", text_color="red", font=("Arial", 12))
        self.error_label.pack(pady=5)

        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=20)
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© Zephyr Analytics 2024",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack()


    def fetch_economic_data(self, series_id):
        """
        Fetches the latest and previous available values for a specific economic series from FRED.
        """
        try:
            data = pdr.DataReader(series_id, "fred", datetime.datetime.now() - datetime.timedelta(days=365))
            latest = data.iloc[-1].values[0]
            previous = data.iloc[-2].values[0]
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
            return f"{value:.2f}%"
        elif metric == "Initial Jobless Claims":
            return f"{int(value):,}"
        elif metric == "GDP":
            return f"${value:,.0f}B"
        else:
            return f"{value}"


    def apply_color(self, metric, latest, previous):
        """
        Determines the color based on whether the value has increased or decreased.
        """
        if latest is None or previous is None or latest == previous:
            return "black"

        if metric == "Federal Funds Rate":
            return "black"

        if metric in self.opposite_scale_metrics:
            return "#006400" if latest < previous else "#8B0000"
        else:
            return "#006400" if latest > previous else "#8B0000"


    def update_economic_data(self):
        """
        Fetches and updates the economic data fields for both current and previous values.
        """
        for metric, series_id in self.economic_metrics.items():
            latest, previous = self.fetch_economic_data(series_id)
            formatted_latest = self.format_value(metric, latest)
            formatted_previous = self.format_value(metric, previous)

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
        # TODO the date settings do not look correct.
        start_date = date - datetime.timedelta(days=7)
        end_date = date
        try:
            data = pdr.DataReader(series, "fred", start_date, end_date)
            return data.iloc[-1].dropna()
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
            ("Today", today, "black", "-", 2),
            ("1 Month Ago", today - datetime.timedelta(days=30), "#ff7f0e", "--", 1),
            ("6 Months Ago", today - datetime.timedelta(days=182), "#9467bd", "--", 1),
            ("1 Year Ago", today - datetime.timedelta(days=365), "#2ca02c", "--", 1),
        ]
        try:
            self.error_label.configure(text="")
            yield_data = []
            for label, date, color, style, linewidth in time_points:
                try:
                    yields = self.fetch_yield_curve_data(date)
                    yield_data.append((label, yields, color, style, linewidth))
                except ValueError as e:
                    logging.error(f"Error fetching data for {label}: {e}")
            if not yield_data:
                raise ValueError("No yield curve data could be retrieved for any date.")
            self.plot_yield_curve(yield_data)
        except Exception as e:
            self.error_label.configure(text=f"Error: {str(e)}")
