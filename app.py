import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crypto API Tracker", layout="wide")
st.title("\U0001F680 Real-Time Crypto Dashboard")

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

# Multiselect for table as well (optional)
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
    "\U0001F4CA Market Cap", 
    "\U0001F4C8 Price vs Volume", 
    "\U0001F4C9 Percent Change", 
    "\U0001F501 Volume Change", 
    "\U0001F967 Dominance"
])

with tab1:
    st.subheader("🏦 Top 10 by Market Cap")
    st.caption("This bar chart displays the top cryptocurrencies by market capitalization (USD), allowing you to compare how much total value each coin holds in the market.")
    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab1_filter")
    filtered_df = df[df['name'].isin(selected_coins)]
    top_marketcap = filtered_df[['name', 'market_cap']].sort_values(by='market_cap', ascending=False)
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=top_marketcap, x='name', y='market_cap', ax=ax1)
    ax1.set_ylabel("Market Cap (USD)")
    plt.xticks(rotation=45)
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    st.pyplot(fig1)

with tab2:
    st.subheader("📊 Price vs. 24h Volume")
    st.caption("This scatter plot compares the price of each selected cryptocurrency against its 24-hour trading volume. Log scale helps visualize both high and low value coins.")
    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab2_filter")
    filtered_df = df[df['name'].isin(selected_coins)]
    fig2, ax2 = plt.subplots()
    sns.scatterplot(data=filtered_df, x='price', y='volume_24h', hue='name', ax=ax2)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel("Price (USD)")
    ax2.set_ylabel("24h Volume (USD)")
    st.pyplot(fig2)

with tab3:
    st.subheader("📈 Percent Change (1h - 90d)")
    st.caption("This point plot shows the percentage change in price for each cryptocurrency across multiple timeframes — from 90 days down to 1 hour.")

    df_melt = df[['name', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d',
                  'percent_change_30d', 'percent_change_60d', 'percent_change_90d']]

    df_melt = df_melt.melt(id_vars='name', var_name='Timeframe', value_name='Percent Change')
    df_melt['Timeframe'] = df_melt['Timeframe'].str.replace('percent_change_', '')

    # Explicit descending order for X-axis
    order_desc = ['90d', '60d', '30d', '7d', '24h', '1h']
    df_melt['Timeframe'] = pd.Categorical(df_melt['Timeframe'], categories=order_desc, ordered=True)

    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab3_filter")
    filtered_df = df_melt[df_melt['name'].isin(selected_coins)]

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.pointplot(data=filtered_df, x='Timeframe', y='Percent Change', hue='name', ax=ax3)
    plt.tight_layout()
    ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    st.pyplot(fig3)



with tab4:
    st.subheader("🔁 24h Volume Change %")
    st.caption("This bar chart shows how the 24-hour trading volume has changed (in %) for each cryptocurrency. It helps identify sudden spikes or drops in market activity.")
    selected_coins = st.multiselect("🔍 Select cryptocurrencies to display", df['name'].unique(), df['name'].unique(), key="tab4_filter")
    filtered_df = df[df['name'].isin(selected_coins)]
    volume_change = filtered_df[['name', 'volume_change_24h']].sort_values(by='volume_change_24h', ascending=False)
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=volume_change, x='name', y='volume_change_24h', ax=ax4)
    ax4.set_ylabel("Volume Change (24h %)")
    plt.xticks(rotation=45)
    st.pyplot(fig4)

with tab5:
    st.subheader("🥧 Market Cap Dominance (Top 5)")
    st.caption("This pie chart shows the top 5 cryptocurrencies based on their market cap dominance — their share of the entire crypto market. It helps visualize how dominant coins like BTC and ETH are compared to others.")

    # Sort and get top 5 by dominance
    dominance = df[['name', 'market_cap_dominance']].sort_values(by='market_cap_dominance', ascending=False).head(5)

    fig5, ax5 = plt.subplots()
    ax5.pie(
        dominance['market_cap_dominance'],
        labels=dominance['name'],
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.8,
        labeldistance=1.1
    )
    ax5.axis('equal')
    st.pyplot(fig5)




# Footer
st.markdown("---")
st.markdown("\U0001F512 API secured with Streamlit secrets • Built by **Nisha Kathiriya**")
