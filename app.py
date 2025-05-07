# streamlit_app.py

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("🚀 Real-Time Crypto Dashboard")

# Load API Key securely from Streamlit secrets
api_key = st.secrets["CMC_API_KEY"]

# API request setup
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {'start': '1', 'limit': '10', 'convert': 'USD'}
headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}

# Make request
try:
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()['data']
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# Normalize data
df = pd.json_normalize(data)
df['Timestamp'] = datetime.now()

# Display price data
st.subheader("💱 Current Prices")
st.dataframe(df[['name', 'symbol', 'quote.USD.price', 'quote.USD.percent_change_1h', 'Timestamp']])

# Percent change trends
df7 = df[['name', 'quote.USD.percent_change_1h', 'quote.USD.percent_change_24h',
        'quote.USD.percent_change_7d', 'quote.USD.percent_change_30d',
        'quote.USD.percent_change_60d', 'quote.USD.percent_change_90d']]
df7 = df7.melt(id_vars='name', var_name='percent_change', value_name='values')
df7['percent_change'] = df7['percent_change'].str.replace('quote.USD.percent_change_', '')

# Plot
st.subheader("📈 Percent Change Trend")
fig, ax = plt.subplots(figsize=(10, 5))
sns.pointplot(data=df7, x='percent_change', y='values', hue='name', ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)
