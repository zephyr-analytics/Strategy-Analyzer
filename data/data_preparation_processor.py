"""
Module for preparaing and persisting data.
"""

import utilities as utilities
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData


class DataPreparationProcessor:
    """
    Class for obtaining and persisting data with retry mechanisms and validation.
    """

    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        self.data_models = models_data
        self.data_portfolio = portfolio_data

        self.weights_filename = self.data_models.weights_filename
        self.asset_weights = self.data_models.assets_weights
        self.cash_ticker = self.data_models.cash_ticker
        self.bond_ticker = self.data_models.bond_ticker
        self.ma_threshold_asset = self.data_models.ma_threshold_asset
        self.benchmark_asset = self.data_models.benchmark_asset
        self.out_of_market_tickers = self.data_models.out_of_market_tickers

    def process(self):
        """
        Main method to check, load, and validate data.
        """
        self.read_data()
    
    def read_data(self):
        """
        Method to read data using utility functions and filter it based on asset weights.
        """
        full_data = utilities.read_data(self.weights_filename)
        self.data_portfolio.assets_data = full_data[full_data['asset'].isin(self.asset_weights.keys())]

        if self.cash_ticker in full_data['asset'].values:
            self.data_portfolio.cash_data = full_data[full_data['asset'] == self.cash_ticker]
        if self.bond_ticker in full_data['asset'].values:
            self.data_portfolio.bond_data = full_data[full_data['asset'] == self.bond_ticker]
        if self.ma_threshold_asset in full_data['asset'].values:
            self.data_portfolio.ma_threshold_data = full_data[full_data['asset'] == self.ma_threshold_asset]
        if self.benchmark_asset in full_data['asset'].values:
            self.data_portfolio.benchmark_data = full_data[full_data['asset'] == self.benchmark_asset]
        if any(ticker in full_data['asset'].values for ticker in self.out_of_market_tickers):
            self.data_portfolio.out_of_market_data = full_data[full_data['asset'].isin(self.out_of_market_tickers)]
