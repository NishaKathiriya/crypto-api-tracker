import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Crypto API Tracker", layout="wide")
st.title("🚀 Real-Time Crypto Dashboard")

# Load API Key from Streamlit secrets
api_key = st.secrets["CMC_API_KEY"]

# API request
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {'start': '1', 'limit': '10', 'convert': 'USD'}
headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}

try:
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()['data']
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# Normalize and timestamp
df = pd.json_normalize(data)
df['Timestamp'] = datetime.now()
df.columns = df.columns.str.replace('quote.USD.', '', regex=False)

st.subheader("💱 Current Prices Table")

selected_table_coins = st.multiselect(
    "🔍 Filter table by cryptocurrencies",
    options=df['name'].unique().tolist(),
    default=df['name'].unique().tolist(),
    key="table_filter"
)

filtered_table_df = df[df['name'].isin(selected_table_coins)]

st.dataframe(filtered_table_df[['name', 'symbol', 'price', 'percent_change_1h', 'Timestamp']])

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Cap", 
    "📈 Price vs Volume", 
    "📉 Percent Change", 
    "🔁 Volume Change", 
    "🥧 Dominance"
])

import plotly.express as px

with tab1:
    st.subheader("🏦 Top 10 by Market Cap")
    st.caption("This bar chart displays the top cryptocurrencies by market capitalization (USD), allowing you to compare how much total value each coin holds in the market.")

    selected_coins = st.multiselect(
        "🔍 Select cryptocurrencies to display",
        df['name'].unique(),
        df['name'].unique(),
        key="tab1_filter"
    )

    filtered_df = df[df['name'].isin(selected_coins)]
    top_marketcap = filtered_df[['name', 'market_cap']].sort_values(by='market_cap', ascending=False)

    # ✅ Plotly Express Bar Chart
    fig1 = px.bar(
        top_marketcap,
        x='name',
        y='market_cap',
        color='name',
        labels={'name': 'Cryptocurrency', 'market_cap': 'Market Cap (USD)'},
        title='Top 10 by Market Cap'
    )
    fig1.update_layout(
        template='plotly_dark',
        xaxis_title='Cryptocurrency',
        yaxis_title='Market Cap (USD)',
        showlegend=False  # hide redundant color legend
    )

    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("📊 Price vs. 24h Volume")
    st.caption("This scatter plot compares the price of each selected cryptocurrency against its 24-hour trading volume. Log scale helps visualize both high and low value coins.")
    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab2_filter")
    filtered_df = df[df['name'].isin(selected_coins)]

    fig2 = go.Figure()
    for name in filtered_df['name'].unique():
        temp = filtered_df[filtered_df['name'] == name]
        fig2.add_trace(go.Scatter(
            x=temp['price'],
            y=temp['volume_24h'],
            mode='markers',
            name=name,
            marker=dict(size=12, line=dict(width=1))
        ))

    fig2.update_layout(
        xaxis_type="log",
        yaxis_type="log",
        xaxis_title="Price (USD)",
        yaxis_title="24h Volume (USD)",
        template="plotly_dark"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("📈 Percent Change (1h - 90d)")
    st.caption("This point plot shows the percentage change in price for each cryptocurrency across multiple timeframes — from 90 days down to 1 hour.")

    df_melt = df[['name', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d',
                  'percent_change_30d', 'percent_change_60d', 'percent_change_90d']]
    df_melt = df_melt.melt(id_vars='name', var_name='Timeframe', value_name='Percent Change')
    df_melt['Timeframe'] = df_melt['Timeframe'].str.replace('percent_change_', '')

    order_desc = ['90d', '60d', '30d', '7d', '24h', '1h']
    df_melt['Timeframe'] = pd.Categorical(df_melt['Timeframe'], categories=order_desc, ordered=True)

    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab3_filter")
    filtered_df = df_melt[df_melt['name'].isin(selected_coins)]

    fig3 = go.Figure()
    for name in filtered_df['name'].unique():
        temp = filtered_df[filtered_df['name'] == name]
        fig3.add_trace(go.Scatter(x=temp['Timeframe'], y=temp['Percent Change'], name=name, mode='lines+markers'))

    fig3.update_layout(title="Percent Change Trend", xaxis_title="Timeframe", yaxis_title="Percent Change", template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("🔁 24h Volume Change %")
    st.caption("This bar chart shows how the 24-hour trading volume has changed (in %) for each cryptocurrency. It helps identify sudden spikes or drops in market activity.")
    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab4_filter")
    filtered_df = df[df['name'].isin(selected_coins)]
    volume_change = filtered_df[['name', 'volume_change_24h']].sort_values(by='volume_change_24h', ascending=False)

    fig4 = go.Figure(go.Bar(
        x=volume_change['name'],
        y=volume_change['volume_change_24h'],
        marker_color='indianred'
    ))
    fig4.update_layout(title="24h Volume Change %", xaxis_title="Cryptocurrency", yaxis_title="Change (%)", template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

with tab5:
    st.subheader("🥧 Market Cap Dominance (Top 5)")
    st.caption("This pie chart shows the top 5 cryptocurrencies based on their market cap dominance — their share of the entire crypto market. It helps visualize how dominant coins like BTC and ETH are compared to others.")

    dominance = df[['name', 'market_cap_dominance']].sort_values(by='market_cap_dominance', ascending=False).head(5)

    fig5 = go.Figure(go.Pie(
        labels=dominance['name'],
        values=dominance['market_cap_dominance'],
        hole=0.3
    ))
    fig5.update_layout(title="Market Cap Dominance (Top 5)", template="plotly_dark")
    st.plotly_chart(fig5, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🔒 API secured with Streamlit secrets • Built by **Nisha Kathiriya**")
