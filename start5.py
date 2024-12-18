import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="S&P 500 Stock Alerts", layout="wide")

@st.cache_data
def load_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_table = tables[0]
    return dict(zip(sp500_table['Security'], sp500_table['Symbol']))

sp500_stocks = load_sp500()

st.title("📈 S&P 500 Stock Data Viewer with Price Alerts")
st.markdown("Select a stock, set a price alert, and monitor its real-time data for price alerts!")

st.markdown("""
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #007bff;
    }
    .alert-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
    }
    .alert-header {
        font-size: 24px;
        font-weight: bold;
    }
    .alert-list {
        margin-top: 10px;
    }
    .alert-item {
        background-color: #07663b;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .alert-item p {
        margin: 0;
    }
    .alert-item .stock-name {
        font-weight: bold;
        font-size: 16px;
    }
    .alert-item .alert-price {
        color: #ffffff;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
        font-size: 16px;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

stock_name = st.selectbox("Choose a stock:", options=list(sp500_stocks.keys()))

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

if "alerts" not in st.session_state:
    st.session_state.alerts = []

def fetch_stock_data(ticker, period, interval):
    return yf.download(tickers=ticker, period=period, interval=interval)

if stock_name and time_range:
    ticker = sp500_stocks[stock_name]
    period = time_range[1]
    
    interval = "1m" if time_range[0] == "1 Day" else "1d"

    st.write(f"Fetching data for **{stock_name} ({ticker})** for the last **{time_range[0]}**...")

    try:
        historical_data = fetch_stock_data(ticker, period, interval)
        if not historical_data.empty:
            st.write(f"Historical data for **{stock_name} ({ticker})** over the past {time_range[0]}:")

            st.dataframe(historical_data)

            st.line_chart(historical_data['Close'])

            with st.expander("Set a Price Alert", expanded=True):
                alert_price = st.number_input(
                    "Enter the stock price to set an alert:",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    format="%.2f",
                    help="Enter the price at which you want to be alerted."
                )
                if st.button("Add Alert", use_container_width=True):
                    alert = {"stock_name": stock_name, "ticker": ticker, "alert_price": alert_price}
                    st.session_state.alerts.append(alert)
                    st.success(f"✅ Alert added for **{stock_name} ({ticker})** at price: **${alert_price:.2f}**", icon="🔔")

            if st.session_state.alerts:
                st.subheader("Active Alerts", anchor="active-alerts")
                for alert in st.session_state.alerts:
                    st.markdown(f"""
                    <div class="alert-item">
                        <p class="stock-name">{alert['stock_name']} ({alert['ticker']})</p>
                        <p class="alert-price">Price Alert: ${alert['alert_price']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.subheader("Monitoring Alerts")
            with st.spinner("Checking stock prices every minute..."):
                while True:
                    for alert in st.session_state.alerts:
                        current_data = yf.Ticker(alert["ticker"]).history(period="1d", interval="1m")
                        if not current_data.empty:
                            current_price = current_data["Close"].iloc[-1]
                            st.write(f"Current price for {alert['stock_name']} ({alert['ticker']}): **${current_price:.2f}**")

                            if current_price >= alert["alert_price"]:
                                st.markdown(f"""
                                <div class="success-message">
                                    🚨 Alert Activated: **{alert['stock_name']} ({alert['ticker']})** reached ${current_price:.2f}!
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state.alerts.remove(alert)
                        else:
                            st.warning("No data available. Retrying...")

                    time.sleep(60)  

        else:
            st.warning("No data available for the selected stock.")
    except Exception as e:
        st.markdown(f'<div class="error-message">Error: {e}</div>', unsafe_allow_html=True)
