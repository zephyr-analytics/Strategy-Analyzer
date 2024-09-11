"""
Backtesting processor module.
"""

import pandas as pd

import utilities as utilities

from results.results_processor import ResultsProcessor
import warnings

warnings.filterwarnings("ignore")

class BacktestStaticPortfolio:
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA).

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
    _data : DataFrame or None
        DataFrame to store the adjusted closing prices of the assets.
    _portfolio_value : Series
        Series to store the portfolio values over time.
    _returns : Series
        Series to store the portfolio returns over time.
    """

    def __init__(self, data_models):
        """
        Initializes the BacktestStaticPortfolio class with data from ModelsData.

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

        # Class-defined attributes
        self._data = None


    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        self._data = utilities.fetch_data_wo_threshold(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker)
        self._run_backtest()
        self._get_portfolio_statistics()
        buy_and_hold_values, buy_and_hold_returns = self._calculate_buy_and_hold()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value(buy_and_hold_values)
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()


    def _adjust_weights(self, current_date):
        """
        Adjusts the weights of the assets based on their SMA and the selected weighting strategy.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
        """
        if self.weighting_strategy == 'Use File Weights':
            adjusted_weights = self.assets_weights.copy()
        elif self.weighting_strategy == 'Equal Weight':
            adjusted_weights = utilities.equal_weighting(self.assets_weights)
        elif self.weighting_strategy == 'Risk Contribution':
            adjusted_weights = utilities.risk_contribution_weighting(self._data.cov(), self.assets_weights)
        elif self.weighting_strategy == 'Min Volatility':
            weights = utilities.min_volatility_weighting(self._data.cov())
            adjusted_weights = dict(zip(self.assets_weights.keys(), weights))
        elif self.weighting_strategy == 'Max Sharpe':
            returns = self._data.pct_change().mean()
            weights = utilities.max_sharpe_ratio_weighting(self._data.cov(), returns)
            adjusted_weights = dict(zip(self.assets_weights.keys(), weights))
        else:
            raise ValueError("Invalid weighting strategy")
        for ticker in self.assets_weights.keys():
            if self._data.loc[:current_date, ticker].iloc[-1] < self._data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                if self._data.loc[:current_date, self.bond_ticker].iloc[-1] < self._data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                    adjusted_weights[ticker] = 0
                    adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + self.assets_weights[ticker]
                else:
                    adjusted_weights[ticker] = 0
                    adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + self.assets_weights[ticker]
        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight
        return adjusted_weights


    def _run_backtest(self):
        """
        Runs the backtest by calculating portfolio values and returns over time.
        """
        print(self.sma_period, self.cash_ticker, self.bond_ticker)
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
            adjusted_weights = self._adjust_weights(last_date_current_month)
            # adjusted_weights = self._rebalance_portfolio(adjusted_weights)
            previous_value = portfolio_values[-1]
            month_end_data = self._data.loc[last_date_current_month]
            month_start_data = month_end_data
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self._data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_start_data) - 1
            print(next_month_end_data)
            print(month_start_data)
            print(monthly_returns)
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)
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

        self.data_models.cagr = cagr
        self.data_models.average_annual_return =average_annual_return
        self.data_models.max_drawdown = max_drawdown
        self.data_models.var = var
        self.data_models.cvar = cvar
        self.data_models.annual_volatility = annual_volatility


    def _rebalance_portfolio(self, current_weights):
        """
        Rebalances the portfolio if the weights are outside their target range.

        Parameters
        ----------
        current_weights : dict
            Dictionary of current asset weights.

        Returns
        -------
        dict
            Dictionary of rebalanced asset weights.
        """
        rebalanced_weights = current_weights.copy()
        for ticker, target_weight in self.assets_weights.items():
            if abs(current_weights[ticker] - target_weight) > self.rebalance_threshold:
                rebalanced_weights[ticker] = target_weight
        total_weight = sum(rebalanced_weights.values())
        for ticker in rebalanced_weights:
            rebalanced_weights[ticker] /= total_weight

        return rebalanced_weights


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
        
        self._data = utilities.fetch_data_wo_threshold(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker)
        
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
