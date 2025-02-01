

from datetime import date, datetime

import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from scipy.stats import norm


# === CONFIGURATION ===
pd.set_option("display.max_rows", None)  # Show all rows
pd.set_option("display.max_columns", None)
TICKER = "QQQ"
SHARES = 100  # Number of shares to hedge
CONTRACTS = 1  # Each contract covers 100 shares
RISK_FREE_RATE = 0.045  # Assume a risk-free rate of 2%
TRADING_DAYS = 252

# Black-Scholes Greeks & Implied Volatility

def black_scholes(S, K, T, r, sigma, last_price, option_type):
    """
    """
    d1 = (np.log(S/K) + (r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    
    if option_type == "call":
        price = S*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
    else:
        price = K*np.exp(-r*T)*norm.cdf(-d2)- S*norm.cdf(-d1)
    
    if price > last_price:
        return "Undervalued"
    elif price < last_price:
        return "Overvalued"
    else:
        return "Fair Value"


def calculate_time_to_expiry(expiry) -> float:
    """
    """
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    time_delta = expiry_date - date.today()
    time_delta = (int(time_delta.days) / TRADING_DAYS) / 12

    return time_delta


def calculate_greeks(S, K, T, r, sigma, option_type):
    """
    Calculates Delta, Gamma, Theta, and Vega.

    Parameters
    ----------
    S : float
        Float representing the underlying stock price.
    K : float
        Float representing the options contract strike price.
    T : int
        Integer representing the options contract time to maturity in % of year.
    r : constant, float
        The current risk free rate of return.
    sigma : float
        Float representing the assets current implied volatility.
    option_type : str
        String representing the type of options contract, put or call.
    """
    if np.isnan(sigma) or sigma <= 0:
        return 0, 0, 0, 0  # Return zeros if invalid sigma
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    delta = norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    if option_type == "call":
        first_term = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        second_term = - r * K * np.exp(-r * T) * norm.cdf(d2)
        theta = first_term + second_term
    else:
        first_term = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        second_term = r * K * np.exp(-r * T) * norm.cdf(-d2)
        theta = first_term + second_term

    vega = S * np.sqrt(T) * norm.pdf(d1)

    return delta, gamma, theta, vega


def transform_data(data):
    """
    """
    data["impliedVolatility"] = data["impliedVolatility"].apply(lambda x: f"{x:.2%}")
    data["Delta(%)"] = data["Delta(%)"].apply(lambda x: f"{x:.2%}")
    return data


# === FETCH STOCK PRICE ===
stock = yf.Ticker(TICKER)
stock_price = stock.history(period="1d")["Close"].iloc[-1]
print(f"\nStock Price for {TICKER}: ${stock_price:.2f}")

# === FETCH OPTIONS CHAIN ===
expiry_dates = stock.options  # Available expiration dates
print("\nAvailable Expiry Dates:")
for i, dates in enumerate(expiry_dates):
    print(f"{i}: {dates}")
expiry_index = int(input("Select expiry index: "))
expiry = expiry_dates[expiry_index]
options_chain = stock.option_chain(expiry)
calls, puts = options_chain.calls, options_chain.puts


time_delta = calculate_time_to_expiry(expiry=expiry)


# Calculate Greeks and Implied Volatility
calls[["Valuation"]] = calls.apply(lambda row: pd.Series(black_scholes(stock_price, row["strike"], time_delta, RISK_FREE_RATE, row["impliedVolatility"], row["lastPrice"], "call")), axis=1)
puts[["Valuation"]] = puts.apply(lambda row: pd.Series(black_scholes(stock_price, row["strike"], time_delta, RISK_FREE_RATE, row["impliedVolatility"], row["lastPrice"], "put")), axis=1)
calls[["Delta(%)", "Gamma", "Theta", "Vega"]] = calls.apply(lambda row: pd.Series(calculate_greeks(stock_price, row["strike"], time_delta, RISK_FREE_RATE, row["impliedVolatility"], "call")), axis=1)
puts[["Delta(%)", "Gamma", "Theta", "Vega"]] = puts.apply(lambda row: pd.Series(calculate_greeks(stock_price, row["strike"], time_delta, RISK_FREE_RATE, row["impliedVolatility"], "put")), axis=1)

calls = transform_data(calls)
puts = transform_data(puts)


# Display available options
print("\nAvailable Call Options:")
print(calls[['contractSymbol', 'strike', 'lastPrice', 'openInterest', 'impliedVolatility', "Valuation", "Delta(%)", "Gamma", "Theta", "Vega"]])
print("\nAvailable Put Options:")
print(puts[['contractSymbol', 'strike', 'lastPrice', 'openInterest', 'impliedVolatility', "Valuation", "Delta(%)", "Gamma", "Theta", "Vega"]])

# User selects contracts
call_index = int(input("Select call option index: "))
put_index = int(input("Select put option index: "))
call_option = calls.iloc[call_index]
put_option = puts.iloc[put_index]

call_strike = call_option['strike']
put_strike = put_option['strike']
call_premium = call_option['lastPrice']
put_premium = put_option['lastPrice']

# Calculate net premium cost
net_premium = (put_premium + call_premium) * (CONTRACTS * 100)
print(f"\nTotal Cost of Straddle: ${net_premium:.2f}")

# === PLOT PAYOFF ===
stock_prices = np.linspace(stock_price * 0.8, stock_price * 1.2, 100)

put_pnl = (np.maximum(put_strike - stock_prices, 0) * CONTRACTS * 100) - (put_premium * CONTRACTS * 100)
call_pnl = (np.maximum(stock_prices - call_strike, 0) * CONTRACTS * 100) - (call_premium * CONTRACTS * 100)
total_pnl = put_pnl + call_pnl

# Plot results

break_even_indices = np.where(np.diff(np.sign(total_pnl)))[0]
break_even_values = []

for idx in break_even_indices:
    # Linear interpolation to approximate the exact break-even point
    x1, x2 = stock_prices[idx], stock_prices[idx + 1]
    y1, y2 = total_pnl[idx], total_pnl[idx + 1]
    if y2 - y1 != 0:
        break_even = x1 - y1 * (x2 - x1) / (y2 - y1)
        break_even_values.append(break_even)
# Calculate percentage change needed to reach each break-even point
percent_changes = [(be - stock_price) / stock_price * 100 for be in break_even_values]

# Format break-even points with percentage changes
if break_even_values:
    be_legend = ", ".join([f"{be:.2f} ({pc:+.2f}%)" for be, pc in zip(sorted(break_even_values), percent_changes)])
else:
    be_legend = "N/A"

# Plot results
plt.figure(figsize=(15, 8))
plt.plot(stock_prices, put_pnl, label="Put Option PnL", linestyle="--", color="red", linewidth=1)
plt.plot(stock_prices, call_pnl, label="Call Option PnL", linestyle="--", color="green", linewidth=1)
plt.plot(stock_prices, total_pnl, label="Total PnL (Straddle)", color="black", linewidth=1)

# Add vertical lines for key price levels
plt.axvline(x=stock_price, color="gray", linestyle="--", label="Current Price")

# Add legend entry for break-even points with percentage changes
plt.plot([], [], color="blue", linestyle=":", label=f"Break-even: {be_legend}")

plt.title(f"{TICKER} Straddle Strategy PnL at Expiration")
plt.xlabel("Stock Price at Expiration")
plt.ylabel("Profit / Loss ($)")
plt.legend()
plt.grid(True)
plt.show()
