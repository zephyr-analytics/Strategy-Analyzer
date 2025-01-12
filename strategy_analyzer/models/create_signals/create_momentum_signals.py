"""
Module for creating momentum trading signals.
"""

from strategy_analyzer.models.create_signals.signals_processor import SignalsProcessor
from strategy_analyzer.models.backtest_models.momentum_backtest_processor import MomentumBacktestProcessor
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.results.models_results import ModelsResults


class CreateMomentumSignals(SignalsProcessor):
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
        self.backtest_portfolio = MomentumBacktestProcessor(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        self.backtest_portfolio.process()
        latest_weights = self.results_models.adjusted_weights
        latest_weights = latest_weights.iloc[-1]
        self.plot_signals(latest_weights)
