import os
from datetime import datetime

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

# Create directories
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

# Data sources
SLTDA_BASE_URL = "https://www.sltda.gov.lk"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Sri Lankan holidays and events (sample - extend as needed)
SRI_LANKAN_HOLIDAYS = {
    '2020-01-01': 'New Year',
    '2020-01-14': 'Thai Pongal',
    '2020-02-04': 'Independence Day',
    '2020-04-10': 'Sinhala Tamil New Year',
    '2020-04-13': 'Sinhala Tamil New Year',
    '2020-05-01': 'May Day',
    '2020-05-07': 'Vesak Full Moon',
    '2020-05-25': 'Eid al-Fitr',
    '2020-12-25': 'Christmas',
    '2021-01-01': 'New Year',
    '2021-01-14': 'Thai Pongal',
    '2021-02-04': 'Independence Day',
    '2021-04-13': 'Sinhala Tamil New Year',
    '2021-04-14': 'Sinhala Tamil New Year',
    '2021-05-01': 'May Day',
    '2021-05-26': 'Vesak Full Moon',
    '2021-12-25': 'Christmas',
    '2022-01-01': 'New Year',
    '2022-01-14': 'Thai Pongal',
    '2022-02-04': 'Independence Day',
    '2022-04-13': 'Sinhala Tamil New Year',
    '2022-04-14': 'Sinhala Tamil New Year',
    '2022-05-01': 'May Day',
    '2022-05-16': 'Vesak Full Moon',
    '2022-12-25': 'Christmas',
    '2023-01-01': 'New Year',
    '2023-01-14': 'Thai Pongal',
    '2023-02-04': 'Independence Day',
    '2023-04-13': 'Sinhala Tamil New Year',
    '2023-04-14': 'Sinhala Tamil New Year',
    '2023-05-01': 'May Day',
    '2023-05-05': 'Vesak Full Moon',
    '2023-12-25': 'Christmas',
    '2024-01-01': 'New Year',
    '2024-01-14': 'Thai Pongal',
    '2024-02-04': 'Independence Day',
    '2024-04-13': 'Sinhala Tamil New Year',
    '2024-04-14': 'Sinhala Tamil New Year',
    '2024-05-01': 'May Day',
    '2024-05-23': 'Vesak Full Moon',
    '2024-12-25': 'Christmas',
}

# Country groupings for analysis
COUNTRY_REGIONS = {
    'Asia': ['India', 'China', 'Japan', 'South Korea', 'Thailand', 'Malaysia', 
             'Singapore', 'Indonesia', 'Philippines', 'Vietnam', 'Bangladesh',
             'Pakistan', 'Hong Kong', 'Taiwan', 'Myanmar', 'Cambodia'],
    'Europe': ['United Kingdom', 'Germany', 'France', 'Russia', 'Italy', 
               'Netherlands', 'Spain', 'Switzerland', 'Belgium', 'Austria',
               'Poland', 'Ukraine', 'Czech Republic', 'Sweden', 'Denmark'],
    'Middle East': ['Saudi Arabia', 'UAE', 'Qatar', 'Kuwait', 'Oman', 
                    'Bahrain', 'Israel', 'Turkey', 'Iran', 'Jordan'],
    'Americas': ['United States', 'Canada', 'Brazil', 'Argentina', 'Mexico',
                 'Colombia', 'Chile', 'Peru'],
    'Oceania': ['Australia', 'New Zealand'],
    'Africa': ['South Africa', 'Egypt', 'Kenya', 'Nigeria', 'Morocco']
}

# Seasons in Sri Lanka
SEASONS = {
    'Southwest Monsoon': [5, 6, 7, 8, 9],      # May-Sep
    'Northeast Monsoon': [10, 11, 12, 1, 2],   # Oct-Feb
    'Inter Monsoon': [3, 4]                     # Mar-Apr
}

# Model parameters - XGBoost (replaces Prophet)
XGBOOST_PARAMS = {
    'objective': 'reg:squarederror',
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 200,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'early_stopping_rounds': 20
}

# LSTM parameters
LSTM_PARAMS = {
    'units': 100,
    'epochs': 100,
    'batch_size': 32,
    'lookback': 12,
    'learning_rate': 0.001
}

# File names
PROCESSED_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, 'tourist_arrivals.csv')
XGBOOST_MODEL_FILE = os.path.join(MODELS_DIR, 'xgboost_model.pkl')
XGBOOST_FEATURES_FILE = os.path.join(MODELS_DIR, 'xgb_feature_cols.pkl')
LSTM_MODEL_FILE = os.path.join(MODELS_DIR, 'lstm_model.h5')
SCALER_FILE = os.path.join(MODELS_DIR, 'scaler.pkl')

# Legacy file names (for backward compatibility)
PROPHET_MODEL_FILE = os.path.join(MODELS_DIR, 'prophet_model.pkl')  # Will be replaced with XGBoost