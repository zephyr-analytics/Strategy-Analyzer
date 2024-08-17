# Portfolio Strategy Analyzer

## Overview

This application is designed for comprehensive portfolio analysis, incorporating backtesting, Monte Carlo simulations, and signal generation. The application supports multiple weighting strategies, theme selection, and various portfolio analysis tasks, making it a versatile tool for financial analysis.

## Features

- **Backtesting**: Perform backtests on static portfolios with customizable parameters like trading frequency, SMA window, and weighting strategy.
- **Monte Carlo Simulation**: Run simulations to project future portfolio values based on historical data.
- **Signal Generation**: Generate and visualize trading signals based on moving averages and asset weights.

## Inputs

### 1. **Asset Weights**
   - **Description**: Load asset weights from a CSV file to use in portfolio analysis.
   - **Example**: 
     ```
     Ticker,Weight
     AAPL,0.3
     MSFT,0.2
     GOOGL,0.5
     ```

### 2. **Historical Data**
   - **Description**: The application fetches historical stock data using `yfinance`. Ensure that the necessary tickers are correctly specified in the asset weights file.
   - **Example**: No manual input required; data is fetched automatically.

### 3. **Backtest Parameters**
   - **Start Date**: The start date for the backtest.
   - **End Date**: The end date for the backtest.
   - **Cash Ticker**: Ticker for cash asset. ('SGOV')
   - **Bond Ticker**: Ticker for bond asset. ('BND')
   - **Trading Frequency**: The frequency at which the portfolio is strategy is reset.
   - **Weighting Strategy**: The strategy for weighting assets (e.g., 'Equal Weight', 'Risk Contribution').
   - **SMA Window**: The Simple Moving Average window for generating signals.

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
