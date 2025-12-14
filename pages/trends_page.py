import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render(data):
    '''Render the trends analysis page'''
    monthly_trends = data['monthly_trends']
    filtered_df = data['filtered_df']
    year_comparison = data['year_comparison']
    
    st.markdown('<div class="section-header"><h2>📈 Trend Analysis</h2></div>', unsafe_allow_html=True)
    
    df = pd.DataFrame(monthly_trends)
    if not df.empty:
        # Monthly trend chart
        st.markdown('<div class="section-header"><h3>📅 Monthly Arrivals Trend</h3></div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(df['date']),
            y=df['arrivals'],
            mode='lines+markers',
            name='Monthly Arrivals',
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
        st.plotly_chart(fig, use_container_width=True)
        
        # Seasonality
        if 'month' in filtered_df.columns:
            st.markdown('<div class="section-header"><h3>📆 Seasonality (Average by Month)</h3></div>', unsafe_allow_html=True)
            season_df = filtered_df.groupby('month')['arrivals'].mean().reset_index()
            fig2 = px.bar(season_df, x='month', y='arrivals', color='arrivals', color_continuous_scale='Tealgrn')
            fig2.update_layout(template='plotly_dark', height=350, xaxis_title='Month', yaxis_title='Avg Arrivals')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Yearly comparison
    st.markdown('<div class="section-header"><h3>📅 Yearly Comparison</h3></div>', unsafe_allow_html=True)
    if year_comparison:
        yc_df = pd.DataFrame(year_comparison)
        st.dataframe(yc_df, use_container_width=True)