import yfinance as yf, pandas as pd, numpy as np, streamlit as st, matplotlib.pyplot as plt
st.set_page_config(layout="wide"); st.title("⚡ Lightning Trader AI v2.0 by Jett S")

t = st.sidebar.text_input("Ticker", "AAPL")
s = st.sidebar.date_input("Start Date", pd.to_datetime("2025-01-01"))
e = st.sidebar.date_input("End Date", pd.to_datetime("2026-01-01"))
d = yf.download(t, start=s, end=e)

# Indicators
d['EMA12'], d['EMA26'] = d['Close'].ewm(span=12).mean(), d['Close'].ewm(span=26).mean()
d['MACD'], d['Signal'] = d['EMA12'] - d['EMA26'], (d['EMA12'] - d['EMA26']).ewm(span=9).mean()
delta = d['Close'].diff()
gain, loss = delta.clip(lower=0).rolling(14).mean(), -delta.clip(upper=0).rolling(14).mean()
rs = gain / loss; d['RSI'] = 100 - (100 / (1 + rs))
d['MA20'], d['STD'] = d['Close'].rolling(20).mean(), d['Close'].rolling(20).std()
d['Upper'], d['Lower'] = d['MA20'] + 2*d['STD'], d['MA20'] - 2*d['STD']
d.dropna(inplace=True)

# Smart Strategy
cash, pos, port = 10000, 0, []
for i in range(len(d)):
    price = d['Close'].iloc[i]
    macd, signal = d['MACD'].iloc[i], d['Signal'].iloc[i]
    rsi = d['RSI'].iloc[i]
    upper, lower = d['Upper'].iloc[i], d['Lower'].iloc[i]
    ema_trend = d['EMA12'].iloc[i] > d['EMA26'].iloc[i]

    buy_cond = macd > signal and rsi < 35 and price < lower and ema_trend
    sell_cond = macd < signal and rsi > 65 and price > upper and not ema_trend

    if buy_cond and cash >= price:
        shares = cash // price
        cash -= shares * price
        pos += shares
    elif sell_cond and pos > 0:
        cash += pos * price
        pos = 0
    port.append(cash + pos * price)

d['Portfolio'] = port

# Charting
fig, ax = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
ax[0].plot(d.index, d['Close'], label='Close'); ax[0].plot(d.index, d['Upper'], '--', alpha=0.5)
ax[0].plot(d.index, d['Lower'], '--', alpha=0.5); ax[0].set_title(f'{t} Price + Bollinger Bands'); ax[0].legend()
ax[1].plot(d.index, d['Portfolio'], label='Portfolio Value', color='green'); ax[1].set_title('Smart Portfolio'); ax[1].legend()
st.pyplot(fig)
