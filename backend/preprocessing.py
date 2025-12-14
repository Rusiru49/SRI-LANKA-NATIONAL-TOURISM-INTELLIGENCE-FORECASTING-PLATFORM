import pandas as pd
import numpy as np
from datetime import datetime
import config

def load_data():
    """Load the collected data"""
    try:
        df = pd.read_csv(config.PROCESSED_DATA_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def add_season_features(df):
    """Add season indicators"""
    def get_season(month):
        if month in config.SEASONS['Southwest Monsoon']:
            return 'Southwest Monsoon'
        elif month in config.SEASONS['Northeast Monsoon']:
            return 'Northeast Monsoon'
        else:
            return 'Inter Monsoon'
    
    df['season'] = df['month'].apply(get_season)
    
    # One-hot encode seasons
    season_dummies = pd.get_dummies(df['season'], prefix='season')
    df = pd.concat([df, season_dummies], axis=1)
    
    return df

def add_holiday_features(df):
    """Add holiday/event flags"""
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    df['is_holiday'] = df['date_str'].isin(config.SRI_LANKAN_HOLIDAYS.keys()).astype(int)
    
    # Holiday proximity (within 7 days)
    df['near_holiday'] = 0
    holiday_dates = pd.to_datetime(list(config.SRI_LANKAN_HOLIDAYS.keys()))
    
    for idx, row in df.iterrows():
        date = row['date']
        days_to_holiday = min([abs((date - hd).days) for hd in holiday_dates] 
                              if len(holiday_dates) > 0 else [999])
        if days_to_holiday <= 7:
            df.at[idx, 'near_holiday'] = 1
    
    df = df.drop('date_str', axis=1)
    return df

def add_country_region(df):
    """Add country region grouping"""
    def get_region(country):
        for region, countries in config.COUNTRY_REGIONS.items():
            if country in countries:
                return region
        return 'Other'
    
    df['region'] = df['country'].apply(get_region)
    
    # One-hot encode regions
    region_dummies = pd.get_dummies(df['region'], prefix='region')
    df = pd.concat([df, region_dummies], axis=1)
    
    return df

def add_temporal_features(df):
    """Add temporal features"""
    df['quarter'] = df['date'].dt.quarter
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    # Cyclical encoding for month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df

def add_lag_features(df, lags=[1, 3, 6, 12]):
    """Add lagged features for time series"""
    # Sort by country and date
    df = df.sort_values(['country', 'date'])
    
    for lag in lags:
        df[f'arrivals_lag_{lag}'] = df.groupby('country')['arrivals'].shift(lag)
    
    # Rolling statistics
    df['arrivals_rolling_mean_3'] = df.groupby('country')['arrivals'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    df['arrivals_rolling_std_3'] = df.groupby('country')['arrivals'].transform(
        lambda x: x.rolling(window=3, min_periods=1).std()
    )
    
    return df

def add_growth_features(df):
    """Add growth rate features"""
    df = df.sort_values(['country', 'date'])
    
    # Year-over-year growth
    df['yoy_growth'] = df.groupby('country')['arrivals'].pct_change(12)
    
    # Month-over-month growth
    df['mom_growth'] = df.groupby('country')['arrivals'].pct_change(1)
    
    return df

def handle_missing_values(df):
    """Handle missing values"""
    # Fill NaN values in lag features with 0
    lag_cols = [col for col in df.columns if 'lag' in col or 'rolling' in col or 'growth' in col]
    df[lag_cols] = df[lag_cols].fillna(0)
    
    # Fill any other missing values
    df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
    
    return df

def preprocess_data():
    """Main preprocessing pipeline"""
    print("=" * 60)
    print("DATA PREPROCESSING")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data...")
    df = load_data()
    if df is None:
        print("Error: Could not load data")
        return None
    print(f"   Loaded {len(df)} records")
    
    # Add features
    print("\n2. Adding season features...")
    df = add_season_features(df)
    
    print("3. Adding holiday features...")
    df = add_holiday_features(df)
    
    print("4. Adding country region features...")
    df = add_country_region(df)
    
    print("5. Adding temporal features...")
    df = add_temporal_features(df)
    
    print("6. Adding lag features...")
    df = add_lag_features(df)
    
    print("7. Adding growth features...")
    df = add_growth_features(df)
    
    print("8. Handling missing values...")
    df = handle_missing_values(df)
    
    # Save processed data
    output_file = config.PROCESSED_DATA_FILE.replace('.csv', '_engineered.csv')
    df.to_csv(output_file, index=False)
    
    print("\n" + "=" * 60)
    print("Preprocessing completed!")
    print("=" * 60)
    print(f"Final shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nProcessed data saved to: {output_file}")
    
    return df

if __name__ == '__main__':
    df = preprocess_data()
    
    if df is not None:
        print("\n" + "=" * 60)
        print("SAMPLE OF PROCESSED DATA")
        print("=" * 60)
        print(df.head())
        
        print("\n" + "=" * 60)
        print("DATA STATISTICS")
        print("=" * 60)
        print(df.describe())