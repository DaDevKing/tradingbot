import yfinance as yf, pandas as pd, numpy as np, streamlit as st, matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("⚡ Lightning Trader v2.1 by Jett S")

t = st.sidebar.text_input("Ticker", "AAPL")
s = st.sidebar.date_input("Start Date", pd.to_datetime("2025-01-01"))
e = st.sidebar.date_input("End Date", pd.to_datetime("2026-01-01"))
d = yf.download(t, start=s, end=e)

d['EMA12'], d['EMA26'] = d['Close'].ewm(span=12).mean(), d['Close'].ewm(span=26).mean()
d['MACD'] = d['EMA12'] - d['EMA26']
d['Signal'] = d['MACD'].ewm(span=9).mean()

delta = d['Close'].diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = -delta.clip(upper=0).rolling(14).mean()
rs = gain / loss
d['RSI'] = 100 - (100 / (1 + rs))

d['MA20'] = d['Close'].rolling(20).mean()
d['STD'] = d['Close'].rolling(20).std()
d['Upper'], d['Lower'] = d['MA20'] + 2 * d['STD'], d['MA20'] - 2 * d['STD']
d.dropna(inplace=True)

cash, pos, port = 10000, 0, []

for i in range(len(d)):
    price = float(d['Close'].iloc[i])
    macd = float(d['MACD'].iloc[i])
    signal = float(d['Signal'].iloc[i])
    rsi = float(d['RSI'].iloc[i])
    upper = float(d['Upper'].iloc[i])
    lower = float(d['Lower'].iloc[i])
    ema_trend = d['EMA12'].iloc[i] > d['EMA26'].iloc[i]

    buy_cond = macd > signal and rsi < 35 and price < lower and ema_trend
    sell_cond = macd < signal and rsi > 65 and price > upper and not ema_trend

    if buy_cond and cash >= price:
        print(f"Buying at {price} on {d.index[i]}")
        shares = cash // price
        cash -= shares * price
        pos += shares
    elif sell_cond and pos > 0:
        print(f"Selling at {price} on {d.index[i]}")
        cash += pos * price
        pos = 0

    port.append(cash + pos * price)


d['Portfolio'] = port

# Display metrics
final_val = round(port[-1], 2)
change = final_val - 10000
pct = (change / 10000) * 100
col1, col2, col3 = st.columns(3)
col1.metric("📈 Final Portfolio", f"${final_val:,.2f}")
col2.metric("💰 Net Gain", f"${change:,.2f}", delta=f"{pct:.2f}%")
col3.metric("🧠 Strategy", "MACD + RSI + BBands", delta="v2.1")

# Plotting
fig, ax = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
ax[0].plot(d.index, d['Close'], label='Close', color='black')
ax[0].plot(d.index, d['Upper'], '--', label='Upper Band', alpha=0.4)
ax[0].plot(d.index, d['Lower'], '--', label='Lower Band', alpha=0.4)
ax[0].fill_between(d.index, d['Lower'], d['Upper'], color='gray', alpha=0.1)
ax[0].set_title(f'{t} Price + Bollinger Bands')
ax[0].legend()

ax[1].plot(d.index, d['Portfolio'], color='green', label='Portfolio Value')
ax[1].set_title('Portfolio Value Over Time')
ax[1].legend()

st.pyplot(fig)
