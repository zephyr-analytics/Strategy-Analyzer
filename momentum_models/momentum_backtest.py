import pandas as pd
import yfinance as yf
import numpy as np
import utilities
from results.results_processor import ResultsProcessor


class MomentumBacktesting:
    """
    A class to backtest a momentum-based portfolio with adjustable weights based on Simple Moving Average (SMA).

    Attributes
    ----------
    data_models : ModelsData
        An instance of the ModelsData class containing all relevant parameters and data for backtesting.
    """

    def __init__(self, data_models):
        """
        Initializes the MomentumBacktesting class with data from ModelsData.

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

        # Class-defined attributes
        self.initial_portfolio_value = 10000
        self._data = None
        self.momentum_df = None

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and generating the plots.
        """
        self._data = utilities.fetch_data(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker)
        self._run_backtest()
        self._get_portfolio_statistics()
        results_processor = ResultsProcessor(self.data_models)
        results_processor.plot_portfolio_value()
        results_processor.plot_var_cvar()
        results_processor.plot_returns_heatmaps()

    def _calculate_momentum(self):
        """
        Calculates the momentum for each asset based on multiple timeframes (1, 3, 6, 9, and 12 months).
        """
        data = (self._data.copy().pct_change() + 1)[1:].resample('M').prod() - 1
        self.momentum_df = pd.DataFrame()

        for ticker in self.assets_weights.keys():
            m1 = data[ticker].tail(1).copy()
            m3 = data[ticker].tail(3).copy()
            m6 = data[ticker].tail(6).copy()
            m9 = data[ticker].tail(9).copy()
            m12 = data[ticker].tail(12).copy()

            df_list = [m3, m6, m9, m12]
            for df in df_list:
                df[ticker] = ((1 + df).cumprod() - 1) * 100

            momentum_matrix = pd.concat([m1.tail(1), m3.tail(1), m6.tail(1), m9.tail(1), m12.tail(1)], axis=0)
            momentum_matrix = momentum_matrix.mean(axis=0)
            self.momentum_df[ticker] = momentum_matrix

        self.momentum_df = self.momentum_df.T

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
        # Momentum Calculation
        self._calculate_momentum()

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

        # Momentum-based Adjustment: Only select assets with positive momentum
        for ticker in self.assets_weights.keys():
            if self.momentum_df.loc[ticker].mean() <= 0:
                adjusted_weights[ticker] = 0

        # Reallocation based on SMA
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

        for i in range(0, len(monthly_dates) - 1, step):
            current_date = monthly_dates[i]
            next_date = monthly_dates[min(i + step, len(monthly_dates) - 1)]
            last_date_current_month = self._data.index[self._data.index.get_loc(current_date, method='pad')]
            adjusted_weights = self._adjust_weights(last_date_current_month)
            previous_value = portfolio_values[-1]
            month_end_data = self._data.loc[last_date_current_month]
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]
            next_month_end_data = self._data.loc[last_date_next_month]
            monthly_returns = (next_month_end_data / month_end_data) - 1
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
        self.data_models.average_annual_return = average_annual_return
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
