import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import format_number
from utils.styles import create_metric_card

def render(data):
    """Render the AI forecast page"""
    forecast = data.get('forecast', [])
    monthly_trends = data.get('monthly_trends', [])
    filtered_df = data.get('filtered_df', [])
    
    st.markdown('<div class="section-header"><h2>🔮 AI-Powered Tourism Forecasting</h2></div>', unsafe_allow_html=True)
    
    # Info Box
    st.markdown("""
    <div class="info-box">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="font-size: 3rem;">🤖</div>
            <div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #43e97b; margin-bottom: 8px;">Advanced Machine Learning Forecast</div>
                <div style="color: #bfc9d1; line-height: 1.6;">
                    Our ensemble model combines <strong>XGBoost</strong> (Extreme Gradient Boosting with advanced feature engineering) 
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
        
        # Ensure all required forecast columns exist
        for col in ['ensemble_forecast', 'xgboost_forecast', 'lstm_forecast']:
            if col not in forecast_df.columns:
                forecast_df[col] = np.nan
        
        # Calculate Statistics (use ensemble forecast)
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
            
            # XGBoost forecast (only if column exists)
            if 'xgboost_forecast' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['xgboost_forecast'],
                    mode='lines',
                    name='XGBoost Model',
                    line=dict(color='#667eea', width=2, dash='dot'),
                    opacity=0.5,
                    hovertemplate='<b>%{x|%B %Y}</b><br>XGBoost: %{y:,.0f}<extra></extra>'
                ))
            
            # LSTM forecast (only if column exists)
            if 'lstm_forecast' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['lstm_forecast'],
                    mode='lines',
                    name='LSTM Model',
                    line=dict(color='#fa709a', width=2, dash='dot'),
                    opacity=0.5,
                    hovertemplate='<b>%{x|%B %Y}</b><br>LSTM: %{y:,.0f}<extra></extra>'
                ))
            
            # Vertical line separator
            last_date = recent_historical['date'].iloc[-1]
            if not isinstance(last_date, datetime):
                last_date = pd.Timestamp(last_date).to_pydatetime()
            
            fig.update_layout(
                shapes=[dict(
                    type="line",
                    xref="x",
                    yref="paper",
                    x0=last_date,
                    y0=0,
                    x1=last_date,
                    y1=1,
                    line=dict(color="rgba(67, 233, 123, 0.3)", width=2, dash="dash")
                )],
                annotations=[dict(
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
                )],
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
            fig_compare = go.Figure()
            if 'xgboost_forecast' in forecast_df.columns:
                fig_compare.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['xgboost_forecast'],
                    name='XGBoost',
                    mode='lines+markers',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x|%B %Y}</b><br>XGBoost: %{y:,.0f}<extra></extra>'
                ))
            if 'lstm_forecast' in forecast_df.columns:
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
            if 'xgboost_forecast' in forecast_df.columns and 'lstm_forecast' in forecast_df.columns:
                forecast_df['difference'] = abs(forecast_df['xgboost_forecast'] - forecast_df['lstm_forecast'])
            else:
                forecast_df['difference'] = np.nan
            
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
        
        # Safe formatting
        safe_int_format = lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A"
        for col in ['xgboost_forecast', 'lstm_forecast', 'ensemble_forecast']:
            display_df[col] = display_df[col].apply(safe_int_format)
        
        display_df = display_df[['date', 'xgboost_forecast', 'lstm_forecast', 'ensemble_forecast']]
        display_df.columns = ['Month', 'XGBoost Model', 'LSTM Model', 'Ensemble Forecast']
        st.dataframe(display_df, use_container_width=True, height=450)
        
        # Download Section
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Forecast Data",
                data=csv,
                file_name=f"tourism_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
