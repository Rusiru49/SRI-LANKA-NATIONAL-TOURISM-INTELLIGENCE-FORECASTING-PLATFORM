import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
import config

# Page configuration
st.set_page_config(
    page_title="🇱🇰 Sri Lanka Tourism Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #667eea;
    }
    .st-emotion-cache-16idsys p {
        font-size: 18px;
    }
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2, h3 {
        color: #333;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.3);
        border-radius: 10px;
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# API Base URL
API_BASE = 'http://localhost:5000/api'

# Cache data fetching
@st.cache_data(ttl=300)
def fetch_data(endpoint):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

@st.cache_data(ttl=300)
def load_local_data():
    """Load data directly from file"""
    try:
        df = pd.read_csv(config.PROCESSED_DATA_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return None

def format_number(num):
    """Format numbers with commas"""
    return f"{int(num):,}"

def create_overview_page(overview, year_comparison, regional_data, df):
    """Overview/Dashboard page"""
    st.header("📊 Tourism Overview Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Arrivals", 
            format_number(overview.get('total_arrivals', 0)),
            delta="All Time"
        )
    
    with col2:
        st.metric(
            "Avg Monthly", 
            format_number(overview.get('avg_monthly_arrivals', 0)),
            delta="Per Month"
        )
    
    with col3:
        st.metric(
            "Last 6 Months", 
            format_number(overview.get('recent_6_months', 0)),
            delta="Recent"
        )
    
    with col4:
        st.metric(
            "Source Countries", 
            len(overview.get('top_countries', {})),
            delta="Total"
        )
    
    st.divider()
    
    # Year over Year Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Year-over-Year Comparison")
        if year_comparison:
            yoy_df = pd.DataFrame(year_comparison)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=yoy_df['year'],
                y=yoy_df['total_arrivals'],
                name='Total Arrivals',
                marker_color='#667eea'
            ))
            fig.add_trace(go.Bar(
                x=yoy_df['year'],
                y=yoy_df['avg_monthly'],
                name='Avg Monthly',
                marker_color='#764ba2'
            ))
            fig.update_layout(
                barmode='group',
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Regional Distribution")
        if regional_data:
            regional_df = pd.DataFrame(regional_data)
            fig = px.pie(
                regional_df,
                values='arrivals',
                names='region',
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Top Countries
    st.subheader("🏆 Top 10 Source Countries")
    if overview and 'top_countries' in overview:
        top_countries = overview['top_countries']
        top_10 = dict(sorted(top_countries.items(), key=lambda x: x[1], reverse=True)[:10])
        
        cols = st.columns(5)
        for idx, (country, arrivals) in enumerate(top_10.items()):
            with cols[idx % 5]:
                st.metric(country, format_number(arrivals))

def create_trends_page(monthly_trends, year_comparison, df):
    """Trends analysis page"""
    st.header("📈 Trend Analysis")
    
    if monthly_trends:
        trends_df = pd.DataFrame(monthly_trends)
        trends_df['date'] = pd.to_datetime(trends_df['date'])
        
        # Calculate statistics
        total_arrivals = trends_df['arrivals'].sum()
        avg_monthly = trends_df['arrivals'].mean()
        max_month = trends_df.loc[trends_df['arrivals'].idxmax()]
        min_month = trends_df.loc[trends_df['arrivals'].idxmin()]
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Monthly", format_number(avg_monthly))
        with col2:
            st.metric("Highest Month", format_number(max_month['arrivals']))
        with col3:
            st.metric("Lowest Month", format_number(min_month['arrivals']))
        with col4:
            st.metric("Total Period", format_number(total_arrivals))
        
        st.divider()
        
        # Monthly Trends Chart
        st.subheader("📊 Monthly Arrival Trends")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trends_df['date'],
            y=trends_df['arrivals'],
            mode='lines+markers',
            name='Tourist Arrivals',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        fig.update_layout(
            height=500,
            template='plotly_white',
            hovermode='x unified',
            xaxis_title='Date',
            yaxis_title='Arrivals'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Growth Trajectory
        st.subheader("📉 Growth Trajectory by Year")
        if year_comparison:
            yoy_df = pd.DataFrame(year_comparison)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=yoy_df['year'],
                y=yoy_df['total_arrivals'],
                mode='lines+markers',
                name='Annual Total',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10)
            ))
            fig.add_trace(go.Scatter(
                x=yoy_df['year'],
                y=yoy_df['avg_monthly'],
                mode='lines+markers',
                name='Monthly Average',
                line=dict(color='#764ba2', width=3),
                marker=dict(size=10)
            ))
            fig.update_layout(
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Seasonal Patterns
        st.divider()
        st.subheader("🌤️ Seasonal Patterns")
        monthly_avg = df.groupby('month')['arrivals'].mean().reset_index()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_avg['month_name'] = monthly_avg['month'].apply(lambda x: month_names[x-1])
        
        fig = px.bar(
            monthly_avg,
            x='month_name',
            y='arrivals',
            color='arrivals',
            color_continuous_scale='RdBu',
            labels={'arrivals': 'Average Arrivals', 'month_name': 'Month'}
        )
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

def create_countries_page(top_countries, regional_data, df):
    """Country analysis page"""
    st.header("🌏 Country Analysis")
    
    if top_countries:
        countries_df = pd.DataFrame(top_countries)
        
        # Top 10 Horizontal Bar Chart
        st.subheader("🏆 Top 10 Source Countries")
        top_10 = countries_df.head(10)
        fig = px.bar(
            top_10,
            x='arrivals',
            y='country',
            orientation='h',
            color='arrivals',
            color_continuous_scale='Blues',
            labels={'arrivals': 'Tourist Arrivals', 'country': 'Country'}
        )
        fig.update_layout(height=500, template='plotly_white', yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Regional Breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Regional Breakdown")
            if regional_data:
                regional_df = pd.DataFrame(regional_data)
                fig = px.pie(
                    regional_df,
                    values='arrivals',
                    names='region',
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Regional Bar Chart")
            if regional_data:
                regional_df = pd.DataFrame(regional_data).sort_values('arrivals', ascending=True)
                fig = px.bar(
                    regional_df,
                    x='arrivals',
                    y='region',
                    orientation='h',
                    color='arrivals',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Country Rankings Grid
        st.subheader("📋 Country Rankings")
        cols = st.columns(3)
        for idx, row in countries_df.head(15).iterrows():
            with cols[idx % 3]:
                st.metric(
                    f"#{idx + 1} {row['country']}", 
                    format_number(row['arrivals'])
                )
        
        st.divider()
        
        # Detailed Table
        st.subheader("📄 Detailed Country Data")
        st.dataframe(
            countries_df.style.format({'arrivals': '{:,.0f}'}),
            use_container_width=True,
            height=400
        )

def create_forecast_page(forecast, monthly_trends, df):
    """Forecast page"""
    st.header("🔮 Tourism Forecasting")
    
    # Info Box
    st.info("""
    📊 **Forecast Information**
    
    The forecast uses an ensemble of Prophet (time series) and LSTM (deep learning) models 
    to predict tourist arrivals for the next 12 months. The ensemble combines both predictions 
    for improved accuracy.
    """)
    
    if forecast:
        forecast_df = pd.DataFrame(forecast)
        forecast_df['date'] = pd.to_datetime(forecast_df['date'])
        
        # Calculate statistics
        total_forecast = forecast_df['ensemble_forecast'].sum()
        avg_monthly = forecast_df['ensemble_forecast'].mean()
        max_forecast = forecast_df['ensemble_forecast'].max()
        min_forecast = forecast_df['ensemble_forecast'].min()
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("12-Month Projection", format_number(total_forecast))
        with col2:
            st.metric("Avg Monthly Forecast", format_number(avg_monthly))
        with col3:
            st.metric("Peak Month", format_number(max_forecast))
        with col4:
            st.metric("Low Month", format_number(min_forecast))
        
        st.divider()
        
        # Historical vs Forecast Chart
        st.subheader("📈 Historical vs Forecast")
        
        # Prepare historical data
        if monthly_trends:
            historical_df = pd.DataFrame(monthly_trends)
            historical_df['date'] = pd.to_datetime(historical_df['date'])
            recent_historical = historical_df.tail(12)
            
            # Create combined chart
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=recent_historical['date'],
                y=recent_historical['arrivals'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#333', width=3),
                marker=dict(size=8)
            ))
            
            # Ensemble forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['ensemble_forecast'],
                mode='lines+markers',
                name='Ensemble Forecast',
                line=dict(color='#667eea', width=3, dash='dash'),
                marker=dict(size=8)
            ))
            
            # Prophet forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['prophet_forecast'],
                mode='lines',
                name='Prophet Model',
                line=dict(color='#43e97b', width=2, dash='dot'),
                opacity=0.6
            ))
            
            # LSTM forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['lstm_forecast'],
                mode='lines',
                name='LSTM Model',
                line=dict(color='#fa709a', width=2, dash='dot'),
                opacity=0.6
            ))
            
            fig.update_layout(
                height=500,
                template='plotly_white',
                hovermode='x unified',
                xaxis_title='Date',
                yaxis_title='Arrivals'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Model Comparison
        st.subheader("🤖 Model Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            # Prophet vs LSTM
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['prophet_forecast'],
                name='Prophet',
                line=dict(color='#43e97b', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['lstm_forecast'],
                name='LSTM',
                line=dict(color='#fa709a', width=3)
            ))
            fig.update_layout(
                height=400,
                template='plotly_white',
                title='Prophet vs LSTM Predictions'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Difference Analysis
            forecast_df['difference'] = abs(forecast_df['prophet_forecast'] - forecast_df['lstm_forecast'])
            fig = px.bar(
                forecast_df,
                x='date',
                y='difference',
                color='difference',
                color_continuous_scale='Reds',
                labels={'difference': 'Model Difference'}
            )
            fig.update_layout(
                height=400,
                template='plotly_white',
                title='Prediction Difference Between Models'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Detailed Forecast Table
        st.subheader("📋 Detailed Forecast Table")
        display_df = forecast_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%B %Y')
        display_df['prophet_forecast'] = display_df['prophet_forecast'].apply(lambda x: f"{int(x):,}")
        display_df['lstm_forecast'] = display_df['lstm_forecast'].apply(lambda x: f"{int(x):,}")
        display_df['ensemble_forecast'] = display_df['ensemble_forecast'].apply(lambda x: f"{int(x):,}")
        
        st.dataframe(
            display_df[['date', 'prophet_forecast', 'lstm_forecast', 'ensemble_forecast']],
            use_container_width=True,
            height=400
        )

def main():
    # Header
    st.title("🇱🇰 Sri Lanka National Tourism Intelligence & Forecasting Platform")
    st.markdown("### *National Tourism Analytics & Forecasting Dashboard*")
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/11/Flag_of_Sri_Lanka.svg", width=200)
        st.header("⚙️ Controls")
        
        # Load data
        df = load_local_data()
        
        if df is not None:
            # Year filter
            available_years = sorted(df['year'].unique().tolist())
            selected_year = st.selectbox(
                "Filter by Year",
                ["All Years"] + available_years,
                index=0
            )
            
            # Refresh button
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
            
            st.divider()
            
            # Info
            st.info(f"""
            **Data Range:**
            {df['date'].min().strftime('%B %Y')} to {df['date'].max().strftime('%B %Y')}
            
            **Total Records:** {len(df):,}
            
            **Countries:** {df['country'].nunique()}
            """)
        else:
            st.error("⚠️ Data not available. Please run the backend first.")
            return
    
    # Filter data by year
    if selected_year != "All Years":
        filtered_df = df[df['year'] == selected_year]
    else:
        filtered_df = df
    
    # Fetch API data
    overview = fetch_data('overview')
    monthly_trends_data = fetch_data(f'monthly-trends{"?year=" + str(selected_year) if selected_year != "All Years" else ""}')
    top_countries_data = fetch_data(f'top-countries{"?year=" + str(selected_year) if selected_year != "All Years" else ""}')
    forecast_data = fetch_data('forecast')
    year_comparison = fetch_data('year-comparison')
    regional_data = fetch_data('regional-analysis')
    
    # Fallback to local data if API fails
    if not overview:
        st.warning("⚠️ API not available. Using local data.")
        overview = {
            'total_arrivals': int(filtered_df['arrivals'].sum()),
            'avg_monthly_arrivals': int(filtered_df.groupby('date')['arrivals'].sum().mean()),
            'recent_6_months': int(filtered_df[filtered_df['date'] >= filtered_df['date'].max() - pd.DateOffset(months=6)]['arrivals'].sum()),
            'top_countries': filtered_df.groupby('country')['arrivals'].sum().to_dict()
        }
    
    if not monthly_trends_data:
        monthly_trends_data = filtered_df.groupby('date')['arrivals'].sum().reset_index().to_dict('records')
    
    if not top_countries_data:
        top_countries_data = filtered_df.groupby('country')['arrivals'].sum().reset_index().sort_values('arrivals', ascending=False).to_dict('records')
    
    if not year_comparison:
        year_comparison = filtered_df.groupby('year').agg({
            'arrivals': ['sum', lambda x: x.groupby(filtered_df.loc[x.index, 'month']).sum().mean()]
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
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🌏 Countries", "🔮 Forecast"])
    
    with tab1:
        create_overview_page(overview, year_comparison, regional_data, filtered_df)
    
    with tab2:
        create_trends_page(monthly_trends_data, year_comparison, filtered_df)
    
    with tab3:
        create_countries_page(top_countries_data, regional_data, filtered_df)
    
    with tab4:
        create_forecast_page(forecast_data, monthly_trends_data, filtered_df)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: white; padding: 20px;'>
        <p>🇱🇰 Sri Lanka Tourism Intelligence Platform | Powered by ML & AI</p>
        <p style='font-size: 12px;'>Prophet + LSTM Ensemble Forecasting</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()