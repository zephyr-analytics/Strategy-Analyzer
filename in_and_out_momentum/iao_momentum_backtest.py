"""
Module for backtesting in and out of market momentum assets.
"""

import pandas as pd

import utilities as utilities
from results.results_processor import ResultsProcessor

import warnings
warnings.filterwarnings("ignore")

class BacktestInAndOutMomentumPortfolio:
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA),
    with momentum calculations for both in-market and out-of-market assets.

    Attributes
    ----------
    assets_weights : dict
        Dictionary of asset tickers and their corresponding weights in the portfolio.
    start_date : str
        The start date for the backtest.
    end_date : str
        The end date for the backtest.
    sma_period : int
        The period for calculating the Simple Moving Average (SMA). Default is 168.
    bond_ticker : str
        The ticker symbol for the bond asset. Default is 'BND'.
    cash_ticker : str
        The ticker symbol for the cash asset. Default is 'SHV'.
    initial_portfolio_value : float
        The initial value of the portfolio. Default is 10000.
    out_of_market_tickers : str
        The ticker symbol for the out-of-market asset.
    _data : DataFrame or None
        DataFrame to store the adjusted closing prices of the in-market assets.
    _out_of_market_data : DataFrame or None
        DataFrame to store the adjusted closing prices of the out-of-market assets.
    _portfolio_value : Series
        Series to store the portfolio values over time.
    _returns : Series
        Series to store the portfolio returns over time.
    _momentum_data : DataFrame
        DataFrame to store the returns data for calculating momentum of in-market assets.
    _momentum_data_out_of_market : DataFrame
        DataFrame to store the returns data for calculating momentum of out-of-market assets.
    """

    def __init__(self, data_models):
        """
        Initializes the BacktestMomentumPortfolio class with data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all relevant parameters and data for backtesting.
        """
        self.data_models = data_models

        self.assets_weights = data_models.assets_weights
        self.start_date = data_models.start_date
        self.end_date = data_models.end_date
        self.trading_frequency = data_models.trading_frequency
        self.output_filename = data_models.weights_filename
        self.rebalance_threshold = 0.02
        self.weighting_strategy = data_models.weighting_strategy
        self.sma_period = int(data_models.sma_window)
        self.bond_ticker = data_models.bond_ticker
        self.cash_ticker = data_models.cash_ticker
        self.initial_portfolio_value = int(data_models.initial_portfolio_value)
        self.num_assets_to_select = int(data_models.num_assets_to_select)
        self.threshold_asset = str(data_models.threshold_asset)
        self.out_of_market_tickers = data_models.out_of_market_tickers

        # Class-defined attributes
        self._data = None  # In-market assets data
        self._out_of_market_data = None  # Out-of-market assets data
        self._momentum_data = None  # In-market momentum data
        self._momentum_data_out_of_market = None  # Out-of-market momentum data

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        print(f"Threshold Asset: {self.threshold_asset}")
        print(f"Bond Asset: {self.bond_ticker}")
        print(f"Out-of-Market Asset: {self.out_of_market_tickers}")
        
        # Fetch in-market and out-of-market data
        if self.threshold_asset == "":
            self._data = utilities.fetch_data_wo_threshold(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker)
            self._out_of_market_data = utilities.fetch_out_of_market_data(self.out_of_market_tickers, self.start_date, self.end_date)
        else:
            self._data = utilities.fetch_data_w_threshold(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker, self.threshold_asset)
            self._out_of_market_data = utilities.fetch_out_of_market_data(self.out_of_market_tickers, self.start_date, self.end_date)

        # Calculate momentum for both in-market and out-of-market assets
        self._momentum_data = self._data.copy().pct_change().dropna()
        self._momentum_data_out_of_market = self._out_of_market_data.copy().pct_change().dropna()

        self._run_backtest()
        self._get_portfolio_statistics()
        buy_and_hold_values, buy_and_hold_returns = self._calculate_buy_and_hold()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value(buy_and_hold_values)
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()

    def calculate_momentum(self, current_date):
        """Calculate average momentum based on 1, 3, 6, 9, and 12-month cumulative returns for both in-market and out-of-market assets."""
        # In-market asset momentum
        momentum_1m = (self._momentum_data.loc[:current_date].iloc[-21:] + 1).prod() - 1
        momentum_3m = (self._momentum_data.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m = (self._momentum_data.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m = (self._momentum_data.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m = (self._momentum_data.loc[:current_date].iloc[-252:] + 1).prod() - 1
        in_market_momentum = (momentum_1m + momentum_3m + momentum_6m + momentum_9m + momentum_12m) / 5

        # Out-of-market asset momentum
        momentum_1m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-21:] + 1).prod() - 1
        momentum_3m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-63:] + 1).prod() - 1
        momentum_6m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-126:] + 1).prod() - 1
        momentum_9m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-189:] + 1).prod() - 1
        momentum_12m_out = (self._momentum_data_out_of_market.loc[:current_date].iloc[-252:] + 1).prod() - 1
        out_of_market_momentum = (momentum_1m_out + momentum_3m_out + momentum_6m_out + momentum_9m_out + momentum_12m_out) / 5

        return in_market_momentum, out_of_market_momentum

    def _adjust_weights(self, current_date, selected_assets, selected_out_of_market_assets):
        """
        Adjusts the weights of the selected assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.
        selected_assets : DataFrame
            DataFrame of selected in-market assets and their weights.
        selected_out_of_market_assets : DataFrame
            DataFrame of selected out-of-market assets and their weights.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        adjusted_weights = {}

        # In-Market assets weight adjustments based on SMA
        for ticker in selected_assets['Asset']:
            asset_price = self._data.loc[:current_date, ticker].iloc[-1]
            asset_sma = self._data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]

            if asset_price >= asset_sma:
                adjusted_weights[ticker] = 1 / len(selected_assets)  # Equal weight if above SMA
            else:
                # Check out-of-market assets when in-market asset is below SMA
                all_below_sma = True  # Assume all out-of-market assets are below their SMA
                highest_momentum_asset = None
                highest_momentum_value = float('-inf')

                for out_ticker, momentum in zip(selected_out_of_market_assets['Asset'], selected_out_of_market_assets['Momentum']):
                    out_asset_price = self._out_of_market_data.loc[:current_date, out_ticker].iloc[-1]
                    out_asset_sma = self._out_of_market_data.loc[:current_date, out_ticker].rolling(window=self.sma_period).mean().iloc[-1]

                    if out_asset_price >= out_asset_sma:
                        all_below_sma = False  # Found at least one out-of-market asset above SMA
                        if momentum > highest_momentum_value:
                            highest_momentum_value = momentum
                            highest_momentum_asset = out_ticker

                if all_below_sma:
                    # Move to cash if all out-of-market assets are below their SMAs
                    adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + (1 / len(selected_assets))
                else:
                    # Allocate to the out-of-market asset with the highest momentum
                    adjusted_weights[highest_momentum_asset] = adjusted_weights.get(highest_momentum_asset, 0) + (1 / len(selected_assets))

        # Normalize weights to ensure they sum to 1
        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight

        print(f'{current_date}: Adjusted Weights: {adjusted_weights}')
        return adjusted_weights


    def _run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []
        
        if self.trading_frequency == 'Monthly':
            step = 1
        elif self.trading_frequency == 'Bi-Monthly':
            step = 2
        else:
            raise ValueError("Invalid trading frequency. Choose 'Monthly' or 'Bi-Monthly'.")

        for i in range(0, len(monthly_dates), step):
            current_date = monthly_dates[i]
            next_date = monthly_dates[min(i + step, len(monthly_dates) - 1)]
            last_date_current_month = self._data.index[self._data.index.get_loc(current_date, method='pad')]

            # Calculate momentum for both in-market and out-of-market assets
            in_market_momentum, out_of_market_momentum = self.calculate_momentum(last_date_current_month)

            # Select top assets based on momentum
            selected_assets = pd.DataFrame({'Asset': in_market_momentum.nlargest(self.num_assets_to_select).index,
                                            'Momentum': in_market_momentum.nlargest(self.num_assets_to_select).values})
            selected_out_of_market_assets = pd.DataFrame({'Asset': out_of_market_momentum.nlargest(self.num_assets_to_select).index,
                                                          'Momentum': out_of_market_momentum.nlargest(self.num_assets_to_select).values})

            # Adjust weights based on selected assets and SMA
            adjusted_weights = self._adjust_weights(last_date_current_month, selected_assets, selected_out_of_market_assets)

            previous_value = portfolio_values[-1]
            month_end_data = self._data.loc[last_date_current_month]
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self._data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_end_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self.data_models.adjusted_weights = adjusted_weights
        self.data_models.portfolio_values = pd.Series(portfolio_values, index=pd.date_range(start=self.start_date, periods=len(portfolio_values), freq='M'))
        self.data_models.portfolio_returns = pd.Series(portfolio_returns, index=pd.date_range(start=self.start_date, periods=len(portfolio_returns), freq='M'))


    def _get_portfolio_statistics(self):
        """
        Calculates and sets portfolio statistics such as CAGR, average annual return, max drawdown, VaR, and CVaR in models_data.
        """
        cagr = utilities.calculate_cagr(self.data_models.portfolio_values, self.trading_frequency)
        average_annual_return = utilities.calculate_average_annual_return(self.data_models.portfolio_returns, self.trading_frequency)
        max_drawdown = utilities.calculate_max_drawdown(self.data_models.portfolio_values)
        var, cvar = utilities.calculate_var_cvar(self.data_models.portfolio_returns)
        annual_volatility = utilities.calculate_annual_volatility(self.trading_frequency, self.data_models.portfolio_returns)
        standard_deviation = utilities.calculate_standard_deviation(self.data_models.portfolio_returns)

        self.data_models.cagr = cagr
        self.data_models.average_annual_return = average_annual_return
        self.data_models.max_drawdown = max_drawdown
        self.data_models.var = var
        self.data_models.cvar = cvar
        self.data_models.annual_volatility = annual_volatility
        self.data_models.standard_deviation = standard_deviation

    def _calculate_buy_and_hold(self):
        """
        Calculates the buy-and-hold performance of the portfolio with the same assets and weights over the time frame.
        
        Returns
        -------
        buy_and_hold_values : Series
            Series representing the portfolio value over time following a buy-and-hold strategy.
        buy_and_hold_returns : Series
            Series representing the portfolio returns over time following a buy-and-hold strategy.
        """
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')

        for i in range(1, len(monthly_dates)):
            start_index = self._data.index.get_indexer([monthly_dates[i-1]], method='nearest')[0]
            end_index = self._data.index.get_indexer([monthly_dates[i]], method='nearest')[0]
            start_data = self._data.iloc[start_index]
            end_data = self._data.iloc[end_index]

            previous_value = portfolio_values[-1]
            monthly_returns = (end_data / start_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in self.assets_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        buy_and_hold_values = pd.Series(portfolio_values, index=monthly_dates[:len(portfolio_values)])
        buy_and_hold_returns = pd.Series(portfolio_returns, index=monthly_dates[1:len(portfolio_returns)+1])

        return buy_and_hold_values, buy_and_hold_returns

