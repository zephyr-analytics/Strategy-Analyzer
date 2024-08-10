import utilities as utilities
from models.backtesting import BacktestStaticPortfolio
from models.monte_carlo_sim import MonteCarloSimulation
from results.results_processor import ResultsProcessor
from models.create_signals import CreateSignals

def run_backtest(assets_weights, start_date, end_date, trading_frequency, weighting_strategy, sma_window, weights_filename, bond_ticker, cash_ticker):
    if not assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(
        assets_weights, 
        start_date, 
        end_date, 
        trading_frequency, 
        output_filename=weights_filename,
        weighting_strategy=weighting_strategy,
        sma_period=int(sma_window),
        bond_ticker=bond_ticker, 
        cash_ticker=cash_ticker  
    )
    backtest.process()
    return "Backtest completed and plots saved."

def run_simulation(assets_weights, start_date, end_date, trading_frequency, weighting_strategy, sma_window, weights_filename, num_simulations, simulation_horizon, bond_ticker, cash_ticker):
    if not assets_weights:
        return "Please load asset weights file."

    backtest = BacktestStaticPortfolio(
        assets_weights, 
        start_date, 
        end_date, 
        trading_frequency, 
        output_filename=weights_filename,
        weighting_strategy=weighting_strategy,
        sma_period=int(sma_window),
        bond_ticker=bond_ticker, 
        cash_ticker=cash_ticker  
    )
    backtest.process()
    initial_value, cagr, annual_volatility = utilities.calculate_portfolio_metrics(backtest)
    monte_carlo = MonteCarloSimulation(
        initial_value, 
        cagr, 
        annual_volatility, 
        output_filename=weights_filename, 
        num_simulations=num_simulations, 
        simulation_horizon=simulation_horizon
    )
    monte_carlo.process()
    return "Simulation completed and plot saved."

def run_all_weighting_scenarios(assets_weights, start_date, end_date, trading_frequency, sma_window, weights_filename, bond_ticker, cash_ticker):
    if not assets_weights:
        return "Please load asset weights file."

    strategies = ["Use File Weights", "Equal Weight", "Risk Contribution", "Min Volatility", "Max Sharpe"]
    performance_data = {}

    for strategy in strategies:
        backtest = BacktestStaticPortfolio(
            assets_weights,
            start_date,
            end_date,
            trading_frequency,
            output_filename=weights_filename,
            weighting_strategy=strategy,
            sma_period=int(sma_window),
            bond_ticker=bond_ticker, 
            cash_ticker=cash_ticker  
        )
        backtest.process()
        performance_data[strategy] = backtest.get_portfolio_value()

    results_processor = ResultsProcessor(output_filename=weights_filename)
    results_processor.plot_all_scenarios(performance_data)
    
    return "All scenarios completed and plots saved."

def run_signals(assets_weights, start_date, end_date, trading_frequency, weighting_strategy, sma_window, weights_filename, current_date, bond_ticker, cash_ticker):
    if not assets_weights:
        return "Please load asset weights file."

    data = utilities.fetch_data(assets_weights, start_date, end_date)
    
    create_signals = CreateSignals(
        assets_weights, 
        data, 
        bond_ticker=bond_ticker,  
        cash_ticker=cash_ticker, 
        weighting_strategy=weighting_strategy, 
        sma_period=int(sma_window)
    )
    
    create_signals.generate_signals(current_date)
    
    return f"Signals generated for {current_date}."
