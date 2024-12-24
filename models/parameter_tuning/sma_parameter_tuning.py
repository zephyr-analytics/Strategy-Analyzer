"""
Module for creating sma based porfolio signals.
"""

from models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from models.backtest_models.sma_backtesting import SmaBacktestPortfolio


class SmaParameterTuning(ParameterTuningProcessor):
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
        results = self.get_portfolio_results()
        self.persist_results(results=results)

    def get_portfolio_results(self):
        """
        Processes parameters for tuning and stores results.
        
        Returns
        -------
        dict
            A dictionary of backtest results and portfolio statistics from parameter tuning.
        """
        results = {}
        sma_list = [21, 42, 63, 84, 105, 126, 147, 168, 189, 210]
        trading_frequencies = ["Monthly", "Bi-Monthly"]

        for sma in sma_list:
            for frequency in trading_frequencies:
                self.data_models.sma_window = sma
                self.data_models.trading_frequency = frequency

                backtest = SmaBacktestPortfolio(self.data_models)
                backtest.process()

                cagr = self.data_models.cagr
                average_annual_return = self.data_models.average_annual_return
                max_drawdown = self.data_models.max_drawdown
                var = self.data_models.var
                cvar = self.data_models.cvar
                annual_volatility = self.data_models.annual_volatility

                results[(sma, frequency)] = {
                    "cagr": cagr,
                    "average_annual_return": average_annual_return,
                    "max_drawdown": max_drawdown,
                    "var": var,
                    "cvar": cvar,
                    "annual_volatility": annual_volatility
                }

        return results
