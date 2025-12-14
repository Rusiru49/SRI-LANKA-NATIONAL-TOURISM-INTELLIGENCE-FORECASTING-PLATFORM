import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import format_number
from utils.styles import create_metric_card

def render(data):
    """Render the overview page"""
    overview = data['overview']
    filtered_df = data['filtered_df']
    year_comparison = data['year_comparison']
    regional_data = data['regional_data']
    
    st.markdown('<div class="section-header"><h2>📊 Dashboard Overview</h2></div>', unsafe_allow_html=True)
    
    # Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(create_metric_card(
            "Total Arrivals", 
            format_number(overview.get('total_arrivals', 0)), 
            "🌍"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card(
            "Avg Monthly Arrivals", 
            format_number(overview.get('avg_monthly_arrivals', 0)), 
            "📅"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card(
            "Arrivals (Last 6 Months)", 
            format_number(overview.get('recent_6_months', 0)), 
            "⏳"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Time Series Chart
    st.markdown('<div class="section-header"><h3>📈 Total Arrivals Over Time</h3></div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        ts_df = filtered_df.groupby('date')['arrivals'].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ts_df['date'],
            y=ts_df['arrivals'],
            mode='lines+markers',
            name='Total Arrivals',
            line=dict(color='#43e97b', width=3),
            marker=dict(size=8, color='#38f9d7'),
            fill='tozeroy',
            fillcolor='rgba(67, 233, 123, 0.1)'
        ))
        fig.update_layout(
            height=400,
            template='plotly_dark',
            xaxis_title='Date',
            yaxis_title='Arrivals',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e6ed', size=12),
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True, key="overview_timeseries")
    
    # Region Breakdown
    st.markdown('<div class="section-header"><h3>🌎 Arrivals by Region</h3></div>', unsafe_allow_html=True)
    if regional_data:
        region_df = pd.DataFrame(regional_data)
        fig_pie = px.pie(
            region_df, 
            names='region', 
            values='arrivals', 
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(template='plotly_dark', height=350, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True, key="overview_region_pie")
        st.dataframe(region_df, use_container_width=True)
    
    # Yearly Comparison
    st.markdown('<div class="section-header"><h3>📅 Yearly Comparison</h3></div>', unsafe_allow_html=True)
    if year_comparison:
        yc_df = pd.DataFrame(year_comparison)
        st.dataframe(yc_df, use_container_width=True)