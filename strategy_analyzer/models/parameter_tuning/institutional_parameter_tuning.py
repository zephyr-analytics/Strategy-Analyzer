"""
Module for creating momentum based parameters.
"""

from multiprocessing import Pool

from tqdm import tqdm

from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from strategy_analyzer.models.backtest_models.institutional_backtest_processor import InstitutionalBacktestProcessor
from strategy_analyzer.results.models_results import ModelsResults


class InstitutionalParameterTuning(ParameterTuningProcessor):
    """
    Processor for parameter tuning based on the a momentum portfolio.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the parameter tuning class.

        Parameters
        ----------
        models_data : object
            An instance of the ModelsData class that holds all necessary attributes.
        """
        super().__init__(models_data=models_data, portfolio_data=portfolio_data, models_results=models_results)

    def get_portfolio_results(self) -> dict:
        """
        Processes parameters for tuning using joblib to parallelize execution.

        Returns
        -------
        dict
            A dictionary of backtest results and portfolio statistics from parameter tuning.
        """
        results = {}
        ma_list = [126, 147, 168, 189, 210, 231, 252]
        positive_list = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4, 4.25, 4.5, 4.75, 5]
        negative_list = [0, 0.25, 0.5, 1]
        asset_shift = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        trading_frequencies = ["Monthly"]
        ma_types = ["SMA", "EMA"]

        parameter_combinations = [
            (ma, frequency, ma_type, positive, negative, shift)
            for ma in ma_list
            for frequency in trading_frequencies
            for ma_type in ma_types
            for positive in positive_list
            for negative in negative_list
            for shift in asset_shift
        ]

        with Pool() as pool:
            for params, result in zip(
                parameter_combinations,
                tqdm(pool.imap(self.process_combination_wrapper, parameter_combinations), 
                    total=len(parameter_combinations), 
                    desc="Processing combinations")
            ):
                results[params] = result

        return results

    def process_combination_wrapper(self, args) -> dict:
        """
        Wrapper function for processing a combination.
        Calls the class method with unpacked arguments.

        Parameters
        ----------
        args : tuple
            A tuple containing (ma, frequency, ma_type).

        Returns
        -------
        dict
            The result of the combination processing.
        """
        ma, frequency, ma_type, positive, negative, shift = args

        return self.process_combination(ma, frequency, ma_type, positive, negative, shift)

    def process_combination(self, ma, frequency, ma_type, positive, negative, shift) -> dict:
        """
        Processes a single parameter combination and returns the backtest results.

        Parameters
        ----------
        ma : int
            Moving average window.
        frequency : str
            Trading frequency.
        num_assets : int
            Number of assets to select.
        ma_type : str
            Type of moving average (SMA or EMA).

        Returns
        -------
        dict
            The backtest results for the given parameter combination.
        """
        self.data_models.ma_window = ma
        self.data_models.trading_frequency = frequency
        self.data_models.asset_shift = shift
        self.data_models.ma_type = ma_type
        self.data_models.positive_adjustment = positive
        self.data_models.negative_adjustment = negative

        backtest = InstitutionalBacktestProcessor(
            models_data=self.data_models, 
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        backtest.process()

        return {
            "cagr": self.results_models.cagr,
            "average_annual_return": self.results_models.average_annual_return,
            "max_drawdown": self.results_models.max_drawdown,
            "var": self.results_models.var,
            "cvar": self.results_models.cvar,
            "annual_volatility": self.results_models.annual_volatility,
        }
