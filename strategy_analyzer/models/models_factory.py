"""
Models factory for handling different backtesting models and runs.
"""

from strategy_analyzer.processing_types import *
from strategy_analyzer.models.create_signals import *
from strategy_analyzer.models.backtest_models import *
from strategy_analyzer.models.monte_carlo_simulation import *
from strategy_analyzer.models.parameter_tuning import *
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.data.portfolio_data import PortfolioData
from strategy_analyzer.results.models_results import ModelsResults

class ModelsFactory:
    """
    Factory class to handle model processing based on the provided enum types.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results

    def run(self, model: Models, run_type: Runs) -> str:
        """
        Executes the corresponding method based on the provided model and run type.
        """
        model_run_map = {
            (Models.MA, Runs.BACKTEST): self._run_backtest,
            (Models.MA, Runs.SIGNALS): self._run_signals,
            (Models.MA, Runs.SIMULATION): self._run_simulation,
            (Models.MA, Runs.PARAMETER_TUNE): self._run_parameter_tune,
            (Models.MOMENTUM, Runs.BACKTEST): self._run_backtest,
            (Models.MOMENTUM, Runs.SIGNALS): self._run_signals,
            (Models.MOMENTUM, Runs.SIMULATION): self._run_simulation,
            (Models.MOMENTUM, Runs.PARAMETER_TUNE): self._run_parameter_tune,
            (Models.IN_AND_OUT_OF_MARKET, Runs.BACKTEST): self._run_backtest,
            (Models.IN_AND_OUT_OF_MARKET, Runs.SIGNALS): self._run_signals,
            (Models.IN_AND_OUT_OF_MARKET, Runs.SIMULATION): self._run_simulation,
            (Models.IN_AND_OUT_OF_MARKET, Runs.PARAMETER_TUNE): self._run_parameter_tune,
            (Models.MACHINE_LEARNING, Runs.BACKTEST): self._run_backtest,
            (Models.MACHINE_LEARNING, Runs.PARAMETER_TUNE): self._run_parameter_tune,
            (Models.MA_CROSSOVER, Runs.BACKTEST): self._run_backtest,
            (Models.MA_CROSSOVER, Runs.PARAMETER_TUNE): self._run_parameter_tune
        }

        method = model_run_map.get((model, run_type))
        if not method:
            return "Invalid model or run type combination."

        self.data_models.processing_type = f"{model.name}_{run_type.name}"
        return method(model)

    def _run_backtest(self, model: Models) -> str:
        if not self.data_models.assets_weights:
            return "Please load asset weights file."

        processor_class = self._get_processor_class(model, "backtest")
        if not processor_class:
            return "No backtest processor found for this model."

        processor = processor_class(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        processor.process()
        return f"{model.name} backtest completed and plots saved."

    def _run_signals(self, model: Models) -> str:
        if not self.data_models.assets_weights:
            return "Please load asset weights file."

        processor_class = self._get_processor_class(model, "signals")
        if not processor_class:
            return "No signals processor found for this model."

        processor = processor_class(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        processor.process()
        return f"{model.name} signals generated for {self.data_models.end_date}."

    def _run_simulation(self, model: Models) -> str:
        if not self.data_models.assets_weights:
            return "Please load asset weights file."

        backtest_class = self._get_processor_class(model, "backtest")
        simulation_class = self._get_processor_class(model, "simulation")

        if not backtest_class or not simulation_class:
            return "No simulation processor found for this model."

        backtest = backtest_class(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        backtest.process()

        simulation = simulation_class(
            models_data=self.data_models,
            models_results=self.results_models
        )
        simulation.process()
        return f"{model.name} simulation completed and plots saved."

    def _run_parameter_tune(self, model: Models) -> str:
        if not self.data_models.assets_weights:
            return "Please load asset weights file."

        processor_class = self._get_processor_class(model, "tune")
        if not processor_class:
            return "No parameter tuning processor found for this model."

        processor = processor_class(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        processor.process()
        return f"{model.name} parameter tuning completed."

    def _get_processor_class(self, model: Models, process_type: str):
        processor_map = {
            "MA": {
                "backtest": MovingAverageBacktestProcessor,
                "signals": CreateMovingAverageSignals,
                "simulation": MonteCarloSimulation,
                "tune": MovingAverageParameterTuning
            },
            "MOMENTUM": {
                "backtest": MomentumBacktestProcessor,
                "signals": CreateMomentumSignals,
                "simulation": MonteCarloSimulation,
                "tune": MomentumParameterTuning
            },
            "IN_AND_OUT_OF_MARKET": {
                "backtest": IAOMomentumBacktestProcessor,
                "signals": CreateMomentumInAndOutSignals,
                "simulation": MonteCarloSimulation,
                "tune": InAndOutMomentumParameterTuning
            },
            "MACHINE_LEARNING": {
                "backtest": HierarchicalClusteringBacktestProcessor,
                "tune": HierarchalClusteringParameterTuning
            },
            "MA_CROSSOVER": {
                "backtest": MovingAverageCrossoverProcessor,
                "tune": MaCrossoverParameterTuning
            }
        }
        return processor_map.get(model.name, {}).get(process_type)
