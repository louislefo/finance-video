import yfinance as yf
import pandas as pd

# Define the ticker symbol for Apple
ticker_symbol = "AAPL"

# Create a Ticker object for Apple
apple = yf.Ticker(ticker_symbol)

# --- 1. Get the stock's main information (the "info screen") ---
# This dictionary contains metadata like sector, P/E ratio, market cap, etc.
stock_info = apple.info
print("--- Apple Stock Information (First 10 items) ---")
# Convert to a Series or DataFrame for cleaner display
info_df = pd.Series(stock_info).head(10)
print(info_df)

# --- 2. Get the recent historical data (e.g., last 5 days) ---
historical_data = apple.history(period="5d")
print("\n--- Apple Last 5 Days Historical Data ---")
print(historical_data)