import os
import requests
import pdfplumber
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import config

def generate_sample_data():
    """Generate sample tourism data for demonstration"""
    print("Generating sample tourism data...")
    
    # Generate monthly data from 2019-2024
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2025, 11, 1)
    
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Top countries
    countries = ['India', 'China', 'United Kingdom', 'Germany', 'France',
                 'United States', 'Australia', 'Russia', 'Japan', 'Maldives',
                 'Netherlands', 'Switzerland', 'Italy', 'Canada', 'UAE']
    
    data = []
    
    for date in dates:
        month = date.month
        year = date.year
        
        # Base arrivals with seasonality
        base = 15000
        
        # Seasonal patterns (high season: Dec-Mar, low season: May-Sep)
        if month in [12, 1, 2, 3]:
            seasonal_factor = 1.8
        elif month in [5, 6, 7, 8, 9]:
            seasonal_factor = 0.6
        else:
            seasonal_factor = 1.0
        
        # COVID impact (2020-2021)
        if year == 2020 and month >= 3:
            covid_factor = 0.05
        elif year == 2020:
            covid_factor = 0.8
        elif year == 2021:
            covid_factor = 0.2 + (month / 12) * 0.3
        else:
            covid_factor = 1.0
        
        # Economic crisis impact (2022)
        if year == 2022:
            crisis_factor = 0.4
        else:
            crisis_factor = 1.0
        
        # Recovery (2023-2024)
        if year == 2023:
            recovery_factor = 0.6 + (month / 24)
        elif year == 2024:
            recovery_factor = 1.2
        else:
            recovery_factor = 1.0
        
        # Generate data for each country
        for i, country in enumerate(countries):
            # Country-specific base
            country_base = base * (1 - i * 0.05)
            
            # Calculate arrivals with some randomness
            arrivals = int(country_base * seasonal_factor * covid_factor * 
                          crisis_factor * recovery_factor * 
                          (0.8 + np.random.random() * 0.4))
            
            data.append({
                'date': date,
                'year': year,
                'month': month,
                'country': country,
                'arrivals': max(arrivals, 0)
            })
    
    df = pd.DataFrame(data)
    
    # Add weather data (simplified)
    df['avg_temperature'] = df['month'].apply(lambda m: 
        28 if m in [3, 4, 5] else 26 if m in [6, 7, 8] else 27)
    df['rainfall_mm'] = df['month'].apply(lambda m:
        250 if m in [5, 10, 11] else 100 if m in [6, 9] else 50)
    
    # Save to CSV
    output_file = config.PROCESSED_DATA_FILE
    df.to_csv(output_file, index=False)
    print(f"Sample data generated: {output_file}")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df

def scrape_sltda_pdfs():
    """
    Scrape actual SLTDA PDFs (when available)
    This is a template - actual implementation depends on SLTDA website structure
    """
    print("Attempting to scrape SLTDA data...")
    
    # This would be actual scraping logic
    # For now, we'll use sample data
    print("Using sample data generation instead...")
    
    return generate_sample_data()

def extract_pdf_tables(pdf_path):
    """Extract tables from PDF using pdfplumber"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                all_tables.extend(tables)
            return all_tables
    except Exception as e:
        print(f"Error extracting PDF {pdf_path}: {e}")
        return []

def extract_all_pdfs_in_raw():
    """Extract tables from all PDFs in the raw data directory and print summary."""
    raw_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')
    pdf_files = [f for f in os.listdir(raw_dir) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files in {raw_dir}.")
    for pdf_file in pdf_files:
        pdf_path = os.path.join(raw_dir, pdf_file)
        print(f"\nExtracting tables from: {pdf_file}")
        tables = extract_pdf_tables(pdf_path)
        print(f"  Extracted {len(tables)} tables.")
    print("\nAll PDFs extraction attempted.")

def fetch_weather_data(lat=7.8731, lon=80.7718, start_date=None, end_date=None):
    """
    Fetch weather data from Open-Meteo API for Sri Lanka
    Default coordinates: Colombo
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    url = config.WEATHER_API_URL
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'daily': 'temperature_2m_mean,precipitation_sum',
        'timezone': 'Asia/Colombo'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(data['daily']['time']),
            'temperature': data['daily']['temperature_2m_mean'],
            'precipitation': data['daily']['precipitation_sum']
        })
        
        return df
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("DATA COLLECTION MODULE")
    print("=" * 60)
    
    # Extract all PDFs in raw directory
    extract_all_pdfs_in_raw()
    
    # Generate/collect data
    df = scrape_sltda_pdfs()
    
    print("\n" + "=" * 60)
    print("Data collection completed successfully!")
    print("=" * 60)
    print(f"\nData shape: {df.shape}")
    print(f"\nFirst few records:")
    print(df.head())
    print(f"\nData saved to: {config.PROCESSED_DATA_FILE}")