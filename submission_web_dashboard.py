import streamlit as st
import pandas as pd
import numpy as np

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="BatraHedge Algo Trading Dashboard",
    layout="wide"
)

st.title("📈 BatraHedge Algo-Trading Dashboard")
st.markdown("Moving Average Crossover Strategy (MA 5 / MA 15)")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("raw_backtest_results.csv")
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    return df

df = load_data()

# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("🔧 Controls")

symbols = sorted(df["tradingsymbol"].unique())
selected_symbol = st.sidebar.selectbox("Select Stock", symbols)

symbol_df = df[df["tradingsymbol"] == selected_symbol].copy()

start_date = st.sidebar.date_input(
    "Start Date", symbol_df["Datetime"].min().date()
)
end_date = st.sidebar.date_input(
    "End Date", symbol_df["Datetime"].max().date()
)

symbol_df = symbol_df[
    (symbol_df["Datetime"].dt.date >= start_date) &
    (symbol_df["Datetime"].dt.date <= end_date)
]

# -------------------------
# Metrics
# -------------------------
final_return = symbol_df["cumulative_return"].iloc[-1]
total_trades = symbol_df["signal"].abs().sum()
max_dd = symbol_df["drawdown"].min()

col1, col2, col3 = st.columns(3)
col1.metric("📊 Final Cumulative Return", f"{final_return:.4f}")
col2.metric("🔁 Total Trades", int(total_trades))
col3.metric("⚠️ Max Drawdown", f"{max_dd:.4f}")

# -------------------------
# Price Chart
# -------------------------
st.subheader("📉 Price Chart with Moving Averages")

chart_df = symbol_df.set_index("Datetime")[["close", "ma_fast", "ma_slow"]]
st.line_chart(chart_df)

# -------------------------
# Buy / Sell Signals
# -------------------------
st.subheader("🟢 Buy / 🔴 Sell Signals")

signal_df = symbol_df[symbol_df["signal"] != 0][
    ["Datetime", "close", "signal"]
]

st.dataframe(signal_df, use_container_width=True)

# -------------------------
# Raw Data
# -------------------------
with st.expander("📄 View Raw Backtest Data"):
    st.dataframe(symbol_df.tail(200), use_container_width=True)

# -------------------------
# Download
# -------------------------
st.download_button(
    "⬇️ Download Backtest CSV",
    symbol_df.to_csv(index=False),
    file_name=f"{selected_symbol}_backtest.csv"
)
