"""
Abstract module for processing trading signals.
"""

from abc import ABC, abstractmethod

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import utilities as utilities
from models.models_data import ModelsData


class SignalsProcessor(ABC):
    """
    Abstract base class for creating portfolio signals.
    """

    def __init__(self, models_data: ModelsData):
        """
        Initializes the SignalProcessor class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        self.data_models = models_data
        self.initial_portfolio_value = models_data.initial_portfolio_value
        self.assets_weights = models_data.assets_weights
        self.bond_ticker = models_data.bond_ticker
        self.cash_ticker = models_data.cash_ticker
        self.weighting_strategy = models_data.weighting_strategy
        self.sma_period = int(models_data.sma_window)
        self.current_date = models_data.end_date
        self.output_filename = models_data.weights_filename
        self.weights_filename = models_data.weights_filename
        self.num_assets = models_data.num_assets_to_select
        self.processing_type = self.data_models.processing_type


    def process(self):
        """
        Abstract method to process data and generate trading signals.
        """
        self.generate_signals()


    @abstractmethod
    def generate_signals(self):
        """
        Abstract method to generate trading signals.
        """


    def plot_signals(self, latest_weights: dict, filename: str ='signals.html'):
        """
        Plots a pie chart and a table showing the asset weights as a percentage of the total portfolio.

        Parameters
        ----------
        latest_weights : dict
            The latest asset weights after adjustments from backtesting.
        filename : str
            The filename ending to be added for saving plot.
        """
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "table"}, {"type": "domain"}]],
            column_widths=[0.6, 0.4],
            subplot_titles=("Asset Weights", "Portfolio Weights Distribution")
        )

        asset_labels = list(latest_weights.keys())
        asset_weights = list(latest_weights.values())
        asset_percentages = [weight * 100 for weight in asset_weights]

        asset_values = [weight * self.initial_portfolio_value for weight in asset_weights]

        fig.add_trace(go.Table(
            header=dict(values=["Asset", "% Weight", "Expected Value"]),
            cells=dict(values=[
                asset_labels, 
                [f"{percentage:.2f}%" for percentage in asset_percentages], 
                [f"${value:,.2f}" for value in asset_values]
            ]),
            columnwidth=[80, 200, 200],
        ), row=1, col=1)

        fig.add_trace(go.Pie(
            labels=asset_labels,
            values=asset_weights,
            title="Portfolio Weights",
            textinfo='label+percent',
            hoverinfo='label+percent',
            showlegend=True
        ), row=1, col=2)

        fig.update_layout(
            title_text=f"Portfolio Signals on {self.current_date}",
            height=600,
            margin=dict(t=50, b=50, l=50, r=50),
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0.5, y=0.1,
                    text="© Zephyr Analytics",
                    showarrow=False,
                    font=dict(size=80, color="#f8f9f9"),
                    xanchor='center',
                    yanchor='bottom',
                    opacity=0.5
                )
            ]
        )

        utilities.save_html(
            fig,
            filename=filename,
            weights_filename=self.weights_filename,
            output_filename=self.output_filename,
            processing_type=self.processing_type,
            num_assets=self.num_assets
        )
