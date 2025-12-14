from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from tensorflow import keras
import config
import os

app = Flask(__name__)
CORS(app)

# Load models and data
def load_models():
    models = {}
    try:
        models['prophet'] = joblib.load(config.PROPHET_MODEL_FILE)
        print("Prophet model loaded")
    except:
        print("Prophet model not found")
    
    try:
        models['lstm'] = keras.models.load_model(config.LSTM_MODEL_FILE)
        print("LSTM model loaded")
    except:
        print("LSTM model not found")
    
    try:
        models['scaler'] = joblib.load(config.SCALER_FILE)
        print("Scaler loaded")
    except:
        print("Scaler not found")
    
    return models

models = load_models()

def load_data():
    try:
        df = pd.read_csv(config.PROCESSED_DATA_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return None

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/overview', methods=['GET'])
def overview():
    """Get overall statistics"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    total_arrivals = int(df['arrivals'].sum())
    avg_monthly = int(df.groupby('date')['arrivals'].sum().mean())
    
    # Recent trend
    recent_months = df[df['date'] >= df['date'].max() - pd.DateOffset(months=6)]
    recent_total = int(recent_months['arrivals'].sum())
    
    # Top countries
    top_countries = df.groupby('country')['arrivals'].sum().nlargest(10)
    
    return jsonify({
        'total_arrivals': total_arrivals,
        'avg_monthly_arrivals': avg_monthly,
        'recent_6_months': recent_total,
        'top_countries': top_countries.to_dict(),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d'),
            'end': df['date'].max().strftime('%Y-%m-%d')
        }
    })

@app.route('/api/monthly-trends', methods=['GET'])
def monthly_trends():
    """Get monthly arrival trends"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    year = request.args.get('year', type=int)
    
    if year:
        df = df[df['year'] == year]
    
    monthly = df.groupby('date')['arrivals'].sum().reset_index()
    monthly['date'] = monthly['date'].dt.strftime('%Y-%m-%d')
    
    return jsonify(monthly.to_dict('records'))

@app.route('/api/country-analysis', methods=['GET'])
def country_analysis():
    """Get country-wise analysis"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    country = request.args.get('country')
    
    if country:
        df = df[df['country'] == country]
        trends = df.groupby('date')['arrivals'].sum().reset_index()
        trends['date'] = trends['date'].dt.strftime('%Y-%m-%d')
        return jsonify({
            'country': country,
            'trends': trends.to_dict('records')
        })
    else:
        # All countries summary
        countries = df.groupby('country').agg({
            'arrivals': ['sum', 'mean']
        }).reset_index()
        countries.columns = ['country', 'total', 'average']
        countries = countries.sort_values('total', ascending=False)
        return jsonify(countries.to_dict('records'))

@app.route('/api/seasonal-analysis', methods=['GET'])
def seasonal_analysis():
    """Get seasonal patterns"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    # Monthly patterns
    monthly_avg = df.groupby('month')['arrivals'].mean().reset_index()
    monthly_avg['month_name'] = monthly_avg['month'].apply(
        lambda x: pd.Timestamp(2024, x, 1).strftime('%B')
    )
    
    return jsonify({
        'monthly_patterns': monthly_avg.to_dict('records')
    })

@app.route('/api/top-countries', methods=['GET'])
def top_countries():
    """Get top source countries"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    limit = request.args.get('limit', default=15, type=int)
    year = request.args.get('year', type=int)
    
    if year:
        df = df[df['year'] == year]
    
    top = df.groupby('country')['arrivals'].sum().nlargest(limit).reset_index()
    
    return jsonify(top.to_dict('records'))

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """Get forecast data"""
    forecast_file = os.path.join(config.PROCESSED_DATA_DIR, 'forecast.csv')
    
    try:
        forecast_df = pd.read_csv(forecast_file)
        forecast_df['date'] = pd.to_datetime(forecast_df['date']).dt.strftime('%Y-%m-%d')
        return jsonify(forecast_df.to_dict('records'))
    except:
        return jsonify({'error': 'Forecast not available'}), 404

@app.route('/api/year-comparison', methods=['GET'])
def year_comparison():
    """Compare multiple years"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    years = df['year'].unique().tolist()
    
    comparison = []
    for year in sorted(years):
        year_data = df[df['year'] == year]
        total = int(year_data['arrivals'].sum())
        avg_monthly = int(year_data.groupby('month')['arrivals'].sum().mean())
        
        comparison.append({
            'year': int(year),
            'total_arrivals': total,
            'avg_monthly': avg_monthly
        })
    
    return jsonify(comparison)

@app.route('/api/regional-analysis', methods=['GET'])
def regional_analysis():
    """Get regional analysis"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    # Add region if not present
    def get_region(country):
        for region, countries in config.COUNTRY_REGIONS.items():
            if country in countries:
                return region
        return 'Other'
    
    df['region'] = df['country'].apply(get_region)
    
    regional = df.groupby('region')['arrivals'].sum().reset_index()
    regional = regional.sort_values('arrivals', ascending=False)
    
    return jsonify(regional.to_dict('records'))

@app.route('/api/growth-rates', methods=['GET'])
def growth_rates():
    """Get year-over-year growth rates"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    yearly = df.groupby('year')['arrivals'].sum().reset_index()
    yearly['yoy_growth'] = yearly['arrivals'].pct_change() * 100
    yearly = yearly.dropna()
    
    return jsonify(yearly.to_dict('records'))

@app.route('/api/available-years', methods=['GET'])
def available_years():
    """Get list of available years"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    years = sorted(df['year'].unique().tolist())
    return jsonify({'years': [int(y) for y in years]})

@app.route('/api/available-countries', methods=['GET'])
def available_countries():
    """Get list of available countries"""
    df = load_data()
    if df is None:
        return jsonify({'error': 'Data not found'}), 404
    
    countries = sorted(df['country'].unique().tolist())
    return jsonify({'countries': countries})

if __name__ == '__main__':
    print("=" * 60)
    print("STARTING SRI LANKA TOURISM API SERVER")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  - GET /api/health")
    print("  - GET /api/overview")
    print("  - GET /api/monthly-trends")
    print("  - GET /api/country-analysis")
    print("  - GET /api/seasonal-analysis")
    print("  - GET /api/top-countries")
    print("  - GET /api/forecast")
    print("  - GET /api/year-comparison")
    print("  - GET /api/regional-analysis")
    print("  - GET /api/growth-rates")
    print("  - GET /api/available-years")
    print("  - GET /api/available-countries")
    print("\n" + "=" * 60)
    print("Server running on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)