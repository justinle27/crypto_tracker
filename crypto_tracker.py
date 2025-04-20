import pandas as pd
from datetime import datetime
import time
time.sleep(6) 

def get_price_history(coin_id='bitcoin'):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7'
    response = requests.get(url)

    if response.status_code != 200:
        print("API Error:", response.status_code, response.text)
        return pd.DataFrame()

    data = response.json()
    print("API returned:", data)

    try:
        data = response.json()
        print("Raw price history response:", data)  # 👈 Moved this after data is assigned
    except Exception as e:
        print("Failed to parse JSON:", e)
        return pd.DataFrame()

    if not data or "prices" not in data:
        print("Missing or invalid 'prices' data:", data)
        return pd.DataFrame()

    prices = data["prices"]

    if not prices:
        print("Empty price list received.")
        return pd.DataFrame()

    try:
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print("Error processing price data:", e)
        return pd.DataFrame()

import streamlit as st
import requests

# Function to get crypto price

@st.cache_data(ttl=300)
def get_crypto_data(coin_id='bitcoin'):
    url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}'
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    
    if isinstance(data, list) and len(data) > 0:
        coin = data[0]
        return {
            "name": coin["name"],
            "price": coin["current_price"],
            "change_24h": coin["price_change_percentage_24h"],
            "market_cap": coin["market_cap"]
        }
    else:
        return None

# Streamlit UI
st.title("📈 Crypto Price Tracker")

coin = st.selectbox("Choose a cryptocurrency", ["bitcoin", "ethereum", "dogecoin"])
data = get_crypto_data(coin)

if data is None:
    st.error("⚠️ Could not fetch crypto data. Try again later.")
    st.stop()

if data:
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Current Price (USD)", value=f"${data['price']}")
    col2.metric(label="24h Change", value=f"{data['change_24h']:.2f}%")
    col3.metric(label="Market Cap", value=f"${data['market_cap']:,}")
else:
    st.error("Failed to fetch data.")

st.subheader("📊 Price History (Last 7 Days)")
history_df = get_price_history(coin)

if history_df.empty or "timestamp" not in history_df.columns:
    st.warning("📉 Price history is unavailable right now.")
else:
    st.line_chart(history_df.set_index("timestamp")["price"])

st.subheader("🔔 Price Alert (Local Test)")
alert_price = st.number_input("Alert me if price goes above...", min_value=0.0, value=float(data["price"] + 100))

if data["price"] > alert_price:
    st.warning(f"⚠️ Alert! {coin.title()} is above your threshold (${alert_price})")
else:
    st.info(f"{coin.title()} is below ${alert_price}")