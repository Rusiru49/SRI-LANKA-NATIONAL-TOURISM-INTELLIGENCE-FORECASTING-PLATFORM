import streamlit as st
import pandas as pd
import plotly.express as px

def render(data):
    """Render the country insights page"""
    top_countries = data['top_countries']
    regional_data = data['regional_data']
    
    st.markdown('<div class="section-header"><h2>🌏 Country Insights</h2></div>', unsafe_allow_html=True)
    
    # Top Countries Section
    df = pd.DataFrame(top_countries)
    if not df.empty:
        st.markdown('<div class="section-header"><h3>🏆 Top Source Countries</h3></div>', unsafe_allow_html=True)
        
        # Bar chart with unique key
        fig = px.bar(
            df.head(15), 
            x='country', 
            y='arrivals', 
            color='arrivals', 
            color_continuous_scale='Tealgrn', 
            height=400
        )
        fig.update_layout(
            template='plotly_dark', 
            xaxis_title='Country', 
            yaxis_title='Arrivals', 
            font=dict(color='#e0e6ed')
        )
        # ADD UNIQUE KEY HERE
        st.plotly_chart(fig, use_container_width=True, key="countries_top_bar")
        
        # Display data table
        st.dataframe(df.head(20), use_container_width=True)
    
    # Region Breakdown Section
    st.markdown('<div class="section-header"><h3>🌎 Arrivals by Region</h3></div>', unsafe_allow_html=True)
    if regional_data:
        region_df = pd.DataFrame(regional_data)
        
        # Pie chart with unique key
        fig_pie = px.pie(
            region_df, 
            names='region', 
            values='arrivals', 
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(template='plotly_dark', height=350, showlegend=True)
        
        # ADD UNIQUE KEY HERE
        st.plotly_chart(fig_pie, use_container_width=True, key="countries_region_pie")
        
        # Display regional data table
        st.dataframe(region_df, use_container_width=True)