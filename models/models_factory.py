"""
Models factory for handling differnet backtesting models and runs.
"""

from processing_types import *
from models.create_signals import *
from models.backtest_models import *
from models.monte_carlo_simulation import *
from models.parameter_tuning import *
from models.models_data import ModelsData
from data.portfolio_data import PortfolioData
from results.models_results import ModelsResults


class ModelsFactory:
    """
    Factory class to handle model processing based on the provided enum types.
    """
    def __init__(self, models_data: ModelsData, portfolio_data: PortfolioData, models_results: ModelsResults):
        """
        Initializes the ModelsFactory with the provided data models.

        Parameters
        ----------
        data_models : ModelsData
            An instance of ModelsData containing the relevant data.
        """
        self.data_models = models_data
        self.data_portfolio = portfolio_data
        self.results_models = models_results

    def run(self, model: Models, run_type: Runs) -> str:
        """
        Executes the corresponding method based on the provided model and run type.

        Parameters
        ----------
        model : Models
            Enum representing the model type (e.g., Models.SMA).
        run_type : Runs
            Enum representing the run type (e.g., Runs.BACKTEST).

        Returns
        -------
        str
            Result message indicating the outcome of the operation.
        """
        model_run_map = {
            (Models.MA, Runs.BACKTEST): self._run_ma_backtest,
            (Models.MA, Runs.SIGNALS): self._run_ma_signals,
            (Models.MA, Runs.SIMULATION): self._run_ma_simulation,
            (Models.MA, Runs.PARAMETER_TUNE): self._run_ma_parameter_tune,
            (Models.MOMENTUM, Runs.BACKTEST): self._run_momentum_backtest,
            (Models.MOMENTUM, Runs.SIGNALS): self._run_momentum_signals,
            (Models.MOMENTUM, Runs.SIMULATION): self._run_momentum_simulation,
            (Models.MOMENTUM, Runs.PARAMETER_TUNE): self._run_momentum_parameter_tune,
            (Models.IN_AND_OUT_OF_MARKET, Runs.BACKTEST): self._run_in_and_out_of_market_backtest,
            (Models.IN_AND_OUT_OF_MARKET, Runs.SIGNALS): self._run_in_and_out_of_market_signals,
            (Models.IN_AND_OUT_OF_MARKET, Runs.PARAMETER_TUNE): self._run_iao_momentum_parameter_tune,
            (Models.IN_AND_OUT_OF_MARKET, Runs.SIMULATION): self._run_iao_simulation
        }

        method = model_run_map.get((model, run_type))
        if not method:
            return "Invalid model or run type combination."
        self.data_models.processing_type = f"{model.name}_{run_type.name}"
        return method()

    def _run_ma_backtest(self) -> str:
        """
        Executes the SMA backtest process.

        Returns
        -------
        str
            Message indicating the outcome of the SMA backtest.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        backtest = MovingAverageBacktestProcessor(
            models_data=self.data_models, 
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        backtest.process()
        return "MA backtest completed and plots saved."

    def _run_ma_signals(self) -> str:
        """
        Executes the SMA signals generation process.

        Returns
        -------
        str
            Message indicating the outcome of the SMA signals generation.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        create_signals = CreateMovingAverageSignals(models_data=self.data_models, portfolio_data=self.data_portfolio)
        create_signals.process()
        return f"MA signals generated for {self.data_models.end_date}."

    def _run_ma_simulation(self) -> str:
        """
        Executes the SMA Monte Carlo simulation process.

        Returns
        -------
        str
            Message indicating the outcome of the SMA simulation.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        backtest = MovingAverageBacktestProcessor(models_data=self.data_models, portfolio_data=self.data_portfolio)
        backtest.process()
        monte_carlo = MonteCarloSimulation(models_data=self.data_models)
        monte_carlo.process()
        return "MA simulation completed and plots saved."

    def _run_momentum_backtest(self) -> str:
        """
        Executes the momentum backtest process.

        Returns
        -------
        str
            Message indicating the outcome of the momentum backtest.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        backtest = MomentumBacktestProcessor(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        backtest.process()
        return "Momentum backtest completed and plots saved."

    def _run_momentum_signals(self) -> str:
        """
        Executes the momentum signals generation process.

        Returns
        -------
        str
            Message indicating the outcome of the momentum signals generation.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        create_signals = CreateMomentumSignals(models_data=self.data_models, portfolio_data=self.data_portfolio)
        create_signals.process()
        return f"Momentum signals generated for {self.data_models.end_date}."

    def _run_momentum_simulation(self)-> str:
        """
        Executes the momentum Monte Carlo simulation process.

        Returns
        -------
        str
            Message indicating the outcome of the momentum simulation.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        backtest = MomentumBacktestProcessor(models_data=self.data_models, portfolio_data=self.data_portfolio)
        backtest.process()
        monte_carlo = MonteCarloSimulation(models_data=self.data_models)
        monte_carlo.process()
        return "Momentum simulation completed and plots saved."

    def _run_in_and_out_of_market_backtest(self) -> str:
        """
        Executes the In and Out of Market backtest process.

        Returns
        -------
        str
            Message indicating the outcome of the In and Out of Market backtest.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        if not self.data_models.out_of_market_tickers:
            return "Please load out of market assets file."
        backtest = IAOMomentumBacktestProcessor(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        backtest.process()
        return "In and Out of Market backtest completed and plots saved."

    def _run_in_and_out_of_market_signals(self) -> str:
        """
        Executes the In and Out of Market signals generation process.

        Returns
        -------
        str
            Message indicating the outcome of the In and Out of Market signals generation.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        if not self.data_models.out_of_market_tickers:
            return "Please load out of market assets file."
        signals = CreateMomentumInAndOutSignals(models_data=self.data_models, portfolio_data=self.data_portfolio)
        signals.process()
        return "In and Out of Market signals completed and plots saved."

    def _run_ma_parameter_tune(self) -> str:
        """
        Executes the SMA parameter tune processor.

        Returns
        -------
        str
            Message indicating the outcome of the SMA parameter tune generation.
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        parameter_tune = MovingAverageParameterTuning(
            models_data=self.data_models,
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        parameter_tune.process()
        return "MA parameter tuning completed."

    def _run_momentum_parameter_tune(self) -> str:
        """
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        parameter_tune = MomentumParameterTuning(
            models_data=self.data_models, 
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        parameter_tune.process()
        return "Momentum parameter tuning completed."

    def _run_iao_momentum_parameter_tune(self) -> str:
        """
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        if not self.data_models.out_of_market_tickers:
            return "Please load out of market assets file."
        parameter_tune = InAndOutMomentumParameterTuning(
            models_data=self.data_models, 
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        parameter_tune.process()
        return "In and Out Momentum parameter tuning completed."

    def _run_iao_simulation(self) -> str:
        """
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        if not self.data_models.out_of_market_tickers:
            return "Please load out of market assets file."
        backtest = IAOMomentumBacktestProcessor(models_data=self.data_models, portfolio_data=self.data_portfolio)
        backtest.process()
        monte_carlo = MonteCarloSimulation(models_data=self.data_models)
        monte_carlo.process()
        return "Momentum simulation completed and plots saved."

    def _run_moving_average_crossover_backtest(self) -> str:
        """
        """
        if not self.data_models.assets_weights:
            return "Please load asset weights file."
        backtest = MovingAverageCrossoverProcessor(
            models_data=self.data_models, 
            portfolio_data=self.data_portfolio,
            models_results=self.results_models
        )
        backtest.process()
