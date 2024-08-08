import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go

import utilities as utilities

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

    def __init__(self, assets_weights, start_date, end_date):
        """
        Initializes the BacktestStaticPortfolio class with given asset weights, start date, and end date.

        Parameters
        ----------
        assets_weights : dict
            Dictionary of asset tickers and their corresponding weights in the portfolio.
        start_date : str
            The start date for the backtest.
        end_date : str
            The end date for the backtest.
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
        Processes the backtest by fetching data and running the backtest.
        """
        self._data = utilities.fetch_data(self.assets_weights, self.start_date, self.end_date, self.bond_ticker, self.cash_ticker)
        self._run_backtest()

    def _adjust_weights(self, current_date):
        """
        Adjusts the weights of the assets based on their SMA.

        Parameters
        ----------
        current_date : datetime
            The current date for which the weights are being adjusted.

        Returns
        -------
        dict
            Dictionary of adjusted asset weights.
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
        Runs the backtest by calculating portfolio values and returns over time.
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
        Calculates the Value at Risk (VaR) and Conditional Value at Risk (CVaR) of the portfolio.

        Parameters
        ----------
        confidence_level : float, optional
            The confidence level for calculating VaR and CVaR. Default is 0.95.

        Returns
        -------
        tuple
            Tuple containing VaR and CVaR values.
        """
        sorted_returns = np.sort(self._returns.dropna())
        index = int((1 - confidence_level) * len(sorted_returns))
        var = sorted_returns[index]
        cvar = sorted_returns[:index].mean()
        return var, cvar


    def get_portfolio_value(self):
        """
        Returns the portfolio value series.

        Returns
        -------
        Series
            Series containing the portfolio values over time.
        """
        return self._portfolio_value

    def plot_portfolio_value(self, filename='portfolio_value.html'):
        """
        Plots the portfolio value over time and saves the plot as an HTML file.
        """
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self._portfolio_value.index, y=self._portfolio_value, mode='lines', name='Portfolio Value'))
        fig.update_layout(title='Portfolio Value Over Time', xaxis_title='Date', yaxis_title='Portfolio Value ($)')
        utilities.save_html(fig, filename)


    def plot_var_cvar(self, confidence_level=0.95, filename='var_cvar.html'):
        """
        Plots the portfolio returns with VaR and CVaR and saves the plot as an HTML file.

        Parameters
        ----------
        confidence_level : float, optional
            The confidence level for calculating VaR and CVaR. Default is 0.95.
        filename : str, optional
            The name of the HTML file to save the plot. Default is 'var_cvar.html'.
        """
        var, cvar = self._calculate_var_cvar(confidence_level)
        cagr = utilities.calculate_cagr(self._portfolio_value)
        avg_annual_return = utilities.calculate_average_annual_return(self._returns)
        max_drawdown = utilities.calculate_max_drawdown(self._portfolio_value)

        fig = go.Figure()

        fig.add_trace(go.Histogram(x=self._returns.dropna(), nbinsx=30, name='Returns', opacity=0.75, marker_color='blue'))

        fig.add_shape(type="line",
                    x0=var, y0=0, x1=var, y1=1,
                    line=dict(color="Red", dash="dash"),
                    xref='x', yref='paper',
                    name=f'VaR ({confidence_level * 100}%): {var:.2%}')
        fig.add_shape(type="line",
                    x0=cvar, y0=0, x1=cvar, y1=1,
                    line=dict(color="Green", dash="dash"),
                    xref='x', yref='paper',
                    name=f'CVaR ({confidence_level * 100}%): {cvar:.2%}')

        fig.update_layout(
            title='Portfolio Returns with VaR and CVaR',
            xaxis_title='Returns',
            yaxis_title='Frequency',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.3,
                xanchor="center",
                x=0.5
            ),
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.25,
                    xanchor='center', yanchor='bottom',
                    text=f'CAGR: {cagr:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.2,
                    xanchor='center', yanchor='bottom',
                    text=f'Avg Annual Return: {avg_annual_return:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.15,
                    xanchor='center', yanchor='bottom',
                    text=f'Max Drawdown: {max_drawdown:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.1,
                    xanchor='center', yanchor='bottom',
                    text=f'VaR ({confidence_level * 100}%): {var:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.05,
                    xanchor='center', yanchor='bottom',
                    text=f'CVaR ({confidence_level * 100}%): {cvar:.2%}',
                    showarrow=False
                )
            ]
        )
        utilities.save_html(fig, filename)