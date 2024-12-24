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

    def process_parameters(self):
        """
        Processes different SMA settings, runs backtests, and stores results
        in a dictionary with SMA values as keys.
        
        Returns
        -------
        dict
            A dictionary where keys are SMA values, and values are the corresponding
            backtest results and portfolio statistics.
        """
        results = {}
        sma_list = [21, 42, 63, 84, 105, 126, 147, 168, 189, 210]
        
        for sma in sma_list:
            self.data_models.sma_window = sma

            backtest_result = SmaBacktestPortfolio(self.data_models)

            cagr = self.data_models.cagr
            average_annual_return = self.data_models.average_annual_return
            max_drawdown = self.data_models.max_drawdown
            var = self.data_models.var
            cvar = self.data_models.cvar
            annual_volatility = self.data_models.annual_volatility

            results[sma] = {
                "backtest_result": backtest_result,
                "cagr": cagr,
                "average_annual_return": average_annual_return,
                "max_drawdown": max_drawdown,
                "var": var,
                "cvar": cvar,
                "annual_volatility": annual_volatility
            }

        return results
