import streamlit as st
import json
import yfinance as yf
from nsepython import nse_optionchain_scrapper
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load stock symbols from the constant largecap.json file
def load_symbols():
    with open('largecap.json', 'r') as file:
        data = json.load(file)
    return [stock["Symbol"] for stock in data]

# Fetch the spot price and options data using nsepython
def get_options_data(symbol):
    try:
        data = nse_optionchain_scrapper(symbol)
        spot_price = data['records']['underlyingValue']
        options_data = data['records']['data']
        return spot_price, options_data
    except Exception as e:
        st.error(f"Error fetching options data for {symbol}: {e}")
        return None, None

# Filter options data based on strike price range
def filter_options_data(options_data, spot_price, percentage_range=10):
    lower_bound = spot_price * (1 - percentage_range / 100)
    upper_bound = spot_price * (1 + percentage_range / 100)
    
    filtered_data = [option for option in options_data if lower_bound <= option['strikePrice'] <= upper_bound]
    return filtered_data

# Fetch OHLC data from Yahoo Finance
def get_ohlc_data(symbol, start_date, end_date):
    try:
        stock = yf.Ticker(f"{symbol}.NS")
        ohlc_data = stock.history(start=start_date, end=end_date)
        if ohlc_data.empty:
            st.warning(f"No OHLC data found for {symbol} in the specified date range.")
        return ohlc_data[['Open', 'High', 'Low', 'Close']] if not ohlc_data.empty else None
    except Exception as e:
        st.error(f"Error fetching OHLC data for {symbol}: {e}")
        return None

# Streamlit app
def main():
    st.title("Options OHLC Data Viewer")
    
    # Load stock symbols from the largecap.json file
    symbols = load_symbols()
        
    # Sidebar for stock selection
    selected_stock = st.sidebar.selectbox("Select a Stock:", symbols)
    
    # Input dates for OHLC data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days
    start_date = st.sidebar.date_input("Start Date", value=start_date)
    end_date = st.sidebar.date_input("End Date", value=end_date)
    
    # Display options data
    if st.sidebar.button("Fetch Options OHLC Data"):
        st.write(f"Fetching OHLC data for options ±10% of spot price for {selected_stock}...")
        
        # Get spot price and options data
        spot_price, options_data = get_options_data(selected_stock)
        if spot_price is None or options_data is None:
            st.warning(f"No data available for {selected_stock}.")
            return
        
        st.write(f"Spot Price for {selected_stock}: {spot_price}")
        
        # Filter options data
        filtered_options = filter_options_data(options_data, spot_price)
        
        # Fetch OHLC data for the stock
        stock_ohlc = get_ohlc_data(selected_stock, start_date, end_date)
        if stock_ohlc is None:
            st.warning(f"No OHLC data found for {selected_stock}.")
            return
        
        st.subheader(f"OHLC Data for {selected_stock}")
        st.write(stock_ohlc)
        
        # Display options data
        st.subheader(f"Options Data (±10% Strike Prices)")
        
        # Separate calls and puts
        calls = [option for option in filtered_options if 'CE' in option]
        puts = [option for option in filtered_options if 'PE' in option]
        
        # Display calls
        st.write("Call Options:")
        calls_df = pd.DataFrame(calls)
        st.write(calls_df[['strikePrice', 'CE.lastPrice', 'CE.openInterest', 'CE.changeinOpenInterest']])
        
        # Display puts
        st.write("Put Options:")
        puts_df = pd.DataFrame(puts)
        st.write(puts_df[['strikePrice', 'PE.lastPrice', 'PE.openInterest', 'PE.changeinOpenInterest']])

if __name__ == "__main__":
    main()
