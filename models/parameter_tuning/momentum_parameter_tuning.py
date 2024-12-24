"""
Module for creating sma based porfolio signals.
"""

import os
import json

from models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from models.backtest_models.momentum_backtest import BacktestMomentumPortfolio


class MomentumParameterTuning(ParameterTuningProcessor):
    def __init__(self, models_data):
        super().__init__(models_data)

    def process(self):
        results = self.get_portfolio_results()
        self.persist_results(results=results)
        self.optimize_portfolio(results=results)

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
        num_asset_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        trading_frequencies = ["Monthly", "Bi-Monthly"]

        total_assets = len(self.data_models.assets_weights)

        for sma in sma_list:
            for frequency in trading_frequencies:
                for num_assets in num_asset_list:
                    if num_assets > total_assets:
                        break
                    self.data_models.sma_window = sma
                    self.data_models.trading_frequency = frequency
                    self.data_models.num_assets_to_select = num_assets

                    backtest = BacktestMomentumPortfolio(self.data_models)
                    backtest.process()

                    cagr = self.data_models.cagr
                    average_annual_return = self.data_models.average_annual_return
                    max_drawdown = self.data_models.max_drawdown
                    var = self.data_models.var
                    cvar = self.data_models.cvar
                    annual_volatility = self.data_models.annual_volatility

                    results[(sma, frequency, num_assets)] = {
                        "cagr": cagr,
                        "average_annual_return": average_annual_return,
                        "max_drawdown": max_drawdown,
                        "var": var,
                        "cvar": cvar,
                        "annual_volatility": annual_volatility
                    }

        return results

    def persist_results(self, results):
        """
        Persists the results dictionary as a JSON file.

        Parameters
        ----------
        results : dict
            The dictionary containing SMA backtest results and portfolio statistics.
        """
        current_directory = os.getcwd()
        artifacts_directory = os.path.join(current_directory, "artifacts", "data")
        os.makedirs(artifacts_directory, exist_ok=True)

        full_path = os.path.join(artifacts_directory, "sma_parameter_tune.json")
        results_serializable = {
            f"SMA_{key[0]}_Freq_{key[1]}_Assets_{key[2]}": value for key, value in results.items()
        }
        with open(full_path, 'w') as json_file:
            json.dump(results_serializable, json_file, indent=4)
        print(f"Results successfully saved to {full_path}")

    def optimize_portfolio(self, results, return_metric="cagr", risk_metric="max_drawdown"):
        """
        Finds the best portfolio from the results dictionary based on the selected return and risk metrics.

        Parameters
        ----------
        results : dict
            The dictionary containing SMA backtest results and portfolio statistics.
        return_metric : str, optional
            The primary return metric to optimize for (default is "cagr").
        risk_metric : str, optional
            The risk metric to consider for optimization (default is "max_drawdown").

        Returns
        -------
        tuple
            The best SMA, trading frequency, and number of assets configuration, along with its statistics.
        """
        best_config = None
        best_score = float('-inf')
        best_stats = None

        for (sma, frequency, num_assets), stats in results.items():
            return_value = stats.get(return_metric, None)
            risk_value = stats.get(risk_metric, None)

            if return_value is None or risk_value is None:
                continue

            score = return_value / abs(risk_value)

            if score > best_score:
                best_score = score
                best_config = (sma, frequency, num_assets)
                best_stats = stats
        print(best_config)
        print(best_stats)
        return best_config, best_stats
