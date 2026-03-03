import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# ===============================
# ENV & PATH SETUP
# ===============================
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
import config

# ===============================
# PAGE IMPORTS
# ===============================
from pages import overview_page, trends_page, country_insight, ai_forecast

try:
    from pages import weather_tourism
    WEATHER_TOURISM_AVAILABLE = True
except ImportError:
    WEATHER_TOURISM_AVAILABLE = False
    print("⚠️ weather_tourism.py not found. API features will be unavailable.")

# ===============================
# UTILITIES
# ===============================
from utils.data_loader import fetch_data, load_local_data
from utils.styles import apply_custom_styles, apply_plotly_theme

# ===============================
# API CONFIG
# ===============================
try:
    from backend.api_config import APIConfig
    API_CONFIG_AVAILABLE = True
except ImportError:
    API_CONFIG_AVAILABLE = False

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="🇱🇰 Sri Lanka Tourism Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# APPLY GLOBAL STYLES (IMPORTANT)
# ===============================
apply_custom_styles()
apply_plotly_theme()

# ===============================
# HIDE STREAMLIT DEFAULT NAV
# ===============================
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
def render_sidebar(df):
    """Render sidebar with filters, info, and API status"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/11/Flag_of_Sri_Lanka.svg"
                 style="width:100%; max-width:200px; border-radius:12px;">
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align:center;'>Navigation</h3>", unsafe_allow_html=True)

        available_years = sorted(df['year'].unique().tolist())
        selected_year = st.selectbox(
            "📅 Filter by Year",
            ["All Years"] + available_years,
            index=0
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        with col2:
            if st.button("🌐 Live Data", use_container_width=True, disabled=not WEATHER_TOURISM_AVAILABLE):
                st.session_state.show_live_data = True

        st.divider()

        if API_CONFIG_AVAILABLE:
            api_status = APIConfig.get_api_status()
            active_apis = sum(1 for v in api_status.values() if v)
            total_apis = len(api_status)

            st.markdown(f"""
            <div class="info-box">
                <strong>📡 API Status</strong><br>
                Active APIs: <b>{active_apis}/{total_apis}</b>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.markdown(f"""
        <div class="info-box">
            <strong>📊 Dataset Info</strong><br>
            Records: <b>{len(df):,}</b><br>
            Countries: <b>{df['country'].nunique()}</b><br>
            Period: <b>{df['date'].min().strftime('%b %Y')} – {df['date'].max().strftime('%b %Y')}</b>
        </div>
        """, unsafe_allow_html=True)

    return selected_year

# ===============================
# REALTIME WIDGET
# ===============================
def render_realtime_widget():
    try:
        from backend.api_services import WeatherService, ExchangeRateService

        weather = WeatherService.get_current_weather('Colombo', 6.9271, 79.8612)
        if weather:
            st.metric("🌡️ Colombo", f"{weather['temperature']:.0f}°C")

        rates = ExchangeRateService.get_rates()
        if rates and 'LKR' in rates:
            st.metric("💱 USD → LKR", f"{rates['LKR']:.0f}")

    except Exception:
        pass

# ===============================
# DATA PREPARATION
# ===============================
def prepare_data(df, selected_year):
    if selected_year != "All Years":
        filtered_df = df[df['year'] == selected_year]
    else:
        filtered_df = df

    overview = fetch_data('overview')
    monthly_trends = fetch_data('monthly-trends')
    top_countries = fetch_data('top-countries')
    forecast = fetch_data('forecast')
    year_comparison = fetch_data('year-comparison')
    regional_data = fetch_data('regional-analysis')

    if not overview:
        overview = {
            'total_arrivals': int(filtered_df['arrivals'].sum()),
            'avg_monthly_arrivals': int(filtered_df.groupby('date')['arrivals'].sum().mean()),
            'recent_6_months': int(
                filtered_df[
                    filtered_df['date'] >= filtered_df['date'].max() - pd.DateOffset(months=6)
                ]['arrivals'].sum()
            )
        }

    if not regional_data:
        def get_region(country):
            for region, countries in config.COUNTRY_REGIONS.items():
                if country in countries:
                    return region
            return "Other"

        filtered_df['region'] = filtered_df['country'].apply(get_region)
        regional_data = (
            filtered_df.groupby('region')['arrivals']
            .sum()
            .reset_index()
            .to_dict('records')
        )

    return {
        'filtered_df': filtered_df,
        'overview': overview,
        'monthly_trends': monthly_trends,
        'top_countries': top_countries,
        'forecast': forecast,
        'year_comparison': year_comparison,
        'regional_data': regional_data
    }

# ===============================
# MAIN APP
# ===============================
def main():
    if 'show_live_data' not in st.session_state:
        st.session_state.show_live_data = False

    st.markdown("""
    <div class="dashboard-header">
        <h1>🇱🇰 Sri Lanka Tourism Intelligence Platform</h1>
        <p class="subtitle">
            Advanced Analytics & AI-Powered Forecasting Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = load_local_data()
    if df is None:
        st.error("⚠️ Data not available.")
        return

    selected_year = render_sidebar(df)
    data = prepare_data(df, selected_year)

    if WEATHER_TOURISM_AVAILABLE:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "📈 Trends",
            "🌏 Country Insights",
            "🔮 AI Forecast",
            "🌤️ Weather & Tourism"
        ])
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview",
            "📈 Trends",
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

    if WEATHER_TOURISM_AVAILABLE:
        with tab5:
            weather_tourism.main()

    st.markdown("""
    <div class="dashboard-footer">
        🇱🇰 Sri Lanka Tourism Intelligence Platform<br>
        Powered by AI & Real-Time Data
    </div>
    """, unsafe_allow_html=True)

# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    main()
