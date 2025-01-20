"""
Processor for processing results from models.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import strategy_analyzer.utilities as utilities
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.results.models_results import ModelsResults


class SignalsResultsProcessor:
    """
    A class to process and visualize the results of portfolio backtests and simulations.
    """
    def __init__(self, models_data: ModelsData, models_results: ModelsResults):
        """
        Initializes the ResultsProcessor with the data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all
            relevant parameters and data for processing results.
        """
        self.data_models = models_data
        self.results_models = models_results

    def process(self):
        """
        """
        self.plot_signals(latest_weights=self.results_models.latest_weights)

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

        asset_values = [weight * self.data_models.initial_portfolio_value for weight in asset_weights]

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
            title_text=f"Portfolio Signals on {self.data_models.end_date}",
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
            weights_filename=self.data_models.weights_filename,
            processing_type=self.data_models.processing_type
        )
