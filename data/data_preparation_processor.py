import utilities
from logger import logger
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
        logger.info(f"Preparaing Data for {self.weights_filename}.")
        self.read_data()

    def read_data(self):
        """
        Method to read data using utility functions and filter it based on asset weights.
        """
        full_data = utilities.read_data(self.weights_filename)

        self.data_portfolio.trading_data = full_data

        tickers_to_check = (
            set(self.asset_weights.keys()) |
            {self.cash_ticker, self.bond_ticker, self.ma_threshold_asset, self.benchmark_asset} |
            set(self.out_of_market_tickers)
        )

        filtered_data = full_data.loc[:, full_data.columns.intersection(tickers_to_check)]

        self.data_portfolio.assets_data = filtered_data.loc[:, filtered_data.columns.intersection(self.asset_weights.keys())]

        if self.cash_ticker in filtered_data.columns:
            self.data_portfolio.cash_data = filtered_data[[self.cash_ticker]]

        if self.bond_ticker in filtered_data.columns:
            self.data_portfolio.bond_data = filtered_data[[self.bond_ticker]]

        if self.ma_threshold_asset in filtered_data.columns:
            self.data_portfolio.ma_threshold_data = filtered_data[[self.ma_threshold_asset]]

        if self.benchmark_asset in filtered_data.columns:
            self.data_portfolio.benchmark_data = filtered_data[[self.benchmark_asset]]

        out_of_market_data = filtered_data.loc[:, filtered_data.columns.intersection(self.out_of_market_tickers)]
        if not out_of_market_data.empty:
            self.data_portfolio.out_of_market_data = out_of_market_data

        logger.info("Data successfully prepared.")
