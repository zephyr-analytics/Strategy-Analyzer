import yfinance as yf
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt

class ClusteringPortfolio:
    """
    A class to construct a portfolio using hierarchical clustering, momentum, and equal weighting of selected assets.
    """

    def __init__(self, tickers, start_date, end_date, max_distance, num_assets):
        """
        Initialize the EqualWeightPortfolio class.
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.returns = None
        self.max_distance = max_distance
        self.num_assets = num_assets


    def fetch_data(self):
        """Fetch historical price data using yfinance."""
        self.data = yf.download(self.tickers, start=self.start_date, end=self.end_date)['Adj Close']
        self.returns = self.data.pct_change().dropna()


    def calculate_momentum(self):
        """Calculate average momentum based on 1, 3, 6, 9, and 12-month returns."""
        momentum_1m = self.returns.rolling(window=21).mean().iloc[-1]
        momentum_3m = self.returns.rolling(window=63).mean().iloc[-1]
        momentum_6m = self.returns.rolling(window=126).mean().iloc[-1]
        momentum_9m = self.returns.rolling(window=189).mean().iloc[-1]
        momentum_12m = self.returns.rolling(window=252).mean().iloc[-1]
        return (momentum_1m + momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 5


    def filter_assets_by_sma(self):
        """Filter assets that are above their 168-day Simple Moving Average (SMA)."""
        sma_168 = self.data.rolling(window=168).mean().iloc[-1]
        above_sma_168 = self.data.iloc[-1] > sma_168
        return self.data.columns[above_sma_168]


    def perform_clustering(self, filtered_assets):
        """
        Perform hierarchical clustering on the filtered assets and add labels to the dendrogram.
        """
        filtered_returns = self.returns[filtered_assets]
        cov_matrix = filtered_returns.cov()
        distance_matrix = 1 - cov_matrix.corr()
        condensed_distance_matrix = squareform(distance_matrix)
        Z = linkage(condensed_distance_matrix, method='ward')

        plt.figure(figsize=(20, 10))
        dendro = dendrogram(Z, labels=distance_matrix.columns)

        # Add labels to the dendrogram
        plt.title('Hierarchical Clustering of Assets')
        plt.xlabel('Assets')
        plt.ylabel('Distance')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

        clusters = fcluster(Z, self.max_distance, criterion='distance')
        return clusters


    def select_assets(self, filtered_assets, clusters, momentum):
        """
        Select the top 2 assets with the highest momentum from each cluster.
        If more than 4 assets are selected, drop BIL and SHV if present.
        """
        clustered_assets = pd.DataFrame({'Asset': filtered_assets, 'Cluster': clusters, 'Momentum': momentum[filtered_assets]})
        selected_assets = clustered_assets.groupby('Cluster').apply(lambda x: x.nlargest(self.num_assets, 'Momentum')).reset_index(drop=True)
        
        if len(selected_assets) > 2:
            selected_assets = selected_assets[~selected_assets['Asset'].isin(['SGOV', 'SHV'])]
        return selected_assets


    def plot_portfolio_allocation(self, selected_assets):
        """
        Plot a pie chart of the portfolio allocation based on equal weighting.
        """
        equal_weights = np.ones(len(selected_assets)) / len(selected_assets)
        plt.figure(figsize=(8, 8))
        plt.pie(equal_weights, labels=selected_assets['Asset'], autopct='%1.1f%%', startangle=140)
        plt.title('Portfolio Allocation Based on Equal Weighting')
        plt.show()


    def process(self):
        """
        Encapsulates the entire process of data fetching, filtering, clustering, asset selection,
        and plotting the portfolio allocation.
        """
        self.fetch_data()
        momentum = self.calculate_momentum()
        filtered_assets = self.filter_assets_by_sma()
        clusters = self.perform_clustering(filtered_assets)
        selected_assets = self.select_assets(filtered_assets, clusters, momentum)
        self.plot_portfolio_allocation(selected_assets)


if __name__ == "__main__":

    tickers = ['TLT', 'TLH', 'IEI', 'IEF', 'SGOV', 'SHV', 'SHY',
               'GLD', 'DBC',
               'VOX', 'VCR', 'VDC', 'VDE', 'VFH', 'VHT', 'VIS', 'VGT', 'VAW', 'VNQ', 'VPU',
               'VV', 'VUG', 'VTV', 'VB', 'VBK', 'VBR']

    portfolio = ClusteringPortfolio(tickers=tickers, start_date='2018-01-01', end_date='2024-09-01', max_distance=0.5, num_assets=2)
    portfolio.process()
