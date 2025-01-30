import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# === CONFIGURATION ===
TICKER = "SPLG"  # Stock to hedge
PUT_DELTA = 0.01  # Put strike 5% below stock price
CALL_DELTA = 0.01  # Call strike 5% above stock price
SHARES = 100
CONTRACTS = 1  # Each contract = 100 shares

# === FETCH STOCK PRICE ===
stock = yf.Ticker(TICKER)
stock_price = stock.history(period="1d")["Close"].iloc[-1]
print(f"\nStock Price for {TICKER}: ${stock_price:.2f}")

# === FETCH OPTIONS CHAIN ===
expiry = stock.options[4]  # Select first available expiry date
options_chain = stock.option_chain(expiry)
calls, puts = options_chain.calls, options_chain.puts

# === SELECT HEDGE OPTIONS (Fix Selection Logic) ===
# Find the closest OTM put (5% below stock price)
puts = puts.sort_values(by="strike", ascending=True)  # Sort for proper selection
put_candidates = puts[puts["strike"] <= stock_price * (1 + PUT_DELTA)]
put_option = put_candidates.iloc[-1] if not put_candidates.empty else puts.iloc[0]  # Fallback to nearest

# Find the closest OTM call (5% above stock price)
calls = calls.sort_values(by="strike", ascending=True)  # Sort for proper selection
call_candidates = calls[calls["strike"] >= stock_price * (1 + CALL_DELTA)]
call_option = call_candidates.iloc[0] if not call_candidates.empty else calls.iloc[-1]  # Fallback to nearest

# === STRIKE PRICES & PREMIUMS ===
put_strike = put_option['strike']
call_strike = call_option['strike']
put_premium = put_option['lastPrice']
call_premium = call_option['lastPrice']

# Print Selected Options
print("\nSelected Put Option (Protection):")
print(put_option[['contractSymbol', 'strike', 'lastPrice', 'openInterest']])

print("\nSelected Call Option (Income):")
print(call_option[['contractSymbol', 'strike', 'lastPrice', 'openInterest']])

# Calculate net premium cost of the hedge (Fix Scaling)
net_premium = (put_premium - call_premium) * (CONTRACTS * 100)  # Multiply by contracts & contract size
print(f"\nNet cost to hedge: ${net_premium:.2f} total")

if net_premium > 0:
    print("💰 This hedge requires an upfront cost.")
elif net_premium < 0:
    print("💵 This hedge generates a credit (costless hedge).")
else:
    print("⚖️ This hedge is neutral (zero cost).")

# === PLOT PAYOFF ===
stock_prices = np.linspace(stock_price * 0.8, stock_price * 1.2, 100)  # Range of final stock prices

# Calculate PnL components
stock_pnl = (stock_prices - stock_price) * SHARES  # Profit/loss from stock movement
put_pnl = (np.maximum(put_strike - stock_prices, 0) * CONTRACTS * 100) + (put_premium * CONTRACTS * 100)
call_pnl = (np.minimum(call_strike - stock_prices, 0) * CONTRACTS * 100) + (call_premium * CONTRACTS * 100)
total_pnl = stock_pnl + put_pnl + call_pnl

# === PLOT RESULTS ===
plt.figure(figsize=(15, 8))

# Plot individual components
# plt.plot(stock_prices, stock_pnl, label="Stock PnL", linestyle="--", color="blue", linewidth=2)
plt.plot(stock_prices, put_pnl, label="Put Option PnL", linestyle="--", color="red", linewidth=2)
plt.plot(stock_prices, call_pnl, label="Call Option PnL", linestyle="--", color="green", linewidth=2)

# Plot total strategy PnL
plt.plot(stock_prices, total_pnl, label="Total PnL (Hedged)", color="black", linewidth=2)

# Mark strike prices
plt.axvline(x=stock_price, color="gray", linestyle="--", label="Current Price")
plt.axvline(x=put_strike, color="red", linestyle="--", label="Put Strike")
plt.axvline(x=call_strike, color="green", linestyle="--", label="Call Strike")

# Labels and legend
plt.title(f"{TICKER} Options Hedging Strategy PnL at Expiration")
plt.xlabel("Stock Price at Expiration")
plt.ylabel("Profit / Loss ($)")
plt.legend()
plt.grid(True)

# Show plot
plt.show()