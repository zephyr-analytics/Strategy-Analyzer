import utilities as utilities

from models.backtesting import BacktestStaticPortfolio
from models.monte_carlo_sim import MonteCarloSimulation
from results.results_processor import ResultsProcessor
from models.create_signals import CreateSignals
from models_data import ModelsData

def run_backtest(data_models: ModelsData):
    if not data_models.assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(
        data_models.assets_weights,
        data_models.start_date,
        data_models.end_date,
        data_models.trading_frequency,
        output_filename=data_models.weights_filename,
        weighting_strategy=data_models.weighting_strategy,
        sma_period=int(data_models.sma_window),
        bond_ticker=data_models.bond_ticker,
        cash_ticker=data_models.cash_ticker
    )
    backtest.process()
    return "Backtest completed and plots saved."

def run_simulation(data_models: ModelsData):
    if not data_models.assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(
        data_models.assets_weights,
        data_models.start_date,
        data_models.end_date,
        data_models.trading_frequency,
        output_filename=data_models.weights_filename,
        weighting_strategy=data_models.weighting_strategy,
        sma_period=int(data_models.sma_window),
        bond_ticker=data_models.bond_ticker,
        cash_ticker=data_models.cash_ticker
    )
    backtest.process()
    initial_value, cagr, annual_volatility = utilities.calculate_portfolio_metrics(backtest)
    monte_carlo = MonteCarloSimulation(
        initial_value,
        cagr,
        annual_volatility,
        output_filename=data_models.weights_filename,
        num_simulations=data_models.num_simulations,
        simulation_horizon=data_models.simulation_horizon
    )
    monte_carlo.process()
    return "Simulation completed and plot saved."

def run_all_weighting_scenarios(data_models: ModelsData):
    if not data_models.assets_weights:
        return "Please load asset weights file."

    strategies = ["Use File Weights", "Equal Weight", "Risk Contribution", "Min Volatility", "Max Sharpe"]
    performance_data = {}

    for strategy in strategies:
        backtest = BacktestStaticPortfolio(
            data_models.assets_weights,
            data_models.start_date,
            data_models.end_date,
            data_models.trading_frequency,
            output_filename=data_models.weights_filename,
            weighting_strategy=strategy,
            sma_period=int(data_models.sma_window),
            bond_ticker=data_models.bond_ticker,
            cash_ticker=data_models.cash_ticker
        )
        backtest.process()
        performance_data[strategy] = backtest.get_portfolio_value()

    results_processor = ResultsProcessor(output_filename=data_models.weights_filename)
    results_processor.plot_all_scenarios(performance_data)
    
    return "All scenarios completed and plots saved."

def run_signals(data_models: ModelsData):
    if not data_models.assets_weights:
        return "Please load asset weights file."

    data = utilities.fetch_data(data_models.assets_weights, data_models.start_date, data_models.end_date)
    
    create_signals = CreateSignals(
        data_models.assets_weights,
        data,
        bond_ticker=data_models.bond_ticker,
        cash_ticker=data_models.cash_ticker,
        weighting_strategy=data_models.weighting_strategy,
        sma_period=int(data_models.sma_window)
    )
    
    create_signals.generate_signals(data_models.end_date)
    
    return f"Signals generated for {data_models.end_date}."
