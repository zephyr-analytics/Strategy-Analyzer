import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import squareform
import utilities as utilities

class CreateMLSignals:
    """
    Processor for creating portfolio signals based on momentum and clustering.
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
        self.models_data = models_data
        self.data = data
        self.assets_weights = models_data.assets_weights
        self.bond_ticker = models_data.bond_ticker
        self.cash_ticker = models_data.cash_ticker
        self.sma_period = int(models_data.sma_window)
        self.current_date = models_data.end_date
        self.output_filename = models_data.weights_filename
        self.initial_portfolio_value = models_data.initial_portfolio_value

    def process(self):
        """
        Processes the data to generate trading signals.
        """
        momentum = self.calculate_momentum(self.current_date)
        clusters = self.perform_clustering(self.current_date, list(self.assets_weights.keys()))
        selected_assets = self.select_assets(list(self.assets_weights.keys()), clusters, momentum)
        latest_weights = self.adjust_weights(self.current_date, selected_assets)
        self.plot_signals(latest_weights)

    def calculate_momentum(self, current_date):
        """
        Calculate average momentum based on 1, 3, 6, 9, and 12-month cumulative returns.
        """
        momentum_data = self.data.pct_change().dropna()
        momentum_1m = (momentum_data.loc[:current_date].iloc[-21:] + 1).prod() - 1
        momentum_3m = (momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        return (momentum_1m + momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 5

    def perform_clustering(self, current_date, filtered_assets):
        """
        Perform hierarchical clustering on the filtered assets and add labels to the dendrogram.
        """
        filtered_returns = self.data.pct_change().dropna().loc[:current_date, filtered_assets]
        cov_matrix = filtered_returns.cov()
        distance_matrix = 1 - cov_matrix.corr()
        condensed_distance_matrix = squareform(distance_matrix)
        Z = linkage(condensed_distance_matrix, method='ward')
        clusters = fcluster(Z, self.models_data.max_distance, criterion='distance')
        return clusters

    def select_assets(self, filtered_assets, clusters, momentum):
        """
        Select the top 2 assets with the highest momentum from each cluster.
        If more than 4 assets are selected, drop SGOV and SHV if present.
        """
        clustered_assets = pd.DataFrame({'Asset': filtered_assets, 'Cluster': clusters, 'Momentum': momentum[filtered_assets]})
        selected_assets = clustered_assets.groupby('Cluster').apply(lambda x: x.nlargest(1, 'Momentum')).reset_index(drop=True)
        
        if len(selected_assets) > 1:
            selected_assets = selected_assets[~selected_assets['Asset'].isin(['BND', 'SHV'])]
        return selected_assets

    def adjust_weights(self, current_date, selected_assets):
        """
        Adjusts the weights of the selected assets based on their SMA.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame of selected assets and their weights.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        num_assets = len(selected_assets)
        equal_weight = 1 / num_assets
        adjusted_weights = {asset: equal_weight for asset in selected_assets['Asset']}
        
        for ticker in list(adjusted_weights.keys()):
            if self.data.loc[:current_date, ticker].iloc[-1] < self.data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                if self.data.loc[:current_date, self.bond_ticker].iloc[-1] < self.data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                    adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + adjusted_weights[ticker]
                    adjusted_weights[ticker] = 0
                else:
                    adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + adjusted_weights[ticker]
                    adjusted_weights[ticker] = 0

        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight
        return adjusted_weights

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
