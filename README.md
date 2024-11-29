# Portfolio Strategy Analyzer

## This application was built using Python 3.10.1 and will require an instance of Python installed on your computer to run.
## Additionally, a requirements file is also attached and those may also be necessary to run the application, depending on system environment.

## Overview
This application is designed for comprehensive portfolio analysis. Backtesting is incororated to demostrate how the portfolio and trading parameters
have performed historically. Monte Carlo Simualation has been introduced for being able to model how it will perform moving forward in time. 

### Features

#### **Backtesting**  
Evaluate portfolio performance with flexible parameters such as trading frequency, SMA windows, and asset weighting strategies.
- **Simple Moving Average (SMA)**  
Use SMA-based strategies to guide asset selection and trading decisions by analyzing price trends over time.
- **Momentum**  
Incorporate momentum strategies to identify high-performing assets based on historical returns and optimize portfolio composition.

#### **Monte Carlo Simulation**  
Simulate potential future portfolio outcomes using historical data, accounting for different scenarios and risk metrics.

#### **Signal Generation**  
Generate trading signals and visualize market opportunities through automated moving average and weight-based analyses. 

## Inputs

### 1. **Asset Weights**
   - **Description**: Load asset weights from a CSV file to use in portfolio analysis.
   - **Example**: 
     ```
     Ticker,Weight
     VTI,0.3
     IAU,0.2
     BND,0.5
     ```

### 2. **Historical Data**
   - **Description**: The application fetches historical stock data using `yfinance`. Ensure that the necessary tickers are correctly specified in the asset weights file.

### 3. **Backtest Parameters**
- **Start Date**: The start date for the backtest. (Default: `'2010-01-01'`)
- **End Date**: The end date for the backtest. (Default: Today's date in `'YYYY-MM-DD'` format)
- **Initial Portfolio Value**: The starting value of the portfolio. (Default: `$10,000`)
- **Cash Ticker**: Ticker for the cash asset. (Default: `'SGOV'`)
- **Bond Ticker**: Ticker for the bond asset. (Default: `'BND'`)
- **Trading Frequency**: The frequency at which the portfolio strategy is reset. (Default: `'Monthly'`)
- **Weighting Strategy**: The strategy for weighting assets. (Default: `'Use File Weights'`. Options: `'Equal Weight'`, `'Risk Contribution'`, etc.)
- **SMA Window**: The Simple Moving Average window for generating signals. (Default: `21` trading days)
- **Threshold Asset**: An optional asset whose SMA is used as a benchmark for trading signals. (Default: `None`)
- **Out of Market Assets**: Assets and weights used for constructing an out-of-market momentum trading strategy. (Default: `{}`)
- **Number of Assets to Select**: Specifies the number of assets to include based on momentum. (Default: `1`)
- **Benchmark Asset**: An optional asset used as a benchmark for performance comparison. (Default: `None`)
- **Contribution**: Optional periodic contribution to the portfolio during simulations. (Default: `None`)
- **Contribution Frequency**: Frequency of contributions (e.g., `'Monthly'`, `'Quarterly'`, `'Yearly'`). (Default: `None`)
- **Simulation Parameters**:
  - **Number of Simulations**: Number of Monte Carlo simulation paths. (Default: `1000`)
  - **Simulation Horizon**: Time horizon for simulations in years. (Default: `10`)
- **Risk Metrics**:
  - **CAGR (Compound Annual Growth Rate)**: Calculated during backtests.
  - **Max Drawdown**: The largest peak-to-trough decline observed.
  - **Annual Volatility**: Measure of the portfolio's annualized risk.
  - **VaR (Value at Risk)**: The portfolio's estimated worst loss at a given confidence level.
  - **CVaR (Conditional Value at Risk)**: The expected loss in the worst-case scenarios.

## Example Usage

### Running a Backtest

1. Load the asset weights file (e.g., `weights.csv`).
2. Set the backtest parameters.
3. Run the backtest via the GUI.

### Performing Monte Carlo Simulation

1. Set the simulation parameters, such as the number of simulations and the time horizon.
2. Run the simulation and view the results in the GUI.

### Generating Signals

1. Set the SMA window for generating signals.
2. Run the signal generation process and view the signals plotted in the GUI.
