import pandas as pd
from pandas_datareader import data as pdr
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk


def fetch_yield_curve_data(date):
    """
    Fetches yield curve data from the FRED database for a specific date range.
    """
    series = [
        "DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2",
        "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"
    ]
    start_date = date - datetime.timedelta(days=7)  # Use a week window to ensure data availability
    end_date = date
    data = pdr.DataReader(series, "fred", start_date, end_date)
    return data.iloc[-1].dropna()  # Get the most recent data and drop NaNs


def plot_yield_curve(today_yields, one_month_ago_yields, one_year_ago_yields, canvas):
    """
    Plots the yield curve for three time points on the same plot.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Extract maturities and yields for each time period
    def process_yields(yields):
        maturities = [
            int(s.lstrip('DGS').replace('MO', '')) / 12 if 'MO' in s else int(s.lstrip('DGS'))
            for s in yields.index
        ]
        rates = yields.values
        return maturities, rates

    # Plot each yield curve
    for yields, label, color in zip(
        [today_yields, one_month_ago_yields, one_year_ago_yields],
        ["Today", "1 Month Ago", "1 Year Ago"],
        ["blue", "orange", "green"],
    ):
        maturities, rates = process_yields(yields)
        ax.plot(maturities, rates, marker='o', linestyle='-', label=label, color=color)

    # Chart formatting
    ax.set_title("Yield Curve Comparison")
    ax.set_xlabel("Maturity (Years)")
    ax.set_ylabel("Yield (%)")
    ax.legend()
    ax.grid(True)

    # Update the canvas
    canvas.figure = fig
    canvas.draw()


class YieldCurveWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yield Curve Widget")
        self.geometry("800x600")

        # Header
        header = ttk.Label(self, text="Yield Curve Visualization", font=("Arial", 16))
        header.pack(pady=10)

        # Fetch and Plot Button
        fetch_button = ttk.Button(self, text="Fetch and Plot Yield Curve", command=self.update_plot)
        fetch_button.pack(pady=10)

        # Matplotlib Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

    def update_plot(self):
        today = datetime.datetime.now()
        one_month_ago = today - datetime.timedelta(days=30)
        one_year_ago = today - datetime.timedelta(days=365)

        try:
            # Fetch data for three time periods
            today_yields = fetch_yield_curve_data(today)
            one_month_ago_yields = fetch_yield_curve_data(one_month_ago)
            one_year_ago_yields = fetch_yield_curve_data(one_year_ago)

            # Plot yield curves
            plot_yield_curve(today_yields, one_month_ago_yields, one_year_ago_yields, self.canvas)

        except Exception as e:
            error_label = ttk.Label(self, text=f"Error: {str(e)}", foreground="red")
            error_label.pack(pady=5)


if __name__ == "__main__":
    app = YieldCurveWidget()
    app.mainloop()
