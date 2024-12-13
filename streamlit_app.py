import streamlit as st
import json
import yfinance as yf
from nsepython import nse_optionchain_scrapper
import pandas as pd

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

# Fetch options data for the selected stock
def fetch_options_data(symbol, percentage_range=10):
    # Get spot price
    spot_price = get_spot_price(symbol)
    st.write(f"Spot Price for {symbol}: {spot_price}")
    
    # Calculate strike prices ±10%
    lower_strike = spot_price * (1 - percentage_range / 100)
    upper_strike = spot_price * (1 + percentage_range / 100)
    st.write(f"Strike Prices: {lower_strike} (Put), {upper_strike} (Call)")
    
    return lower_strike, upper_strike

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
        
        # Get strike prices ±10% away from spot
        lower_strike, upper_strike = fetch_options_data(selected_stock)
        
        # Fetch OHLC data for the stock
        stock_ohlc = get_ohlc_data(selected_stock, start_date, end_date)
        st.subheader(f"OHLC Data for {selected_stock}")
        st.write(stock_ohlc)
        
        # Display the strike prices as a simulation for options OHLC data
        # Simulate OHLC data for options (Note: This is not real OHLC data, but a simulation)
        simulated_ohlc = stock_ohlc.copy()
        simulated_ohlc['Call Strike Price'] = upper_strike
        simulated_ohlc['Put Strike Price'] = lower_strike
        
        st.subheader(f"Simulated OHLC for Options (±10% Strike Prices)")
        st.write(simulated_ohlc)

if __name__ == "__main__":
    main()
