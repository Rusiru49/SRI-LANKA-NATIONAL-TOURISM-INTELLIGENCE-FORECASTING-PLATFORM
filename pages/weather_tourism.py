"""
New Streamlit Page: Weather & Tourism Information
Place this in: pages/weather_tourism.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from backend.api_services import (
    WeatherService, HotelService, FlightService, 
    ExchangeRateService, TravelAdvisoryService,
    TourismDataAggregator
)
from backend.api_config import APIConfig

st.set_page_config(page_title="Weather & Tourism Info", page_icon="🌤️", layout="wide")

def main():
    st.title("🌤️ Real-Time Weather & Tourism Information")
    st.markdown("Live data from external APIs for Sri Lanka tourism")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        selected_city = st.selectbox(
            "Select City",
            [city['name'] for city in APIConfig.SRI_LANKA_CITIES]
        )
        
        st.divider()
        
        # Hotel search parameters
        st.subheader("Hotel Search")
        checkin = st.date_input("Check-in", datetime.now() + timedelta(days=7))
        checkout = st.date_input("Check-out", datetime.now() + timedelta(days=10))
        adults = st.number_input("Adults", min_value=1, max_value=10, value=2)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌡️ Weather", "🏨 Hotels", "✈️ Flights", "💱 Exchange Rates", "⚠️ Travel Advisory"
    ])
    
    # Tab 1: Weather Information
    with tab1:
        display_weather_info(selected_city)
    
    # Tab 2: Hotel Information
    with tab2:
        display_hotel_info(selected_city, checkin.strftime('%Y-%m-%d'), 
                          checkout.strftime('%Y-%m-%d'), adults)
    
    # Tab 3: Flight Information
    with tab3:
        display_flight_info()
    
    # Tab 4: Exchange Rates
    with tab4:
        display_exchange_rates()
    
    # Tab 5: Travel Advisory
    with tab5:
        display_travel_advisory()


def display_weather_info(city: str):
    """Display weather information for selected city"""
    st.header(f"Weather in {city}")
    
    city_info = next((c for c in APIConfig.SRI_LANKA_CITIES if c['name'] == city), None)
    if not city_info:
        st.error("City not found")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Current Weather")
        weather = WeatherService.get_current_weather(city, city_info['lat'], city_info['lon'])
        
        if weather:
            st.metric("Temperature", f"{weather['temperature']:.1f}°C")
            st.metric("Feels Like", f"{weather['feels_like']:.1f}°C")
            st.metric("Humidity", f"{weather['humidity']}%")
            st.metric("Wind Speed", f"{weather['wind_speed']} m/s")
            st.info(f"Conditions: {weather['description'].title()}")
        else:
            st.warning("Weather data unavailable")
    
    with col2:
        st.subheader("5-Day Forecast")
        forecast = WeatherService.get_forecast(city, city_info['lat'], city_info['lon'])
        
        if forecast:
            # Create forecast chart
            df_forecast = pd.DataFrame(forecast)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_forecast['datetime'],
                y=df_forecast['temperature'],
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#FF6B6B', width=3)
            ))
            
            fig.update_layout(
                title="Temperature Forecast",
                xaxis_title="Date & Time",
                yaxis_title="Temperature (°C)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show forecast table
            st.dataframe(
                df_forecast[['datetime', 'temperature', 'description', 'humidity', 'rain_probability']].head(10),
                use_container_width=True
            )
        else:
            st.warning("Forecast data unavailable")
    
    # All cities weather comparison
    st.divider()
    st.subheader("Weather Across Sri Lanka")
    
    all_weather = TourismDataAggregator.get_all_cities_weather()
    if all_weather:
        df_all = pd.DataFrame(all_weather)
        
        fig = px.bar(
            df_all,
            x='city',
            y='temperature',
            color='temperature',
            title="Temperature Comparison",
            labels={'temperature': 'Temperature (°C)', 'city': 'City'},
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)


def display_hotel_info(city: str, checkin: str, checkout: str, adults: int):
    """Display hotel information"""
    st.header(f"Hotels in {city}")
    
    with st.spinner("Searching hotels..."):
        hotels = HotelService.search_hotels(city, checkin, checkout, adults)
    
    if hotels:
        st.success(f"Found {len(hotels)} hotels")
        
        # Display hotels in cards
        for hotel in hotels:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(hotel['name'])
                    st.caption(hotel['address'])
                
                with col2:
                    st.metric("Rating", f"{hotel['rating']:.1f}/10")
                    st.caption(f"{hotel['review_count']} reviews")
                
                with col3:
                    st.metric("Price", f"${hotel['price']:.2f}")
                    st.caption("per stay")
                
                st.divider()
    else:
        st.info("Enable RapidAPI key to search hotels. See setup instructions below.")
        with st.expander("How to get RapidAPI key"):
            st.markdown("""
            1. Sign up at [RapidAPI](https://rapidapi.com/)
            2. Subscribe to [Booking.com API](https://rapidapi.com/apidojo/api/booking-com/)
            3. Copy your API key
            4. Add to `.env` file: `RAPIDAPI_KEY=your_key_here`
            """)


def display_flight_info():
    """Display flight arrivals to Colombo"""
    st.header("✈️ Arrivals to Colombo (CMB)")
    
    with st.spinner("Loading flight data..."):
        flights = FlightService.get_flight_arrivals()
    
    if flights:
        df_flights = pd.DataFrame(flights)
        
        st.dataframe(
            df_flights,
            use_container_width=True,
            column_config={
                "flight_number": "Flight",
                "airline": "Airline",
                "origin": "From",
                "origin_country": "Country",
                "scheduled": "Arrival Time",
                "status": st.column_config.TextColumn("Status", help="Flight status")
            }
        )
        
        # Flight statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Flights", len(flights))
        with col2:
            on_time = sum(1 for f in flights if f['status'] == 'scheduled')
            st.metric("On Time", on_time)
        with col3:
            unique_airlines = len(set(f['airline'] for f in flights))
            st.metric("Airlines", unique_airlines)
    else:
        st.info("Enable AviationStack API key to view flight data.")


def display_exchange_rates():
    """Display currency exchange rates"""
    st.header("💱 Currency Exchange Rates")
    
    rates = ExchangeRateService.get_rates()
    
    if rates:
        st.info(f"Base: {rates['base']} | Updated: {rates['date']}")
        
        # Create a nice display of rates
        currencies = {
            'LKR': '🇱🇰 Sri Lankan Rupee',
            'EUR': '🇪🇺 Euro',
            'GBP': '🇬🇧 British Pound',
            'INR': '🇮🇳 Indian Rupee',
            'AUD': '🇦🇺 Australian Dollar',
            'CNY': '🇨🇳 Chinese Yuan',
            'JPY': '🇯🇵 Japanese Yen'
        }
        
        cols = st.columns(2)
        for idx, (code, name) in enumerate(currencies.items()):
            with cols[idx % 2]:
                if code in rates:
                    st.metric(name, f"{rates[code]:.2f}")
        
        # Currency converter
        st.divider()
        st.subheader("Currency Converter")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            amount = st.number_input("Amount", min_value=0.0, value=100.0)
        with col2:
            from_curr = st.selectbox("From", list(currencies.keys()))
        with col3:
            to_curr = st.selectbox("To", list(currencies.keys()), index=1)
        
        if from_curr in rates and to_curr in rates:
            converted = amount * (rates[to_curr] / rates[from_curr])
            st.success(f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr}")
    else:
        st.error("Exchange rate data unavailable")


def display_travel_advisory():
    """Display travel advisory information"""
    st.header("⚠️ Travel Advisory for Sri Lanka")
    
    advisory = TravelAdvisoryService.get_advisory()
    
    if advisory:
        score = advisory['score']
        
        # Color code based on score
        if score <= 2.5:
            color = "green"
            emoji = "✅"
        elif score <= 3.5:
            color = "orange"
            emoji = "⚠️"
        else:
            color = "red"
            emoji = "🚨"
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.metric("Safety Score", f"{score}/5.0")
            st.markdown(f"Status: :{color}[{emoji} {advisory['message']}]")
        
        with col2:
            st.info(f"Last Updated: {advisory['updated']}")
            if advisory['sources']:
                with st.expander("Advisory Sources"):
                    for source in advisory['sources']:
                        st.write(f"- {source}")
        
        st.divider()
        
        st.subheader("General Travel Tips for Sri Lanka")
        st.markdown("""
        - **Best Time to Visit**: December to March (west coast), April to September (east coast)
        - **Visa**: ETA (Electronic Travel Authorization) required for most nationalities
        - **Currency**: Sri Lankan Rupee (LKR)
        - **Languages**: Sinhala, Tamil, English widely spoken in tourist areas
        - **Emergency Numbers**: Police 119, Ambulance 110
        """)
    else:
        st.warning("Travel advisory data unavailable")


if __name__ == "__main__":
    main()