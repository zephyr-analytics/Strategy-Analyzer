"""
Processor for creating porfolio signals.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import utilities as utilities


class CreateSignals:
    """
    Processor for creating portfolio signals.
    """

    def __init__(self, models_data, data):
        """
        Initializes the CreateSignals class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        data : pandas.DataFrame
            Data containing historical prices of the assets.
        """
        self.assets_weights = models_data.assets_weights
        self.data = data
        self.bond_ticker = models_data.bond_ticker
        self.cash_ticker = models_data.cash_ticker
        self.weighting_strategy = models_data.weighting_strategy
        self.sma_period = int(models_data.sma_window)
        self.current_date = models_data.end_date
        self.output_filename = models_data.weights_filename
        self.initial_portfolio_value = models_data.initial_portfolio_value

    def process(self):
        """
        Processes the data to generate trading signals.
        """
        self.generate_signals()

    def generate_signals(self):
        """
        Generates trading signals and plots the results.

        Parameters
        ----------
        current_date : str
            The date for which the signals are generated.
        """
        latest_weights = utilities.adjusted_weights(
            self.assets_weights, self.data, self.bond_ticker, self.cash_ticker,
            self.weighting_strategy, self.sma_period, self.current_date
        )
        self.plot_signals(latest_weights)

    def plot_signals(self, latest_weights, filename='signals.html'):
        """
        Plots the SMA status and current portfolio weights along with their dollar values.

        Parameters
        ----------
        latest_weights : dict
            The latest asset weights after adjustments.
        """
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "table"}, {"type": "domain"}]],
            column_widths=[0.6, 0.4],
            subplot_titles=("SMA Status", "Current Weights")
        )
        sma_status = []
        for ticker in self.assets_weights.keys():
            price = self.data.loc[:self.current_date, ticker].iloc[-1]
            sma = self.data.loc[:self.current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]
            status = "Above SMA" if price > sma else "Below SMA"
            sma_status.append(f"{ticker}: {status}")
        
        fig.add_trace(go.Table(
            header=dict(values=["Asset", "SMA Status"]),
            cells=dict(values=[list(self.assets_weights.keys()), sma_status]),
            columnwidth=[80, 200],
        ), row=1, col=1)
        
        asset_labels = list(latest_weights.keys())
        asset_weights = list(latest_weights.values())
        asset_values = [weight * self.initial_portfolio_value for weight in asset_weights]
        
        fig.add_trace(go.Pie(
            labels=asset_labels,
            values=asset_weights,
            title="Current Portfolio Weights",
            textinfo='label+percent',
            hoverinfo='label+value+percent+text',
            text=[f"${value:,.2f}" for value in asset_values],
            showlegend=True
        ), row=1, col=2)
        
        fig.update_layout(
            title_text=f"Portfolio Signals on {self.current_date}",
            height=600,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        utilities.save_html(fig, filename, self.output_filename)
