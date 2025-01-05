# Portfolio Strategy Analyzer
## This application was built using Python 3.10.1 and will require an instance of Python installed on your computer to run.

## Overview
This application is designed for comprehensive portfolio analysis.
Backtesting is incororated to demostrate how the portfolio and trading parameters have performed historically. 
Monte Carlo Simualation has been introduced for being able to model how it will perform moving forward in time. 

### Features

#### **Backtesting**  
Evaluate portfolio performance with flexible parameters such as trading frequency, SMA windows, and asset weighting strategies.
- **Moving Average**  
Use MA-based strategies to guide asset selection and trading decisions by analyzing price trends over time.
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

### 3. **Backtest Settings**
#### Data Settings:
  - **Initial Portfolio Value**: The starting value of the portfolio. (Default: `$10,000`)
  - **In market assets**: Select the .csv file containing the assets for trading when above ma.
  - **Out of market assets**: Select the .csv file containing the assets for trading when below ma.
  - **Start Date**: The start date for the backtest in `'YYYY-MM-DD'` format. (Default: `'2010-01-01'`)
  - **End Date**: The end date for the backtest in `'YYYY-MM-DD'` format. (Default: Today's date)
  - **Cash Ticker**: Ticker for the cash asset. (Default: `'SHV'`)
  - **Bond Ticker**: Ticker for the bond asset.
  - **Obtain Data**: When pressed will fetch the data based on the current settings.

#### Trade Settings:
  - **Benchmark Asset**: Asset used to compare trading model returns to.
  - **Trading Frequency**: The frequency at which the portfolio strategy is reset. (Default: `'Monthly'`)

#### Moving Average Settings
  - **Moving Average Window**: The moving average window for generating signals. (trading days)
  - **Moving Average Threshold Asset**: An optional asset whose moving average is used as a benchmark for trading signals.
  - **Moving Average Type**: The type of moving average preferred by the user. (Either `EMA` or `SMA`)

#### Momentum Settings:
  - **Number of Assets to Select**: Specifies the number of assets to include based on momentum. (Default: `1`)
  - **Remove Negative Momentum**: Removes assets with negative momentum when creating the trading model.

#### Simulation Parameters:
  - **Number of Simulations**: Number of Monte Carlo simulation paths. (Default: `1000`)
  - **Simulation Horizon**: Time horizon for simulations in years. (Default: `10`)
  - **Contribution**: Optional periodic contribution to the portfolio during simulations. (Default: `None`)
  - **Contribution Frequency**: Frequency of contributions (e.g., `'Monthly'`, `'Quarterly'`, `'Yearly'`). (Default: `None`)

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
