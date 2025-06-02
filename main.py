import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Lightning Trader: MACD, RSI, and Bollinger Bands Strategy by Jett S")

ticker = st.sidebar.text_input("Enter Ticker", "AAPL")
start = st.sidebar.date_input("Start Date", pd.to_datetime("2025-01-01"))
end = st.sidebar.date_input("End Date", pd.to_datetime("2026-01-01"))

data = yf.download(ticker, start=start, end=end, auto_adjust=False)

data['EMA12'] = data['Close'].ewm(span=12).mean()
data['EMA26'] = data['Close'].ewm(span=26).mean()
data['MACD'] = data['EMA12'] - data['EMA26']
data['Signal'] = data['MACD'].ewm(span=9).mean()

delta = data['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

data['MA20'] = data['Close'].rolling(window=20).mean()
data['STD'] = data['Close'].rolling(window=20).std()
data['Upper'] = data['MA20'] + 2 * data['STD']
data['Lower'] = data['MA20'] - 2 * data['STD']

data.dropna(inplace=True)

cash = 10000
position = 0
portfolio = []

for i in range(len(data)):
    price = data['Close'].iloc[i].item()
    macd = data['MACD'].iloc[i].item()
    signal = data['Signal'].iloc[i].item()
    rsi = data['RSI'].iloc[i].item()
    upper = data['Upper'].iloc[i].item()
    lower = data['Lower'].iloc[i].item()
    
    if macd > signal and rsi < 30 and price < lower and cash >= price:
        shares = cash // price
        cash -= shares * price
        position = shares
    elif macd < signal and rsi > 70 and price > upper and position > 0:
        cash += position * price
        position = 0
    total = cash + position * price
    portfolio.append(total)


data['Portfolio'] = portfolio

fig, ax = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
ax[0].plot(data.index, data['Close'], label='Close Price')
ax[0].plot(data.index, data['Upper'], label='Upper Band', linestyle='--', alpha=0.5)
ax[0].plot(data.index, data['Lower'], label='Lower Band', linestyle='--', alpha=0.5)
ax[0].set_title(f'{ticker} Price and Bollinger Bands')
ax[0].legend()

ax[1].plot(data.index, data['Portfolio'], label='Portfolio Value', color='green')
ax[1].set_title('Portfolio Value Over Time')
ax[1].legend()

st.pyplot(fig)
