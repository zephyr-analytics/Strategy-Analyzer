"""
Main module for encapsulating calling processors.
"""

import utilities as utilities
from models_data import ModelsData

from backtest_models.momentum_backtest import BacktestMomentumPortfolio
from backtest_models.iao_momentum_backtest import BacktestInAndOutMomentumPortfolio

from create_signals.create_momentum_signals import CreateMomentumSignals
from create_signals.create_momentumiao_signals import CreateMomentumInAndOutSignals
from create_signals.create_sma_signals import CreateSmaSignals

from backtest_models.hierarchical_clustering import BacktestClusteringPortfolio
from create_signals.create_ml_signals import CreateMLSignals

from backtest_models.sma_backtesting import SmaBacktest
from monte_carlo_simulation.monte_carlo_sim import MonteCarloSimulation


def run_backtest(data_models: ModelsData):
    """
    Method for passing models_data to Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    backtest = SmaBacktest(data_models)
    backtest.process()

    return "Backtest completed and plots saved."


def run_momentum_backtest(data_models: ModelsData):
    """
    Method for passing models_data to Momentum Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."
    momentum_backtest = BacktestMomentumPortfolio(data_models)
    momentum_backtest.process()

    return "Momentum backtest completed and plots saved"


def run_machine_learning_backtest(data_models: ModelsData):
    """
    Method for passing models_data to Momentum Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."
    momentum_backtest = BacktestClusteringPortfolio(data_models)
    momentum_backtest.process()

    return "Machine learning backtest completed and plots saved"


def run_in_and_out_of_market_backtest(data_models: ModelsData):
    """
    Method for passing models_data to Momentum Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."
    if not data_models.out_of_market_tickers:
        return "Please load out of market assets file."
    out_of_market_momentum_backtest = BacktestInAndOutMomentumPortfolio(data_models)
    out_of_market_momentum_backtest.process()

    return "Momentum backtest completed and plots saved"


def run_simulation(data_models: ModelsData):
    """
    Method for passing models_data to MonteCarlo Simulation Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(data_models)
    backtest.process()

    monte_carlo = MonteCarloSimulation(data_models)
    monte_carlo.process()

    return "Simulation completed and plot saved."


# def run_momentum_simulation(data_models: ModelsData):
#     """
#     Method for passing models_data to MonteCarlo Simulation Processor.
#     """
#     pass


# def run_machine_learning_simulation(data_models: ModelsData):
#     """
#     Method for passing models_data to MonteCarlo Simulation Processor.
#     """
#     pass


def run_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    create_signals = CreateSmaSignals(data_models)
    create_signals.process()

    return f"Signals generated for {data_models.end_date}."


def run_momentum_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    create_signals = CreateMomentumSignals(data_models)
    create_signals.process()

    return f"Signals generated for {data_models.end_date}."


def run_in_and_out_of_market_signals(data_models: ModelsData):
    """
    Method for passing models_data to Momentum Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."
    if not data_models.out_of_market_tickers:
        return "Please load out of market assets file."
    out_of_market_momentum_signals = CreateMomentumInAndOutSignals(data_models)
    out_of_market_momentum_signals.process()

    return "In and Out of market momentum signals completed and plots saved"


def run_machine_learning_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.

    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    data = utilities.fetch_data_wo_threshold(
        data_models.assets_weights,
        data_models.start_date,
        data_models.end_date,
        data_models.bond_ticker,
        data_models.cash_ticker
    )

    create_signals = CreateMLSignals(data_models, data)
    create_signals.process()

    return f"Signals generated for {data_models.end_date}."
