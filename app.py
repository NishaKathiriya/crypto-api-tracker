import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Crypto API Tracker", layout="wide")
st.title("🚀 Real-Time Crypto Dashboard")

# Load API Key
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

# Clean column names for easier plotting
df.columns = df.columns.str.replace('quote.USD.', '', regex=False)

# Display current prices
st.subheader("💱 Current Prices")
st.dataframe(df[['name', 'symbol', 'price', 'percent_change_1h', 'Timestamp']])

# Setup tabs for visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Cap", 
    "📈 Price vs Volume", 
    "📈 Percent Change Trend", 
    "📉 Volume Change %", 
    "🥧 Market Dominance"
])

with tab1:
    st.subheader("🏦 Top 10 by Market Cap")
    top_marketcap = df[['name', 'market_cap']].sort_values(by='market_cap', ascending=False)
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=top_marketcap, x='name', y='market_cap', ax=ax1)
    ax1.set_ylabel("Market Cap (USD)")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with tab2:
    st.subheader("📊 Price vs. 24h Volume")
    fig2, ax2 = plt.subplots()
    sns.scatterplot(data=df, x='price', y='volume_24h', hue='name', ax=ax2)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel("Price (USD)")
    ax2.set_ylabel("24h Volume (USD)")
    st.pyplot(fig2)

with tab3:
    st.subheader("📈 Percent Change (1h - 90d)")
    df_melt = df[['name', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d',
                  'percent_change_30d', 'percent_change_60d', 'percent_change_90d']]
    df_melt = df_melt.melt(id_vars='name', var_name='Timeframe', value_name='Percent Change')
    df_melt['Timeframe'] = df_melt['Timeframe'].str.replace('percent_change_', '')
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.pointplot(data=df_melt, x='Timeframe', y='Percent Change', hue='name', ax=ax3)
    st.pyplot(fig3)

with tab4:
    st.subheader("🔁 24h Volume Change %")
    volume_change = df[['name', 'volume_change_24h']].sort_values(by='volume_change_24h', ascending=False)
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=volume_change, x='name', y='volume_change_24h', ax=ax4)
    ax4.set_ylabel("Volume Change (24h %)")
    plt.xticks(rotation=45)
    st.pyplot(fig4)

with tab5:
    st.subheader("🥧 Market Cap Dominance")
    dominance_top5 = dominance.sort_values(by='market_cap_dominance', ascending=False).head(5)
    fig5, ax5 = plt.subplots()
    ax5.pie(
        dominance['market_cap_dominance'], 
        labels=dominance.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        pctdistance=0.8, 
        labeldistance=1.1
    )
    ax5.axis('equal')
    st.pyplot(fig5)

# Footer
st.markdown("---")
st.markdown("🔒 API secured with Streamlit secrets · Built by **Nisha Kathiriya**")
