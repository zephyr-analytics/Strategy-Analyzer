"""
Main module for encapsulating calling processors.
"""

import utilities as utilities
from models_data import ModelsData

from models.backtesting import BacktestStaticPortfolio
from models.monte_carlo_sim import MonteCarloSimulation
from models.create_signals import CreateSignals

from momentum_models.momentum_backtest import BacktestMomentumPortfolio

from machine_learning_models.hierarchical_clustering import BacktestClusteringPortfolio

def run_backtest(data_models: ModelsData):
    """
    Method for passing models_data to Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(data_models)
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


def run_momentum_simulation(data_models: ModelsData):
    """
    Method for passing models_data to MonteCarlo Simulation Processor.
    """
    pass


def run_machine_learning_simulation(data_models: ModelsData):
    """
    Method for passing models_data to MonteCarlo Simulation Processor.
    """
    pass


def run_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    data = utilities.fetch_data(data_models.assets_weights, data_models.start_date, data_models.end_date, 
                                data_models.bond_ticker, data_models.cash_ticker)

    create_signals = CreateSignals(data_models, data)
    create_signals.process()
    
    return f"Signals generated for {data_models.end_date}."


def run_momentum_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.
    """
    pass


def run_machine_learning_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.
    """
    pass
