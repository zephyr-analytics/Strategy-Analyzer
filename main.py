"""
Main module for encapsulating calling processors.
"""

import utilities as utilities
from models_data import ModelsData

from models.backtesting import BacktestStaticPortfolio
from models.monte_carlo_sim import MonteCarloSimulation
from models.create_signals import CreateSignals

def run_backtest(data_models: ModelsData):
    """
    Method for passing models_data to Backtest Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(data_models)
    backtest.process()
    return "Backtest completed and plots saved."

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

def run_signals(data_models: ModelsData):
    """
    Method for passing models_data to Create Signals Processor.
    """
    if not data_models.assets_weights:
        return "Please load asset weights file."

    data = utilities.fetch_data(data_models.assets_weights, data_models.start_date, data_models.end_date)

    create_signals = CreateSignals(data_models, data)
    create_signals.process()
    
    return f"Signals generated for {data_models.end_date}."
