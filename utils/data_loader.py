import streamlit as st
import pandas as pd
import requests
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
import config

# API Base URL
API_BASE = 'http://localhost:5000/api'

@st.cache_data(ttl=300)
def fetch_data(endpoint):
    """Fetch data from API with caching"""
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

@st.cache_data(ttl=300)
def load_local_data():
    """Load data directly from file with caching"""
    try:
        df = pd.read_csv(config.PROCESSED_DATA_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return None

def format_number(num):
    """Format numbers with commas and handle floats"""
    if pd.isnull(num):
        return "N/A"
    if isinstance(num, float) and num.is_integer():
        return f"{int(num):,}"
    try:
        return f"{num:,.0f}" if isinstance(num, float) else f"{int(num):,}"
    except:
        return str(num)