"""
Module for creating IAO momentum trading signals.
"""
import logging

from strategy_analyzer.logger import logger
from strategy_analyzer.models.create_signals.signals_processor import SignalsProcessor
from strategy_analyzer.models.backtest_models.iao_momentum_backtest_processor import IAOMomentumBacktestProcessor
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.results.models_results import ModelsResults

logger = logging.getLogger(__name__)


class CreateMomentumInAndOutSignals(SignalsProcessor):
    """
    Processor for creating portfolio signals using the _run_backtest method.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the CreateSignals class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)


    def generate_signals(self):
        """
        Generates trading signals by running the backtest and pulling the latest weights.
        """
        self.backtest_portfolio = IAOMomentumBacktestProcessor(
            models_data=self.data_models, 
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        self.backtest_portfolio.process()
        self.results_models.latest_weights = self.results_models.adjusted_weights.iloc[-1]
