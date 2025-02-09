import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

class InstitutionalBacktest:
    def __init__(self, tickers, risk_free_ticker, start, end, initial_weights=None, starting_value=10000):
        """
        tickers: List of asset tickers to fetch data for
        risk_free_ticker: Ticker for the risk-free rate (e.g., treasury bills)
        start: Start date for data retrieval
        end: End date for data retrieval
        initial_weights: Dictionary of initial portfolio weights (optional)
        starting_value: Initial portfolio value
        """
        self.tickers = tickers
        self.risk_free_ticker = risk_free_ticker
        self.start = start
        self.end = end
        self.starting_value = starting_value
        self.fetch_data()
        self.returns = self.price_data.pct_change()

        if initial_weights:
            self.initial_weights = initial_weights
        else:
            self.initial_weights = {ticker: 1 / len(self.tickers) for ticker in self.tickers}
        
        self.portfolio_weights = None

    def fetch_data(self):
        """ Fetch monthly asset and risk-free rate data from Yahoo Finance. """
        self.price_data = yf.download(self.tickers, start=self.start, end=self.end, interval='1mo')['Adj Close']
        risk_free_data = yf.download(self.risk_free_ticker, start=self.start, end=self.end, interval='1mo')['Adj Close']
        self.risk_free_rate = risk_free_data.pct_change().fillna(0)

    def calculate_momentum(self, periods=[1, 3, 6, 9, 12]):
        """ Calculate the momentum factor as the average past returns over given periods (months). """
        momentum_scores = sum([self.returns.rolling(window=p).mean() for p in periods]) / len(periods)

        return momentum_scores

    def calculate_excess_return(self, periods=[1, 3, 6, 9, 12]):
        """ 
        Calculate the excess return factor over the risk-free rate.
        Adjusts the sign properly when aggregating rolling averages.
        """
        excess_returns = self.returns.sub(self.risk_free_rate, axis=0)

        excess_return_scores = sum(
            [np.sign(excess_returns) * excess_returns.abs().rolling(window=p).mean() for p in periods]
        ) / len(periods)

        return excess_return_scores

    def calculate_sma_filter(self, period=8):
        """ Identify assets trading above their 12-month simple moving average. """
        sma = self.price_data.rolling(window=period).mean()

        return self.price_data > sma

    def adjust_weights(self, date):
        """ Adjust portfolio weights based on the three factors for a specific month, starting with initial weights. """
        momentum = self.calculate_momentum().loc[date]
        excess_return = self.calculate_excess_return().loc[date]
        above_sma = self.calculate_sma_filter().loc[date]

        final_weights = pd.Series(self.initial_weights).copy()

        available_assets = momentum.index.intersection(final_weights.index)
        final_weights = final_weights.loc[available_assets]

        # Step: Move weights to risk-free asset if excess return is negative BEFORE ranking adjustments
        excess_return_negative = excess_return < 0
        removed_weight = final_weights[excess_return_negative].sum()
        final_weights[excess_return_negative] = 0  

        # Ranking calculations
        momentum_weight = momentum.rank(pct=True)
        excess_return_weight = excess_return.rank(pct=True)

        ranked_momentum = momentum_weight.rank(ascending=False).reindex(final_weights.index)
        ranked_excess_return = excess_return_weight.rank(ascending=False).reindex(final_weights.index)

        weight_factors = pd.Series(1, index=final_weights.index)

        weight_factors[(ranked_momentum <= 3) | (ranked_excess_return <= 3)] *= 2
        weight_factors[(ranked_momentum > len(momentum) - 3) | (ranked_excess_return > len(momentum) - 3)] /= 2

        final_weights *= weight_factors

        # Step: Move weights to risk-free asset if below SMA
        removed_weight += final_weights[~above_sma.reindex(final_weights.index, fill_value=False)].sum()
        final_weights[~above_sma.reindex(final_weights.index, fill_value=False)] = 0  

        final_weights["Risk-Free"] = removed_weight

        final_weights = final_weights.div(final_weights.sum()).fillna(0)
        # print(final_weights)
        return final_weights

    def run_backtest(self):
        """ Backtest portfolio performance based on adjusted weights for each month. """
        portfolio_values = [self.starting_value]
        print(self.returns)
        for date in self.price_data.index[1:]:
            weights = self.adjust_weights(date)
            monthly_return = (weights * self.returns.loc[date].shift(1)).sum()
            print(monthly_return)
            portfolio_values.append(portfolio_values[-1] * (1 + monthly_return))
        
        self.cumulative_returns = pd.Series(portfolio_values, index=self.price_data.index)

        return self.cumulative_returns

    def plot_returns(self):
        """ Print and plot cumulative portfolio value. """
        print(self.cumulative_returns)
        plt.figure(figsize=(10, 5))
        self.cumulative_returns.plot(title='Institutional Strategy Backtest', ylabel='Portfolio Value ($)', xlabel='Date')
        plt.show()

    def calculate_portfolio_statistics(self):
        """ Compute portfolio performance metrics: Max Drawdown, CAGR, Average Annual Return, and Annual Volatility. """
        portfolio_values = self.cumulative_returns

        yearly_portfolio_values = portfolio_values.resample('Y').last()
        yearly_returns = yearly_portfolio_values.pct_change().dropna()

        cumulative_max = portfolio_values.cummax()
        drawdowns = (portfolio_values - cumulative_max) / cumulative_max
        max_drawdown = drawdowns.min()

        start_value = portfolio_values.iloc[0]
        end_value = portfolio_values.iloc[-1]
        num_years = len(yearly_returns)
        cagr = (end_value / start_value) ** (1 / num_years) - 1

        avg_annual_return = yearly_returns.mean()

        annual_volatility = yearly_returns.std()

        stats = {
            "Max Drawdown": max_drawdown,
            "CAGR": cagr,
            "Average Annual Return": avg_annual_return,
            "Annual Volatility": annual_volatility,
        }

        return stats


tickers = ['VTI', 'VEA', 'VWO', 'BND', "BNDX", "EMB", "IAU", "DBC", "UUP"]
# tickers = ['IXN', 'RXI', 'IXP', 'IXC', "IXG", "MXI", "EXI", "IXJ", "KXI", "JXI"]
risk_free_ticker = 'IEI'
initial_weights = {'VTI': 0.1111, 'VEA': 0.1111, 'VWO': 0.1111, 'BND': 0.1111, "BNDX": 0.1111, "EMB": 0.1111, "IAU": 0.1111, "DBC": 0.1111, "UUP": 0.1111}
# initial_weights = {'IXN': 0.26, 'RXI': 0.12, 'IXP': 0.08, 'IXC': 0.04, "IXG": 0.16, "MXI": 0.04, "EXI": 0.11, "IXJ": 0.1, "KXI": 0.06, "JXI": 0.03}
backtest = InstitutionalBacktest(tickers, risk_free_ticker, '2014-01-01', '2025-02-01', initial_weights)
backtest.run_backtest()
backtest.plot_returns()
stats = backtest.calculate_portfolio_statistics()
print(stats)
