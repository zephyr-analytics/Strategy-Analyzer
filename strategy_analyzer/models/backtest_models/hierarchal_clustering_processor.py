import datetime
import logging
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import strategy_analyzer.utilities as utilities
from strategy_analyzer.logger import logger
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.results.models_results import ModelsResults
from strategy_analyzer.models.backtest_models.backtesting_processor import BacktestingProcessor

logger = logging.getLogger(__name__)

class HierarchicalClusteringBacktestProcessor(BacktestingProcessor):
    """
    A class to backtest a static portfolio using hierarchical clustering based on covariance and distance.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)

    def get_portfolio_assets_and_weights(self, current_date):
        """
        Select assets based on hierarchical clustering and adjust weights based on SMA filtering.
        """
        # Calculate momentum and filter assets based on average momentum
        momentum = self.calculate_momentum(current_date)
        avg_momentum = momentum.mean()
        selected_assets = momentum[momentum > avg_momentum].index.tolist()

        # Perform hierarchical clustering on selected assets using covariance
        asset_data = self.data_portfolio.assets_data[selected_assets].loc[:current_date].pct_change().dropna()
        if asset_data.empty:
            return {}

        distance_matrix = pdist(asset_data.T.cov())
        clusters = fcluster(linkage(distance_matrix, method='ward'), t=0.5, criterion='distance')

        # Ensure the lengths of selected_assets and clusters match
        if len(selected_assets) != len(clusters):
            selected_assets = selected_assets[:len(clusters)]

        # Create a DataFrame to map assets to their clusters
        clustered_assets = pd.DataFrame({'Asset': selected_assets, 'Cluster': clusters})

        # Calculate the distance matrix for the selected assets
        distances = pd.DataFrame(squareform(distance_matrix), index=selected_assets, columns=selected_assets)

        # Select assets from each cluster based on distance
        final_selected_assets = []
        for cluster in clustered_assets['Cluster'].unique():
            cluster_assets = clustered_assets[clustered_assets['Cluster'] == cluster]['Asset'].tolist()
            cluster_distances = distances.loc[cluster_assets, cluster_assets]

            # Select the first asset with the highest momentum
            top_asset = cluster_assets[0]
            final_selected_assets.append(top_asset)

            # Select other assets that are sufficiently distant from the already selected ones
            for asset in cluster_assets[1:]:
                if all(cluster_distances.loc[asset, selected_asset] > 0.5 for selected_asset in final_selected_assets):
                    final_selected_assets.append(asset)

        # Convert final selected assets to DataFrame
        selected_assets_df = pd.DataFrame({'Asset': final_selected_assets})

        # Adjust weights within each cluster using the selected assets
        adjusted_weights = self.adjust_weights(current_date, selected_assets=selected_assets_df)

        return adjusted_weights

    def calculate_momentum(self, current_date: datetime) -> pd.Series:
        """
        Calculate average momentum based on 3, 6, 9, and 12-month cumulative returns.
        """
        momentum_data = self.data_portfolio.assets_data.copy().pct_change().dropna()
        momentum_3m = (momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        return (momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 4

    def adjust_weights(self, current_date: datetime, selected_assets: pd.DataFrame) -> dict:
        """
        Adjusts the weights of the clustered assets based on SMA.
        """
        def get_replacement_asset():
            """ Helper function to get replacement asset based on SMA. """
            if self.data_models.bond_ticker and not utilities.is_below_ma(
                current_date=current_date,
                ticker=self.data_models.bond_ticker,
                data=self.data_portfolio.bond_data,
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            ):
                return self.data_models.bond_ticker
            return self.data_models.cash_ticker

        adjusted_weights = {}
        total_weight = 0

        for _, row in selected_assets.iterrows():
            asset = row['Asset']
            if utilities.is_below_ma(
                current_date=current_date,
                ticker=asset,
                data=self.data_portfolio.assets_data,
                ma_type=self.data_models.ma_type,
                ma_window=self.data_models.ma_window,
            ):
                replacement_asset = get_replacement_asset()
                if replacement_asset:
                    adjusted_weights[replacement_asset] = adjusted_weights.get(replacement_asset, 0) + 1
            else:
                adjusted_weights[asset] = adjusted_weights.get(asset, 0) + 1
                total_weight += 1

        # Normalize weights to sum to 1
        adjusted_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}

        return adjusted_weights
