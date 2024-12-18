import streamlit as st
import pandas as pd
import yfinance as yf
import time

# Load the list of S&P 500 stocks
@st.cache_data
def load_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_table = tables[0]
    return dict(zip(sp500_table['Security'], sp500_table['Symbol']))

sp500_stocks = load_sp500()

# Streamlit App
st.title("S&P 500 Stock Data Viewer with Multiple Price Alerts")
st.write("Select a stock from the list, set a price alert, and view real-time data for multiple alerts!")

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

# Store the list of alerts
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Function to fetch stock data
def fetch_stock_data(ticker, period):
    return yf.download(tickers=ticker, period=period, interval="1d")

# Fetch historical data for the selected stock
if stock_name and time_range:
    ticker = sp500_stocks[stock_name]
    period = time_range[1]
    st.write(f"Fetching data for **{stock_name} ({ticker})** for the last **{time_range[0]}**...")

    try:
        historical_data = fetch_stock_data(ticker, period)
        if not historical_data.empty:
            st.write(f"Historical data for **{stock_name} ({ticker})** over the past {time_range[0]}:")

            # Display data as a table
            st.dataframe(historical_data)

            # Plot the closing price
            st.line_chart(historical_data['Close'])

            # Price alert system
            st.subheader("Set a Price Alert")
            alert_price = st.number_input(
                "Enter the stock price to set an alert:", min_value=0.0, value=0.0, step=0.1
            )
            if st.button("Add Alert"):
                # Add alert to session state (store multiple alerts)
                alert = {"stock_name": stock_name, "ticker": ticker, "alert_price": alert_price}
                st.session_state.alerts.append(alert)
                st.write(f"Alert added for **{stock_name} ({ticker})** at price: ${alert_price}")

            # Show active alerts
            if st.session_state.alerts:
                st.write("Active Alerts:")
                for alert in st.session_state.alerts:
                    st.write(f"{alert['stock_name']} ({alert['ticker']}) - Price Alert: ${alert['alert_price']}")

            # Poll stock price every 1 minute and check for alerts
            st.subheader("Monitoring Alerts")
            with st.spinner("Checking stock prices every minute..."):
                while True:
                    for alert in st.session_state.alerts:
                        current_data = yf.Ticker(alert["ticker"]).history(period="1d", interval="1m")
                        if not current_data.empty:
                            current_price = current_data["Close"].iloc[-1]
                            st.write(f"Current price for {alert['stock_name']} ({alert['ticker']}): ${current_price:.2f}")

                            if current_price >= alert["alert_price"]:
                                st.success(
                                    f"🚨 Alert Activated: **{alert['stock_name']} ({alert['ticker']})** reached ${current_price:.2f}!"
                                )
                                # You could break here if you want the alerts to stop checking after triggering, or you can remove the alert
                                st.session_state.alerts.remove(alert)
                        else:
                            st.warning("No data available. Retrying...")

                    time.sleep(60)  # Wait for 1 minute before checking again

        else:
            st.warning("No data available for the selected stock.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
