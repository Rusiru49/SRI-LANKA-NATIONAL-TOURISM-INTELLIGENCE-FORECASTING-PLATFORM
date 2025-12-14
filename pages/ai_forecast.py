import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import format_number
from utils.styles import create_metric_card

def render(data):
    """Render the AI forecast page"""
    forecast = data['forecast']
    monthly_trends = data['monthly_trends']
    filtered_df = data['filtered_df']
    
    st.markdown('<div class="section-header"><h2>🔮 AI-Powered Tourism Forecasting</h2></div>', unsafe_allow_html=True)
    
    # Info Box
    st.markdown("""
    <div class="info-box">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 3rem;">🤖</div>
            <div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #43e97b; margin-bottom: 8px;">Advanced Machine Learning Forecast</div>
                <div style="color: #bfc9d1; line-height: 1.6;">
                    Our ensemble model combines <strong>Prophet</strong> (Facebook's time series forecasting) 
                    and <strong>LSTM</strong> (Long Short-Term Memory neural networks) to predict tourist arrivals 
                    for the next 12 months with high accuracy.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if forecast:
        forecast_df = pd.DataFrame(forecast)
        forecast_df['date'] = pd.to_datetime(forecast_df['date']).dt.to_pydatetime()
        
        # Calculate Statistics
        total_forecast = forecast_df['ensemble_forecast'].sum()
        avg_monthly = forecast_df['ensemble_forecast'].mean()
        max_forecast = forecast_df['ensemble_forecast'].max()
        min_forecast = forecast_df['ensemble_forecast'].min()
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "12-Month Projection",
                format_number(total_forecast),
                "🎯",
                "Total Expected"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Monthly Average",
                format_number(avg_monthly),
                "📊",
                "Expected Average"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Peak Forecast",
                format_number(max_forecast),
                "🔥",
                "Highest Expected"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Low Forecast",
                format_number(min_forecast),
                "📉",
                "Lowest Expected"
            ), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Historical vs Forecast Chart
        st.markdown('<div class="section-header"><h3>📈 Historical Trends vs AI Forecast</h3></div>', unsafe_allow_html=True)
        
        if monthly_trends:
            historical_df = pd.DataFrame(monthly_trends)
            historical_df['date'] = pd.to_datetime(historical_df['date']).dt.to_pydatetime()
            recent_historical = historical_df.tail(24)  # Last 2 years
            
            # Create Combined Chart
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=recent_historical['date'],
                y=recent_historical['arrivals'],
                mode='lines',
                name='Historical Data',
                line=dict(color='#bfc9d1', width=3),
                fill='tozeroy',
                fillcolor='rgba(191, 201, 209, 0.1)',
                hovertemplate='<b>%{x|%B %Y}</b><br>Actual: %{y:,.0f}<extra></extra>'
            ))
            
            # Ensemble forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['ensemble_forecast'],
                mode='lines',
                name='AI Ensemble Forecast',
                line=dict(color='#43e97b', width=4),
                fill='tozeroy',
                fillcolor='rgba(67, 233, 123, 0.15)',
                hovertemplate='<b>%{x|%B %Y}</b><br>Forecast: %{y:,.0f}<extra></extra>'
            ))
            
            # Prophet forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['prophet_forecast'],
                mode='lines',
                name='Prophet Model',
                line=dict(color='#667eea', width=2, dash='dot'),
                opacity=0.5,
                hovertemplate='<b>%{x|%B %Y}</b><br>Prophet: %{y:,.0f}<extra></extra>'
            ))
            
            # LSTM forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['lstm_forecast'],
                mode='lines',
                name='LSTM Model',
                line=dict(color='#fa709a', width=2, dash='dot'),
                opacity=0.5,
                hovertemplate='<b>%{x|%B %Y}</b><br>LSTM: %{y:,.0f}<extra></extra>'
            ))
            
            # Add vertical line separator
            last_date = recent_historical['date'].iloc[-1]
            if isinstance(last_date, (np.ndarray, pd.Series, list)):
                last_date = last_date.item()
            if not isinstance(last_date, datetime):
                last_date = pd.Timestamp(last_date).to_pydatetime()
            
            fig.update_layout(
                shapes=[
                    dict(
                        type="line",
                        xref="x",
                        yref="paper",
                        x0=last_date,
                        y0=0,
                        x1=last_date,
                        y1=1,
                        line=dict(color="rgba(67, 233, 123, 0.3)", width=2, dash="dash")
                    )
                ],
                annotations=[
                    dict(
                        x=last_date,
                        y=1.05,
                        xref="x",
                        yref="paper",
                        text="Forecast Start",
                        showarrow=False,
                        font=dict(color="#43e97b", size=13),
                        bgcolor="rgba(35,42,52,0.8)",
                        bordercolor="#43e97b",
                        borderwidth=1,
                        borderpad=4
                    )
                ],
                height=550,
                template='plotly_dark',
                hovermode='x unified',
                xaxis_title='',
                yaxis_title='Number of Arrivals',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e6ed', size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(35, 42, 52, 0.8)',
                    bordercolor='rgba(67, 233, 123, 0.3)',
                    borderwidth=1
                ),
                margin=dict(t=60, b=20, l=20, r=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(67, 233, 123, 0.1)')
            )
            st.plotly_chart(fig, use_container_width=True, key="forecast_main_chart")
        
        st.divider()
        
        # Model Comparison
        st.markdown('<div class="section-header"><h3>🤖 Model Performance Comparison</h3></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            # Prophet vs LSTM
            fig_compare = go.Figure()
            fig_compare.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['prophet_forecast'],
                name='Prophet',
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x|%B %Y}</b><br>Prophet: %{y:,.0f}<extra></extra>'
            ))
            fig_compare.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['lstm_forecast'],
                name='LSTM',
                mode='lines+markers',
                line=dict(color='#fa709a', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x|%B %Y}</b><br>LSTM: %{y:,.0f}<extra></extra>'
            ))
            fig_compare.update_layout(
                height=400,
                template='plotly_dark',
                title='Individual Model Predictions',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e6ed', size=11),
                legend=dict(bgcolor='rgba(35, 42, 52, 0.8)'),
                margin=dict(t=40, b=20, l=20, r=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(67, 233, 123, 0.1)')
            )
            st.plotly_chart(fig_compare, use_container_width=True, key="forecast_model_comparison")
        
        with col2:
            # Difference Analysis
            forecast_df['difference'] = abs(forecast_df['prophet_forecast'] - forecast_df['lstm_forecast'])
            fig_diff = go.Figure()
            fig_diff.add_trace(go.Bar(
                x=forecast_df['date'],
                y=forecast_df['difference'],
                marker=dict(
                    color=forecast_df['difference'],
                    colorscale=[[0, '#43e97b'], [0.5, '#fee140'], [1, '#fa709a']],
                    line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
                ),
                hovertemplate='<b>%{x|%B %Y}</b><br>Difference: %{y:,.0f}<extra></extra>'
            ))
            fig_diff.update_layout(
                height=400,
                template='plotly_dark',
                title='Model Prediction Variance',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e6ed', size=11),
                showlegend=False,
                margin=dict(t=40, b=20, l=20, r=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(67, 233, 123, 0.1)')
            )
            st.plotly_chart(fig_diff, use_container_width=True, key="forecast_variance")
        
        st.divider()
        
        # Detailed Forecast Table
        st.markdown('<div class="section-header"><h3>📋 Detailed Monthly Forecast</h3></div>', unsafe_allow_html=True)
        display_df = forecast_df.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%B %Y')
        safe_int_format = lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A"
        display_df['prophet_forecast'] = display_df['prophet_forecast'].apply(safe_int_format)
        display_df['lstm_forecast'] = display_df['lstm_forecast'].apply(safe_int_format)
        display_df['ensemble_forecast'] = display_df['ensemble_forecast'].apply(safe_int_format)
        display_df = display_df[['date', 'prophet_forecast', 'lstm_forecast', 'ensemble_forecast']]
        display_df.columns = ['Month', 'Prophet Model', 'LSTM Model', 'Ensemble Forecast']
        st.dataframe(display_df, use_container_width=True, height=450)