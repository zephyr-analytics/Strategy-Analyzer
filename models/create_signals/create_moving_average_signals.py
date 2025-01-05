"""
Module for creating sma based porfolio signals.
"""

from models.create_signals.signals_processor import SignalsProcessor
from models.backtest_models.moving_average_backtest_processor import MovingAverageBacktestProcessor
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData

class CreateMovingAverageSignals(SignalsProcessor):
    """
    Processor for creating portfolio signals using the _run_backtest method.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData):
        """
        Initializes the CreateSignals class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data)


    def generate_signals(self):
        """
        Generates trading signals by running the backtest and pulling the latest weights.
        """
        self.backtest_portfolio = MovingAverageBacktestProcessor(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio
        )
        self.backtest_portfolio.process()
        latest_weights = self.data_models.adjusted_weights
        latest_weights = latest_weights.iloc[-1]
        self.plot_signals(latest_weights)
