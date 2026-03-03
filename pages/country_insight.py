import streamlit as st
import pandas as pd
import plotly.express as px
from utils.styles import apply_plotly_theme

def render(data):
    """Render the country insights page"""
    # Ensure Plotly theme is applied
    apply_plotly_theme()

    top_countries = data.get('top_countries', [])
    regional_data = data.get('regional_data', [])

    st.markdown(
        '<div class="section-header"><h2>🌏 Country Insights</h2></div>', 
        unsafe_allow_html=True
    )

    # =======================
    # TOP COUNTRIES
    # =======================
    df = pd.DataFrame(top_countries)
    if not df.empty:
        st.markdown(
            '<div class="section-header"><h3>🏆 Top Source Countries</h3></div>', 
            unsafe_allow_html=True
        )

        fig = px.bar(
            df.head(15),
            x='country',
            y='arrivals',
            color='arrivals',
            color_continuous_scale='Tealgrn',
            height=400
        )
        fig.update_layout(
            template='professional_dark',
            xaxis_title='Country',
            yaxis_title='Arrivals',
            font=dict(color='#e0e6ed'),
            margin=dict(t=30, b=30, l=20, r=20)
        )

        st.plotly_chart(fig, use_container_width=True, key="countries_top_bar")

        # Display top countries table
        st.dataframe(df.head(20), use_container_width=True)

    # =======================
    # REGION BREAKDOWN
    # =======================
    st.markdown(
        '<div class="section-header"><h3>🌎 Arrivals by Region</h3></div>',
        unsafe_allow_html=True
    )

    if regional_data:
        region_df = pd.DataFrame(regional_data)

        fig_pie = px.pie(
            region_df,
            names='region',
            values='arrivals',
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_pie.update_traces(textinfo='percent+label', pull=[0.03]*len(region_df))
        fig_pie.update_layout(
            template='professional_dark',
            height=350,
            showlegend=True,
            margin=dict(t=30, b=20, l=20, r=20)
        )

        st.plotly_chart(fig_pie, use_container_width=True, key="countries_region_pie")

        # Display regional table
        st.dataframe(region_df, use_container_width=True)
