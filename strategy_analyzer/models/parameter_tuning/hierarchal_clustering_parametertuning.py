"""
Module for creating momentum based parameters.
"""

from multiprocessing import Pool

from tqdm import tqdm

from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from strategy_analyzer.models.backtest_models.hierarchal_clustering_processor import HierarchicalClusteringBacktestProcessor
from strategy_analyzer.results.models_results import ModelsResults


class HierarchalClusteringParameterTuning(ParameterTuningProcessor):
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
        ma_list = [21, 42, 63, 84, 105, 126, 147, 168, 189, 210, 231, 252]
        num_asset_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        trading_frequencies = ["Monthly", "Bi-Monthly", "Quarterly", "Yearly"]
        ma_types = ["SMA", "EMA"]

        total_assets = len(self.data_models.assets_weights)

        parameter_combinations = [
            (ma, ma, frequency, ma_type)
            for ma in ma_list
            for frequency in trading_frequencies
            for num_assets in num_asset_list if num_assets <= total_assets
            for ma_type in ma_types
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
        ma, frequency, num_assets, ma_type = args

        return self.process_combination(ma, frequency, num_assets, ma_type)

    def process_combination(self, ma, frequency, num_assets, ma_type) -> dict:
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
        self.data_models.num_assets_to_select = num_assets
        self.data_models.ma_type = ma_type

        backtest = HierarchicalClusteringBacktestProcessor(
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
