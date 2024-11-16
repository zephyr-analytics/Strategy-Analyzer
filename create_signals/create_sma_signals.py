"""
Processor for creating sma based porfolio signals.
"""

from sma_models.backtesting import BacktestStaticPortfolio
from create_signals.signals_processor import SignalsProcessor


class CreateSmaSignals(SignalsProcessor):
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
        """
        super().__init__(models_data)


    def process(self):
        """
        Processes the data to generate trading signals.
        """
        self.generate_signals()


    def generate_signals(self):
        """
        Generates trading signals by running the backtest and pulling the latest weights.
        """
        self.backtest_portfolio = BacktestStaticPortfolio(self.data_models)
        self.backtest_portfolio.process()
        latest_weights = self.data_models.adjusted_weights
        print(latest_weights)
        self.plot_signals(latest_weights)
