import streamlit as st
import json
import yfinance as yf
from nsepython import nse_optionchain_scrapper
import pandas as pd
import numpy as np

# Load stock symbols from the constant largecap.json file
def load_symbols():
    with open('largecap.json', 'r') as file:
        data = json.load(file)
    return [stock["Symbol"] for stock in data]

# Fetch the spot price using nsepython
def get_spot_price(symbol):
    data = nse_optionchain_scrapper(symbol)
    return data['records']['underlyingValue']

# Fetch OHLC data from Yahoo Finance
def get_ohlc_data(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    ohlc_data = stock.history(period="1d", start=start_date, end=end_date)
    return ohlc_data[['Open', 'High', 'Low', 'Close']]

# Generate all strike prices within ±10% of spot price
def generate_strikes(spot_price, percentage_range=10, increment=50):
    strikes = []
    lower_bound = spot_price * (1 - percentage_range / 100)
    upper_bound = spot_price * (1 + percentage_range / 100)
    
    # Generate strike prices from lower to upper bound with the specified increment
    strike = lower_bound
    while strike <= upper_bound:
        strikes.append(round(strike, 2))
        strike += increment
    
    return strikes

# Fetch options data for the selected stock
def fetch_options_data(symbol, percentage_range=10, increment=50):
    # Get spot price
    spot_price = get_spot_price(symbol)
    st.write(f"Spot Price for {symbol}: {spot_price}")
    
    # Generate strike prices within ±10%
    strikes = generate_strikes(spot_price, percentage_range, increment)
    st.write(f"Strike Prices: {strikes}")
    
    return strikes, spot_price

# Streamlit app
def main():
    st.title("Options OHLC Data Viewer")
    
    # Load stock symbols from the largecap.json file
    symbols = load_symbols()
        
    # Sidebar for stock selection
    selected_stock = st.sidebar.selectbox("Select a Stock:", symbols)
    
    # Input dates for OHLC data
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")
    
    # Display options data
    if st.sidebar.button("Fetch Options OHLC Data"):
        st.write(f"Fetching OHLC data for options ±10% of spot price for {selected_stock}...")
        
        # Get strikes and spot price
        strikes, spot_price = fetch_options_data(selected_stock)
        
        # Fetch OHLC data for the stock
        stock_ohlc = get_ohlc_data(selected_stock, start_date, end_date)
        st.subheader(f"OHLC Data for {selected_stock}")
        st.write(stock_ohlc)
        
        # Display the strike prices as a simulation for options OHLC data
        # Simulate OHLC data for options (Note: This is not real OHLC data, but a simulation)
        simulated_ohlc = stock_ohlc.copy()
        
        # Simulate data for each strike price
        for strike in strikes:
            simulated_ohlc[f"Call Strike {strike}"] = spot_price * 1.1  # Simulate call option strike
            simulated_ohlc[f"Put Strike {strike}"] = spot_price * 0.9   # Simulate put option strike
        
        st.subheader(f"Simulated OHLC for Options (±10% Strike Prices)")
        st.write(simulated_ohlc)

if __name__ == "__main__":
    main()
