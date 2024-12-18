import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

st.set_page_config(page_title="S&P 500 Stock Alerts", layout="wide")

@st.cache_data
def load_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_table = tables[0]
    return dict(zip(sp500_table['Security'], sp500_table['Symbol']))

sp500_stocks = load_sp500()

st.title("📈 S&P 500 Stock Data Viewer with Price Alerts")
st.markdown("Select a stock, set a price alert, and monitor its real-time data for price alerts and movement predictions!")

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

def preprocess_data(data, threshold=0.002):
    data['Daily_Return'] = data['Close'].pct_change()
    
    def market_movement(change):
        if change > threshold:
            return 1  # Up
        elif change < -threshold:
            return -1  # Down
        else:
            return 0  # Sideways

    data['Movement'] = data['Daily_Return'].apply(market_movement)
    data['MA_5'] = data['Close'].rolling(window=5).mean()
    data['MA_10'] = data['Close'].rolling(window=10).mean()
    data = data.dropna()
    return data

def train_model(data):
    X = data[['Open', 'High', 'Low', 'Close', 'Volume', 'MA_5', 'MA_10']]
    y = data['Movement']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model

def predict_movement(model, latest_data):
    prediction = model.predict(latest_data)
    if prediction == 1:
        return "Up"
    elif prediction == -1:
        return "Down"
    else:
        return "Sideways"

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

            st.subheader("Predict Market Movement")
            data = preprocess_data(historical_data)
            model = train_model(data)
            latest_data = data.iloc[-1][['Open', 'High', 'Low', 'Close', 'Volume', 'MA_5', 'MA_10']].values.reshape(1, -1)
            prediction = predict_movement(model, latest_data)

            st.markdown(f"**Prediction for tomorrow: {prediction}**")

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

        else:
            st.warning("No data available for the selected stock.")
    except Exception as e:
        st.markdown(f'<div class="error-message">Error: {e}</div>', unsafe_allow_html=True)
