"""
Processor for creating porfolio signals.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import utilities as utilities
from sma_models.backtesting import BacktestStaticPortfolio

class CreateSignals:
    """
    Processor for creating portfolio signals using the _run_backtest method.
    """

    def __init__(self, models_data):
        """
        Initializes the CreateSignals class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        data : pandas.DataFrame
            Data containing historical prices of the assets.
        backtest_portfolio : BacktestStaticPortfolio
            An instance of BacktestStaticPortfolio to run the backtest and pull the latest weights.
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
        self.initial_portfolio_value = models_data.initial_portfolio_value
        self.backtest_portfolio = BacktestStaticPortfolio(models_data)

    def process(self):
        """
        Processes the data to generate trading signals.
        """
        self.generate_signals()

    def generate_signals(self):
        """
        Generates trading signals by running the backtest and pulling the latest weights.
        """
        self.backtest_portfolio.process()
        latest_weights = self.data_models.adjusted_weights
        print(latest_weights)
        self.plot_signals(latest_weights)

    def plot_signals(self, latest_weights, filename='signals.html'):
        """
        Plots a pie chart and a table showing the asset weights as a percentage of the total portfolio.

        Parameters
        ----------
        latest_weights : dict
            The latest asset weights after adjustments from backtesting.
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
        
        # Calculate expected value based on initial portfolio value
        asset_values = [weight * self.initial_portfolio_value for weight in asset_weights]

        # Add table with asset weights and expected values
        fig.add_trace(go.Table(
            header=dict(values=["Asset", "% Weight", "Expected Value"]),
            cells=dict(values=[
                asset_labels, 
                [f"{percentage:.2f}%" for percentage in asset_percentages], 
                [f"${value:,.2f}" for value in asset_values]
            ]),
            columnwidth=[80, 200, 200],
        ), row=1, col=1)

        # Add pie chart with asset weight distribution
        fig.add_trace(go.Pie(
            labels=asset_labels,
            values=asset_weights,
            title="Portfolio Weights",
            textinfo='label+percent',
            hoverinfo='label+percent',
            showlegend=True
        ), row=1, col=2)

        # Update layout and add watermark annotation
        fig.update_layout(
            title_text=f"Portfolio Signals on {self.current_date}",
            height=600,
            margin=dict(t=50, b=50, l=50, r=50),
            annotations=[
                # Watermark annotation
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
        
        # Save the plot as an HTML file
        utilities.save_html(fig, filename, self.output_filename)

