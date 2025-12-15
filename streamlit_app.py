import streamlit as st
import pandas as pd
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
import config

# Import page modules
from pages import overview_page, trends_page, country_insight, ai_forecast

# Import shared utilities
from utils.data_loader import fetch_data, load_local_data
from utils.styles import apply_custom_styles

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
</style>
""", unsafe_allow_html=True)

def render_sidebar(df):
    """Render sidebar with filters and info"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/11/Flag_of_Sri_Lanka.svg" 
                 style="width: 100%; max-width: 200px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
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
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
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
        
        st.markdown("""
        <div style="text-align: center; padding: 16px; color: #bfc9d1; font-size: 0.85rem;">
            <div style="margin-bottom: 8px;">💡 <strong>Pro Tip:</strong></div>
            <div>Hover over charts for detailed insights and interact with visualizations</div>
        </div>
        """, unsafe_allow_html=True)
    
    return selected_year

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
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🇱🇰 Sri Lanka Tourism Intelligence Platform</h1>
        <p class="subtitle">Advanced Analytics & AI-Powered Forecasting Dashboard</p>
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
    
    # Create tabs
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
    
    # Footer
    st.markdown("""
    <div class="dashboard-footer">
        <div style="font-size: 1.2rem; font-weight: 600; color: #43e97b; margin-bottom: 8px;">
            🇱🇰 Sri Lanka Tourism Intelligence Platform
        </div>
        <div style="color: #bfc9d1; margin-bottom: 12px;">
            Powered by Advanced Machine Learning & Data Analytics
        </div>
        <div style="display: flex; justify-content: center; gap: 24px; font-size: 0.9rem; color: #bfc9d1;">
            <span>🤖 XGBoost + LSTM Ensemble</span>
            <span>•</span>
            <span>📊 Real-time Analytics</span>
            <span>•</span>
            <span>🔮 Predictive Insights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()