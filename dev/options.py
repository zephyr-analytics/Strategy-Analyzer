import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import scipy.stats as si
import scipy.optimize as opt

# === CONFIGURATION ===
TICKER = "QQQM"  # Stock to hedge
SHARES = 100  # Number of shares to hedge
CONTRACTS = 1  # Each contract covers 100 shares
RISK_FREE_RATE = 0.02  # Assume a risk-free rate of 2%

# Black-Scholes Greeks & Implied Volatility

def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * si.norm.cdf(-d2) - S * si.norm.cdf(-d1)
    
    return price

def implied_volatility(S, K, T, r, market_price, option_type="call"):
    objective = lambda sigma: black_scholes(S, K, T, r, sigma, option_type) - market_price
    try:
        iv = opt.newton(objective, 0.2) * 100  # Convert to percentage
        return iv if not np.isnan(iv) else 20.0  # Default IV if NaN
    except:
        return 20.0  # Return default 20% if calculation fails

def calculate_greeks(S, K, T, r, sigma, option_type="call"):
    if np.isnan(sigma) or sigma <= 0:
        return 0, 0, 0, 0  # Return zeros if invalid sigma
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    delta = si.norm.cdf(d1) if option_type == "call" else si.norm.cdf(d1) - 1
    gamma = si.norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (- (S * si.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2)) if option_type == "call" else (- (S * si.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2))
    vega = S * np.sqrt(T) * si.norm.pdf(d1)

    return delta, gamma, theta, vega

# === FETCH STOCK PRICE ===
stock = yf.Ticker(TICKER)
stock_price = stock.history(period="1d")["Close"].iloc[-1]
print(f"\nStock Price for {TICKER}: ${stock_price:.2f}")

# === FETCH OPTIONS CHAIN ===
expiry_dates = stock.options  # Available expiration dates
print("\nAvailable Expiry Dates:")
for i, date in enumerate(expiry_dates):
    print(f"{i}: {date}")
expiry_index = int(input("Select expiry index: "))
expiry = expiry_dates[expiry_index]
options_chain = stock.option_chain(expiry)
calls, puts = options_chain.calls, options_chain.puts

# Calculate Greeks and Implied Volatility
calls["impliedVol"] = calls.apply(lambda row: implied_volatility(stock_price, row["strike"], 1/12, RISK_FREE_RATE, row["lastPrice"], "call"), axis=1)
calls[["delta", "gamma", "theta", "vega"]] = calls.apply(lambda row: pd.Series(calculate_greeks(stock_price, row["strike"], 1/12, RISK_FREE_RATE, row["impliedVol"] / 100, "call")), axis=1)

puts["impliedVol"] = puts.apply(lambda row: implied_volatility(stock_price, row["strike"], 1/12, RISK_FREE_RATE, row["lastPrice"], "put"), axis=1)
puts[["delta", "gamma", "theta", "vega"]] = puts.apply(lambda row: pd.Series(calculate_greeks(stock_price, row["strike"], 1/12, RISK_FREE_RATE, row["impliedVol"] / 100, "put")), axis=1)

# Display available options
print("\nAvailable Call Options:")
print(calls[['contractSymbol', 'strike', 'lastPrice', 'openInterest', 'impliedVol', 'delta', 'gamma', 'theta', 'vega']])
print("\nAvailable Put Options:")
print(puts[['contractSymbol', 'strike', 'lastPrice', 'openInterest', 'impliedVol', 'delta', 'gamma', 'theta', 'vega']])

# User selects contracts
call_index = int(input("Select call option index: "))
put_index = int(input("Select put option index: "))
call_option = calls.iloc[call_index]
put_option = puts.iloc[put_index]

call_strike = call_option['strike']
put_strike = put_option['strike']
call_premium = call_option['lastPrice']
put_premium = put_option['lastPrice']

# Calculate net premium cost of the hedge
net_premium = (put_premium + call_premium) * (CONTRACTS * 100)
print(f"\nTotal Cost of Straddle: ${net_premium:.2f}")

# === PLOT PAYOFF ===
stock_prices = np.linspace(stock_price * 0.8, stock_price * 1.2, 100)

put_pnl = (np.maximum(put_strike - stock_prices, 0) * CONTRACTS * 100) - (put_premium * CONTRACTS * 100)
call_pnl = (np.maximum(stock_prices - call_strike, 0) * CONTRACTS * 100) - (call_premium * CONTRACTS * 100)
total_pnl = put_pnl + call_pnl

plt.figure(figsize=(15, 8))
plt.plot(stock_prices, put_pnl, label="Put Option PnL", linestyle="--", color="red", linewidth=2)
plt.plot(stock_prices, call_pnl, label="Call Option PnL", linestyle="--", color="green", linewidth=2)
plt.plot(stock_prices, total_pnl, label="Total PnL (Straddle)", color="black", linewidth=2)
plt.axvline(x=stock_price, color="gray", linestyle="--", label="Current Price")
plt.axvline(x=put_strike, color="red", linestyle="--", label="Put Strike")
plt.axvline(x=call_strike, color="green", linestyle="--", label="Call Strike")
plt.title(f"{TICKER} Straddle Strategy PnL at Expiration")
plt.xlabel("Stock Price at Expiration")
plt.ylabel("Profit / Loss ($)")
plt.legend()
plt.grid(True)
plt.show()
