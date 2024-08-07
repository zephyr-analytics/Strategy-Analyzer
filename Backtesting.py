import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class BacktestStaticPortfolio:
    def __init__(self, assets_weights, start_date, end_date):
        self.assets_weights = assets_weights
        self.start_date = start_date
        self.end_date = end_date
        self.sma_period = 168
        self.bond_ticker = 'BND'
        self.cash_ticker = 'SHV'
        self.initial_portfolio_value = 10000
        self.data = None
        self.portfolio_value = pd.Series(dtype=float)
        self.returns = pd.Series(dtype=float)
    
    def process(self):
        self.data = self.fetch_data()
        self.run_backtest()
        self.plot_portfolio_value()
        self.plot_var_cvar()


    def fetch_data(self):
        all_tickers = list(self.assets_weights.keys()) + [self.bond_ticker, self.cash_ticker]
        data = yf.download(all_tickers, start=self.start_date, end=self.end_date)['Adj Close']
        return data
    

    def calculate_sma(self, data):
        return data.rolling(window=self.sma_period).mean()
    

    def adjust_weights(self, current_date):
        adjusted_weights = self.assets_weights.copy()
        for ticker in self.assets_weights.keys():
            if self.data.loc[:current_date, ticker].iloc[-1] < self.data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                if self.data.loc[:current_date, self.bond_ticker].iloc[-1] < self.data.loc[:current_date, self.bond_ticker].rolling(window=self.sma_period).mean().iloc[-1]:
                    adjusted_weights[ticker] = 0
                    adjusted_weights[self.cash_ticker] = adjusted_weights.get(self.cash_ticker, 0) + self.assets_weights[ticker]
                else:
                    adjusted_weights[ticker] = 0
                    adjusted_weights[self.bond_ticker] = adjusted_weights.get(self.bond_ticker, 0) + self.assets_weights[ticker]
        
        total_weight = sum(adjusted_weights.values())
        for ticker in adjusted_weights:
            adjusted_weights[ticker] /= total_weight
        return adjusted_weights
    

    def run_backtest(self):
        monthly_dates = pd.date_range(start=self.start_date, end=self.end_date, freq='M')
        portfolio_values = [self.initial_portfolio_value]
        portfolio_returns = []

        for i in range(len(monthly_dates) - 1):
            current_date = monthly_dates[i]
            next_date = monthly_dates[i + 1]
            last_date_current_month = self.data.index[self.data.index.get_loc(current_date, method='pad')]
            last_date_next_month = self.data.index[self.data.index.get_loc(next_date, method='pad')]
            
            adjusted_weights = self.adjust_weights(last_date_current_month)
            previous_value = portfolio_values[-1]
            
            month_end_data = self.data.loc[last_date_next_month]
            month_start_data = self.data.loc[last_date_current_month]
            monthly_returns = (month_end_data / month_start_data) - 1
            month_return = sum([monthly_returns[ticker] * weight for ticker, weight in adjusted_weights.items()])
            new_portfolio_value = previous_value * (1 + month_return)
            portfolio_values.append(new_portfolio_value)
            portfolio_returns.append(month_return)
        
        self.portfolio_value = pd.Series(portfolio_values, index=pd.date_range(start=self.start_date, periods=len(portfolio_values), freq='M'))
        self.returns = pd.Series(portfolio_returns, index=pd.date_range(start=self.start_date, periods=len(portfolio_returns), freq='M'))
    

    def calculate_var_cvar(self, confidence_level=0.95):
        sorted_returns = np.sort(self.returns.dropna())
        index = int((1 - confidence_level) * len(sorted_returns))
        var = sorted_returns[index]
        cvar = sorted_returns[:index].mean()
        return var, cvar
    

    def calculate_cagr(self):
        total_period = (self.portfolio_value.index[-1] - self.portfolio_value.index[0]).days / 365.25
        cagr = (self.portfolio_value.iloc[-1] / self.portfolio_value.iloc[0]) ** (1 / total_period) - 1
        return cagr
    

    def calculate_average_annual_return(self):
        average_monthly_return = self.returns.mean()
        average_annual_return = (1 + average_monthly_return) ** 12 - 1
        return average_annual_return
    

    def calculate_max_drawdown(self):
        running_max = self.portfolio_value.cummax()
        drawdown = (self.portfolio_value - running_max) / running_max
        max_drawdown = drawdown.min()
        return max_drawdown
    

    def get_portfolio_value(self):
        return self.portfolio_value
    

    def plot_portfolio_value(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.portfolio_value, label='Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    
    def plot_var_cvar(self, confidence_level=0.95):
        var, cvar = self.calculate_var_cvar(confidence_level)
        cagr = self.calculate_cagr()
        avg_annual_return = self.calculate_average_annual_return()
        max_drawdown = self.calculate_max_drawdown()
        
        plt.figure(figsize=(10, 6))
        plt.hist(self.returns.dropna(), bins=30, alpha=0.75, label='Returns')
        plt.axvline(var, color='r', linestyle='--', label=f'VaR ({confidence_level * 100}%): {var:.2%}')
        plt.axvline(cvar, color='g', linestyle='--', label=f'CVaR ({confidence_level * 100}%): {cvar:.2%}')
        plt.title('Portfolio Returns with VaR and CVaR')
        plt.xlabel('Returns')
        plt.ylabel('Frequency')
        plt.legend(title=(f'CAGR: {cagr:.2%}\n'
                          f'Avg Annual Return: {avg_annual_return:.2%}\n'
                          f'Max Drawdown: {max_drawdown:.2%}'))
        plt.grid(True)
        plt.show()


assets_weights = {'VINIX': 0.7, 'VSCIX': 0.3}
# assets_weights = {'VTI': 0.3, 'TLT': 0.4, 'IEI': 0.15, 'GLD': 0.075, 'DBC': 0.075}
start_date = '2010-01-01'
end_date = '2024-08-01'

backtest = BacktestStaticPortfolio(assets_weights, start_date, end_date)
backtest.process()
