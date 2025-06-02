import yfinance as yf, pandas as pd, numpy as np, streamlit as st, matplotlib.pyplot as plt
st.set_page_config(layout="wide"); st.title("⚡️ Lightning Trader AI v2.0")

t=st.sidebar.text_input("Ticker","AAPL"); s=st.sidebar.date_input("Start",pd.to_datetime("2025-01-01"))
e=st.sidebar.date_input("End",pd.to_datetime("2026-01-01")); d=yf.download(t,start=s,end=e,auto_adjust=False)

d['EMA12'],d['EMA26']=d['Close'].ewm(span=12).mean(),d['Close'].ewm(span=26).mean()
d['MACD'],d['Signal']=d['EMA12']-d['EMA26'],(d['EMA12']-d['EMA26']).ewm(span=9).mean()
r=d['Close'].diff(); up=r.where(r>0,0).rolling(14).mean(); down=-r.where(r<0,0).rolling(14).mean()
d['RSI']=100-(100/(1+(up/down))); d['MA20']=d['Close'].rolling(20).mean(); std=d['Close'].rolling(20).std()
d['Upper'],d['Lower']=d['MA20']+2*std,d['MA20']-2*std; d.dropna(inplace=True)

cash,pos,pv=10000,0,[]
for i in range(len(d)):
 p,n=d.iloc[i],d.iloc[max(i-1,0)]; cp=p['Close']; up=p['Upper']; lo=p['Lower']; rsi=p['RSI']; trend=p['EMA12']>p['EMA26']
 buy=p['MACD']>p['Signal'] and rsi<35 and cp<lo and trend and cash>=cp
 sell=p['MACD']<p['Signal'] and rsi>65 and cp>up and not trend and pos>0
 if buy: sh=cash//cp; cash-=sh*cp; pos=sh
 elif sell: cash+=pos*cp; pos=0
 pv.append(cash+pos*cp)

d['Portfolio']=pv
fig,ax=plt.subplots(2,1,figsize=(14,8),sharex=True)
ax[0].plot(d.index,d['Close'],label='Close'); ax[0].plot(d.index,d['Upper'],'--',alpha=0.5,label='Upper')
ax[0].plot(d.index,d['Lower'],'--',alpha=0.5,label='Lower'); ax[0].legend(); ax[0].set_title(f'{t} Price & Bands')
ax[1].plot(d.index,d['Portfolio'],label='Portfolio',color='green'); ax[1].legend(); ax[1].set_title("Value Over Time")
st.pyplot(fig)
