import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------- PAGE SETTINGS ---------------------------
st.set_page_config(page_title="Algo Trading Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Multi-Stock Algo Trading Dashboard")

# --------------------------- LOAD DATA ---------------------------
df = pd.read_excel("power_equity_zerodha_5minute .xlsx")  # your full dataset

# Combine date and time
df['Datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
df = df[['Datetime', 'tradingsymbol', 'close']].copy()

# --------------------------- PREPARE STRATEGY ---------------------------
results = []
for symbol in df['tradingsymbol'].unique():
    temp = df[df['tradingsymbol'] == symbol].copy()
    temp = temp.sort_values('Datetime')
    temp['MA_5'] = temp['close'].rolling(5).mean()
    temp['MA_15'] = temp['close'].rolling(15).mean()
    temp['signal'] = 0
    temp.loc[temp['MA_5'] > temp['MA_15'], 'signal'] = 1
    temp.loc[temp['MA_5'] < temp['MA_15'], 'signal'] = -1
    temp['return'] = temp['close'].pct_change()
    temp['strategy_return'] = temp['return'] * temp['signal'].shift(1)
    temp['cumulative_return'] = (1 + temp['strategy_return']).cumprod()
    results.append(temp)

final_df = pd.concat(results)

# --------------------------- SIDEBAR CONTROLS ---------------------------
st.sidebar.header("Controls")
symbol = st.sidebar.selectbox("Select Stock", final_df['tradingsymbol'].unique())

# Filter for selected stock
data = final_df[final_df['tradingsymbol'] == symbol].copy()

# Date range
min_date = data['Datetime'].min()
max_date = data['Datetime'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
data = data[(data['Datetime'].dt.date >= start_date) & (data['Datetime'].dt.date <= end_date)]

# --------------------------- PERFORMANCE METRICS ---------------------------
cumulative_return = data['cumulative_return'].iloc[-1]
total_trades = data['signal'].abs().sum()
wins = ((data['strategy_return'] > 0) & (data['signal'].shift(1) != 0)).sum()
win_rate = (wins / total_trades * 100) if total_trades != 0 else 0
roll_max = data['cumulative_return'].cummax()
drawdown = (data['cumulative_return'] - roll_max) / roll_max
max_drawdown = drawdown.min()

# --------------------------- TABS ---------------------------
tab1, tab2, tab3 = st.tabs(["📉 Chart", "📈 Metrics", "ℹ️ Stock Info"])

# --------------------------- TAB 1: CHART ---------------------------
with tab1:
    st.subheader(f"Price Chart & Signals: {symbol}")
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(data['Datetime'], data['close'], label="Close Price")
    ax.plot(data['Datetime'], data['MA_5'], label="MA 5")
    ax.plot(data['Datetime'], data['MA_15'], label="MA 15")
    # Buy/Sell markers
    ax.scatter(data[data['signal'] == 1]['Datetime'],
               data[data['signal'] == 1]['close'],
               marker='^', color='green', s=100, label='BUY')
    ax.scatter(data[data['signal'] == -1]['Datetime'],
               data[data['signal'] == -1]['close'],
               marker='v', color='red', s=100, label='SELL')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# --------------------------- TAB 2: METRICS ---------------------------
with tab2:
    st.subheader(f"Performance Metrics: {symbol}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Cumulative Return", round(cumulative_return, 4))
    col2.metric("Total Trades", int(total_trades))
    col3.metric("Win Rate (%)", round(win_rate, 2))
    col4.metric("Max Drawdown", round(max_drawdown, 4))

    # Download button
    metrics_df = pd.DataFrame({
        "Final Cumulative Return": [round(cumulative_return, 4)],
        "Total Trades": [int(total_trades)],
        "Win Rate (%)": [round(win_rate, 2)],
        "Max Drawdown": [round(max_drawdown, 4)]
    })
    st.download_button(
        label="📥 Download Metrics as CSV",
        data=metrics_df.to_csv(index=False),
        file_name=f"{symbol}_metrics.csv",
        mime="text/csv"
    )

# --------------------------- TAB 3: STOCK INFO ---------------------------
with tab3:
    st.subheader(f"Stock Overview: {symbol}")
    st.write(f"Total Data Points: {len(data)}")
    st.write(f"Date Range: {data['Datetime'].min()} to {data['Datetime'].max()}")
    st.write("Strategy: Moving Average Crossover (MA 5 & MA 15)")
    st.write("Buy Signal: MA 5 crosses above MA 15")
    st.write("Sell Signal: MA 5 crosses below MA 15")
    st.write("Note: Strategy is for demonstration and educational purposes")
