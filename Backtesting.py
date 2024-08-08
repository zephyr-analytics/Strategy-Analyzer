import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Utilities_Backtest import calculate_cagr, calculate_average_annual_return, calculate_max_drawdown

class BacktestStaticPortfolio:
    """
    A class to backtest a static portfolio with adjustable weights based on Simple Moving Average (SMA).

    Attributes
    ----------
    assets_weights : dict
        Dictionary containing asset tickers and their corresponding weights.
    start_date : str
        Start date for the backtest.
    end_date : str
        End date for the backtest.
    sma_period : int
        Period for calculating the Simple Moving Average.
    bond_ticker : str
        Ticker symbol for the bond asset.
    cash_ticker : str
        Ticker symbol for the cash asset.
    initial_portfolio_value : float
        Initial value of the portfolio.
    _data : DataFrame
        DataFrame to store the adjusted close prices of the assets.
    _portfolio_value : Series
        Series to store the portfolio value over time.
    _returns : Series
        Series to store the portfolio returns over time.
    """

    def __init__(self, assets_weights, start_date, end_date):
        """
        Initializes the BacktestStaticPortfolio with asset weights, start date, and end date.

        Parameters
        ----------
        assets_weights : dict
            Dictionary containing asset tickers and their corresponding weights.
        start_date : str
            Start date for the backtest.
        end_date : str
            End date for the backtest.
        """
        self.assets_weights = assets_weights
        self.start_date = start_date
        self.end_date = end_date
        self.sma_period = 168
        self.bond_ticker = 'BND'
        self.cash_ticker = 'SHV'
        self.initial_portfolio_value = 10000
        self._data = None
        self._portfolio_value = pd.Series(dtype=float)
        self._returns = pd.Series(dtype=float)

    def process(self):
        """
        Processes the backtest by fetching data, running the backtest, and plotting results.
        """
        self._data = self._fetch_data()
        self._run_backtest()
        self._plot_portfolio_value()
        self._plot_var_cvar()

    def _fetch_data(self):
        """
        Fetches historical adjusted close prices for the given assets, bond, and cash tickers.

        Returns
        -------
        DataFrame
            DataFrame containing the adjusted close prices.
        """
        all_tickers = list(self.assets_weights.keys()) + [self.bond_ticker, self.cash_ticker]
        data = yf.download(all_tickers, start=self.start_date, end=self.end_date)['Adj Close']
        return data

    def _calculate_sma(self, data):
        """
        Calculates the Simple Moving Average (SMA) for the given data.

        Parameters
        ----------
        data : DataFrame
            DataFrame containing asset prices.

        Returns
        -------
        DataFrame
            DataFrame containing the SMA values.
        """
        return data.rolling(window=self.sma_period).mean()

    def _adjust_weights(self, current_date):
        """
        Adjusts the asset weights based on SMA conditions.

        Parameters
        ----------
        current_date : datetime
            The current date for weight adjustment.

        Returns
        -------
        dict
            Dictionary containing the adjusted weights.
        """
        adjusted_weights = self.assets_weights.copy()
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
        Runs the backtest by calculating portfolio value and returns over time.
        """
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []

        for i in range(len(monthly_dates) - 1):
            current_date = monthly_dates[i]
            next_date = monthly_dates[i + 1]
            last_date_current_month = self._data.index[self._data.index.get_loc(current_date, method='pad')]
            last_date_next_month = self._data.index[self._data.index.get_loc(next_date, method='pad')]

            adjusted_weights = self._adjust_weights(last_date_current_month)
            previous_value = portfolio_values[-1]

            month_end_data = self._data.loc[last_date_next_month]
            month_start_data = self._data.loc[last_date_current_month]
            monthly_returns = (month_end_data / month_start_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)

        self._portfolio_value = pd.Series(portfolio_values, index=pd.date_range(start=self.start_date, periods=len(portfolio_values), freq='M'))
        self._returns = pd.Series(portfolio_returns, index=pd.date_range(start=self.start_date, periods=len(portfolio_returns), freq='M'))

    def _calculate_var_cvar(self, confidence_level=0.95):
        """
        Calculates the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for the portfolio returns.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level for VaR and CVaR calculation (default is 0.95).

        Returns
        -------
        tuple
            VaR and CVaR values.
        """
        sorted_returns = np.sort(self._returns.dropna())
        index = int((1 - confidence_level) * len(sorted_returns))
        var = sorted_returns[index]
        cvar = sorted_returns[:index].mean()
        return var, cvar

    def get_portfolio_value(self):
        """
        Returns the portfolio value over time.

        Returns
        -------
        Series
            Series containing the portfolio value over time.
        """
        return self._portfolio_value

    def _plot_portfolio_value(self):
        """
        Plots the portfolio value over time.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(self._portfolio_value, label='Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        plt.savefig('backtest_plot.png')  # Save the plot as an image file
        plt.close()  # Close the plot to free memory

    def _plot_var_cvar(self, confidence_level=0.95):
        """
        Plots the portfolio returns with VaR and CVaR.

        Parameters
        ----------
        confidence_level : float, optional
            Confidence level for VaR and CVaR calculation (default is 0.95).
        """
        var, cvar = self._calculate_var_cvar(confidence_level)
        cagr = calculate_cagr(self._portfolio_value)
        avg_annual_return = calculate_average_annual_return(self._returns)
        max_drawdown = calculate_max_drawdown(self._portfolio_value)

        plt.figure(figsize=(10, 6))
        plt.hist(self._returns.dropna(), bins=30, alpha=0.75, label='Returns')
        plt.axvline(var, color='r', linestyle='--', label=f'VaR ({confidence_level * 100}%): {var:.2%}')
        plt.axvline(cvar, color='g', linestyle='--', label=f'CVaR ({confidence_level * 100}%): {cvar:.2%}')
        plt.title('Portfolio Returns with VaR and CVaR')
        plt.xlabel('Returns')
        plt.ylabel('Frequency')
        plt.legend(title=(f'CAGR: {cagr:.2%}\n'
                          f'Avg Annual Return: {avg_annual_return:.2%}\n'
                          f'Max Drawdown: {max_drawdown:.2%}'))
        plt.grid(True)
        plt.savefig('CVaR_plot.png')  # Save the plot as an image file
        plt.close()  # Close the plot to free memory

# Example usage
# assets_weights = {'VTI': 0.3, 'IEI': 0.15, 'TLT': 0.4, 'GLD': 0.075, 'DBC': 0.075}
assets_weights = {'VINIX': 0.75, 'VSCIX': 0.25}
start_date = '2010-01-01'
end_date = '2024-08-01'

backtest = BacktestStaticPortfolio(assets_weights, start_date, end_date)
backtest.process()
