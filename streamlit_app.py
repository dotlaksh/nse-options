import streamlit as st
import json
from nsepython import nse_optionchain_scrapper

# Load stock symbols from JSON file
def load_symbols(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data["stocks"]

# Fetch options data for the selected stock
def fetch_options_data(symbol, percentage_range=10):
    # Fetch option chain data
    data = nse_optionchain_scrapper(symbol)
    
    # Get spot price
    spot_price = data['records']['underlyingValue']
    st.write(f"Spot Price for {symbol}: {spot_price}")
    
    # Calculate 10% range
    lower_bound = spot_price * (1 - percentage_range / 100)
    upper_bound = spot_price * (1 + percentage_range / 100)

    # Filter options for current expiry
    expiry_date = data['records']['expiryDates'][0]  # Nearest expiry
    option_chain = data['records']['data']
    filtered_options = [
        entry for entry in option_chain 
        if entry['expiryDate'] == expiry_date 
        and lower_bound <= entry['strikePrice'] <= upper_bound
    ]

    # Separate calls and puts
    calls = [entry['CE'] for entry in filtered_options if 'CE' in entry]
    puts = [entry['PE'] for entry in filtered_options if 'PE' in entry]
    
    return calls, puts, spot_price, expiry_date

# Streamlit app
def main():
    st.title("Options Chain Viewer")
    
    # Load stock symbols
    symbols = load_symbols("symbols.json")
    
    # Sidebar for stock selection
    selected_stock = st.sidebar.selectbox("Select a Stock:", symbols)
    
    # Display options data
    if st.sidebar.button("Fetch Options Data"):
        st.write(f"Fetching options data for {selected_stock}...")
        calls, puts, spot_price, expiry_date = fetch_options_data(selected_stock)
        
        st.subheader(f"Options Data for {selected_stock} (Expiry: {expiry_date})")
        
        st.write("### Calls (±10% Strike Prices)")
        st.table(calls)

        st.write("### Puts (±10% Strike Prices)")
        st.table(puts)

if __name__ == "__main__":
    main()
