import streamlit as st
import pandas as pd
import yfinance as yf

# Load the list of S&P 500 stocks
@st.cache_data
def load_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_table = tables[0]
    return dict(zip(sp500_table['Security'], sp500_table['Symbol']))

sp500_stocks = load_sp500()

# Streamlit App
st.title("S&P 500 Stock Data Viewer")
st.write("Select a stock from the list and a time range to view its historical data.")

# Dropdown to select a stock
stock_name = st.selectbox("Choose a stock:", options=list(sp500_stocks.keys()))

# Dropdown to select the time range
time_range = st.selectbox(
    "Select the time range:",
    options=[
        ("1 Day", "1d"),
        ("6 Months", "6mo"),
        ("2 Years", "2y"),
        ("3 Years", "3y"),
        ("5 Years", "5y"),
    ],
)

# Fetch historical data for the selected stock
if stock_name and time_range:
    ticker = sp500_stocks[stock_name]
    period = time_range[1]
    st.write(f"Fetching data for **{stock_name} ({ticker})** for the last **{time_range[0]}**...")

    # Fetch stock data from yfinance
    try:
        historical_data = yf.download(tickers=ticker, period=period, interval="1d")
        if not historical_data.empty:
            st.write(f"Historical data for **{stock_name} ({ticker})** over the past {time_range[0]}:")

            # Display data as a table
            st.dataframe(historical_data)

            # Plot the closing price
            st.line_chart(historical_data['Close'])
        else:
            st.warning("No data available for the selected stock.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
