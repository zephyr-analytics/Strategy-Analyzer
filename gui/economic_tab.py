import customtkinter as ctk
import pandas as pd
from pandas_datareader import data as pdr
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import logging


class EconomicTab:
    def __init__(self, parent):
        self.parent = parent
        self.configure_widgets(self.parent)

    def configure_widgets(self, parent):
        """
        Configures the widgets and layout for the EconomicTab using customtkinter.
        """
        # Header
        header = ctk.CTkLabel(parent, text="U.S. Treasury Yield Curve", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # Fetch and Plot Button
        fetch_button = ctk.CTkButton(parent, text="Fetch and Plot Yield Curve", command=self.update_plot)
        fetch_button.pack(pady=10)

        # Matplotlib Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        # Error Label
        self.error_label = ctk.CTkLabel(parent, text="", text_color="red", font=("Arial", 12))
        self.error_label.pack(pady=5)

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
        self.ax.set_title("Yield Curve Comparison", fontsize=14, fontweight='bold')
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
