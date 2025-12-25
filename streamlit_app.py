import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
import config

# Import page modules
from pages import overview_page, trends_page, country_insight, ai_forecast

# Import new API-powered page
try:
    from pages import weather_tourism
    WEATHER_TOURISM_AVAILABLE = True
except ImportError:
    WEATHER_TOURISM_AVAILABLE = False
    print("⚠️ weather_tourism.py not found. API features will be unavailable.")

# Import shared utilities
from utils.data_loader import fetch_data, load_local_data
from utils.styles import apply_custom_styles

# Import API services for status checking
try:
    from backend.api_config import APIConfig
    API_CONFIG_AVAILABLE = True
except ImportError:
    API_CONFIG_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="🇱🇰 Sri Lanka Tourism Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Enhanced tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 12px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px 24px;
        color: white;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: #43e97b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        border-color: #43e97b !important;
        color: #1a1a2e !important;
    }
    
    /* API Status Badges */
    .api-status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 4px 0;
    }
    
    .api-active {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #1a1a2e;
    }
    
    .api-inactive {
        background: rgba(255, 255, 255, 0.1);
        color: #bfc9d1;
    }
    
    /* Live data indicator */
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #43e97b;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

def render_sidebar(df):
    """Render sidebar with filters, info, and API status"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/11/Flag_of_Sri_Lanka.svg" 
                 style="width: 100%; max-width: 200px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation selector
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #43e97b; margin: 0;">Navigation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Year filter
        available_years = sorted(df['year'].unique().tolist())
        selected_year = st.selectbox(
            "📅 Filter by Year",
            ["All Years"] + available_years,
            index=0
        )
        
        # Refresh button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("🌐 Live Data", use_container_width=True, disabled=not WEATHER_TOURISM_AVAILABLE):
                st.session_state.show_live_data = True
        
        st.divider()
        
        # API Status Section
        if API_CONFIG_AVAILABLE:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 12px;">
                <h4 style="color: #38f9d7; margin: 0;">📡 API Status</h4>
            </div>
            """, unsafe_allow_html=True)
            
            api_status = APIConfig.get_api_status()
            active_apis = sum(1 for status in api_status.values() if status)
            total_apis = len(api_status)
            
            # Progress bar for API availability
            progress_percentage = (active_apis / total_apis) * 100
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #bfc9d1; font-size: 0.85rem;">APIs Configured</span>
                    <span style="color: #43e97b; font-weight: 600;">{active_apis}/{total_apis}</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); width: {progress_percentage}%; height: 100%; transition: width 0.3s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Individual API status
            api_names = {
                'openweather': '🌤️ Weather',
                'rapidapi': '🏨 Hotels',
                'aviationstack': '✈️ Flights',
                'amadeus': '🌍 Travel'
            }
            
            for api_key, api_name in api_names.items():
                if api_key in api_status:
                    status_class = "api-active" if api_status[api_key] else "api-inactive"
                    status_icon = "✓" if api_status[api_key] else "○"
                    st.markdown(f"""
                    <div class="api-status-badge {status_class}">
                        {status_icon} {api_name}
                    </div>
                    """, unsafe_allow_html=True)
            
            if active_apis == 0:
                st.info("💡 Configure APIs in `.env` to unlock live tourism data!", icon="💡")
            elif active_apis < total_apis:
                st.success(f"🎉 {active_apis} API{'s' if active_apis > 1 else ''} active!")
            
            st.divider()
        
        # Dataset info
        st.markdown(f"""
        <div class="info-box">
            <div style="font-weight: 600; color: #43e97b; margin-bottom: 12px; font-size: 1.1rem;">📊 Dataset Information</div>
            <div style="color: #bfc9d1; line-height: 1.8;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>Data Range:</span>
                    <span style="color: #f5f6fa; font-weight: 600;">{df['date'].min().strftime('%b %Y')} - {df['date'].max().strftime('%b %Y')}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>Total Records:</span>
                    <span style="color: #43e97b; font-weight: 600;">{len(df):,}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Countries:</span>
                    <span style="color: #38f9d7; font-weight: 600;">{df['country'].nunique()}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Real-time data widget (if APIs are available)
        if API_CONFIG_AVAILABLE and any(APIConfig.get_api_status().values()):
            render_realtime_widget()
        
        st.divider()
        
        st.markdown("""
        <div style="text-align: center; padding: 16px; color: #bfc9d1; font-size: 0.85rem;">
            <div style="margin-bottom: 8px;">💡 <strong>Pro Tip:</strong></div>
            <div>Hover over charts for detailed insights and interact with visualizations</div>
        </div>
        """, unsafe_allow_html=True)
    
    return selected_year

def render_realtime_widget():
    """Display real-time data widget in sidebar"""
    try:
        from backend.api_services import WeatherService, ExchangeRateService
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 12px;">
            <h4 style="color: #38f9d7; margin: 0;">
                <span class="live-indicator"></span>Live Data
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick weather for Colombo
        weather = WeatherService.get_current_weather('Colombo', 6.9271, 79.8612)
        if weather:
            st.metric(
                "🌡️ Colombo",
                f"{weather['temperature']:.0f}°C",
                delta=weather['description'].title()
            )
        
        # Quick exchange rate
        rates = ExchangeRateService.get_rates()
        if rates and 'LKR' in rates:
            st.metric(
                "💱 USD to LKR",
                f"{rates['LKR']:.0f}",
                delta=f"Updated: {rates.get('date', 'Today')}"
            )
    except Exception as e:
        pass  # Silently fail if APIs not available

def prepare_data(df, selected_year):
    """Filter and prepare data based on selections"""
    # Filter by year
    if selected_year != "All Years":
        filtered_df = df[df['year'] == selected_year]
    else:
        filtered_df = df
    
    # Fetch API data
    overview = fetch_data('overview')
    monthly_trends = fetch_data(f'monthly-trends{"?year=" + str(selected_year) if selected_year != "All Years" else ""}')
    top_countries = fetch_data(f'top-countries{"?year=" + str(selected_year) if selected_year != "All Years" else ""}')
    forecast = fetch_data('forecast')
    year_comparison = fetch_data('year-comparison')
    regional_data = fetch_data('regional-analysis')
    
    # Fallback to local data if API fails
    if not overview:
        st.toast("⚠️ API not available. Using local data.", icon="⚠️")
        overview = {
            'total_arrivals': int(filtered_df['arrivals'].sum()),
            'avg_monthly_arrivals': int(filtered_df.groupby('date')['arrivals'].sum().mean()),
            'recent_6_months': int(filtered_df[filtered_df['date'] >= (filtered_df['date'].max() - pd.DateOffset(months=6))]['arrivals'].sum())
        }
    
    if not monthly_trends:
        monthly_trends = filtered_df.groupby('date')['arrivals'].sum().reset_index().to_dict('records')
    
    if not top_countries:
        top_countries = filtered_df.groupby('country')['arrivals'].sum().reset_index().sort_values('arrivals', ascending=False).to_dict('records')
    
    if not year_comparison:
        import numpy as np
        temp_df = filtered_df.copy()
        if np.issubdtype(temp_df['month'].dtype, np.datetime64):
            temp_df['month'] = temp_df['month'].dt.month
        year_comparison = temp_df.groupby('year').agg({
            'arrivals': ['sum', lambda x: x.groupby(temp_df.loc[x.index, 'month']).sum().mean()]
        }).reset_index()
        year_comparison.columns = ['year', 'total_arrivals', 'avg_monthly']
        year_comparison = year_comparison.to_dict('records')
    
    if not regional_data:
        def get_region(country):
            for region, countries in config.COUNTRY_REGIONS.items():
                if country in countries:
                    return region
            return 'Other'
        filtered_df['region'] = filtered_df['country'].apply(get_region)
        regional_data = filtered_df.groupby('region')['arrivals'].sum().reset_index().to_dict('records')
    
    return {
        'filtered_df': filtered_df,
        'overview': overview,
        'monthly_trends': monthly_trends,
        'top_countries': top_countries,
        'forecast': forecast,
        'year_comparison': year_comparison,
        'regional_data': regional_data
    }

def main():
    # Initialize session state
    if 'show_live_data' not in st.session_state:
        st.session_state.show_live_data = False
    
    # Header with live data indicator
    live_indicator = ""
    if API_CONFIG_AVAILABLE and any(APIConfig.get_api_status().values()):
        live_indicator = '<span class="live-indicator"></span>'
    
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>{live_indicator}🇱🇰 Sri Lanka Tourism Intelligence Platform</h1>
        <p class="subtitle">Advanced Analytics & AI-Powered Forecasting Dashboard with Real-Time Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_local_data()
    
    if df is None:
        st.error("⚠️ Data not available. Please run the backend first.")
        return
    
    # Render sidebar and get selections
    selected_year = render_sidebar(df)
    
    # Prepare data
    data = prepare_data(df, selected_year)
    
    # Create tabs - add Weather & Tourism tab if available
    if WEATHER_TOURISM_AVAILABLE:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard Overview", 
            "📈 Trend Analysis", 
            "🌏 Country Insights", 
            "🔮 AI Forecast",
            "🌤️ Weather & Tourism 🆕"
        ])
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard Overview", 
            "📈 Trend Analysis", 
            "🌏 Country Insights", 
            "🔮 AI Forecast"
        ])
    
    with tab1:
        overview_page.render(data)
    
    with tab2:
        trends_page.render(data)
    
    with tab3:
        country_insight.render(data)
    
    with tab4:
        ai_forecast.render(data)
    
    # New Weather & Tourism tab
    if WEATHER_TOURISM_AVAILABLE:
        with tab5:
            weather_tourism.main()
            
            # Show setup instructions if no APIs configured
            if API_CONFIG_AVAILABLE:
                api_status = APIConfig.get_api_status()
                if not any(api_status.values()):
                    st.info("💡 **Get Started with Live Data!**")
                    with st.expander("📖 Quick Setup Guide", expanded=True):
                        st.markdown("""
                        ### Enable Real-Time Tourism Data in 3 Steps:
                        
                        1. **Get a Free API Key** (Choose one to start):
                           - 🌤️ [OpenWeatherMap](https://openweathermap.org/api) - Weather data (FREE, 1000 calls/day)
                           - 💱 Exchange Rates API - Already enabled, no key needed!
                           - ⚠️ Travel Advisory API - Already enabled, no key needed!
                        
                        2. **Create `.env` file** in your project root:
                        ```
                        OPENWEATHER_API_KEY=your_key_here
                        ```
                        
                        3. **Restart the app** to see live data!
                        
                        ---
                        
                        **Want More Features?** Get these optional APIs:
                        - 🏨 Hotels: [RapidAPI](https://rapidapi.com/) (Booking.com API)
                        - ✈️ Flights: [AviationStack](https://aviationstack.com/) (100 calls/month free)
                        
                        All APIs have generous free tiers - perfect for your dashboard! 🚀
                        """)
    
    # Footer
    st.markdown("""
    <div class="dashboard-footer">
        <div style="font-size: 1.2rem; font-weight: 600; color: #43e97b; margin-bottom: 8px;">
            🇱🇰 Sri Lanka Tourism Intelligence Platform
        </div>
        <div style="color: #bfc9d1; margin-bottom: 12px;">
            Powered by Advanced Machine Learning & Real-Time Tourism APIs
        </div>
        <div style="display: flex; justify-content: center; gap: 24px; font-size: 0.9rem; color: #bfc9d1; flex-wrap: wrap;">
            <span>🤖 XGBoost + LSTM Ensemble</span>
            <span>•</span>
            <span>📊 Real-time Analytics</span>
            <span>•</span>
            <span>🔮 Predictive Insights</span>
            <span>•</span>
            <span>🌐 Live API Integration</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()