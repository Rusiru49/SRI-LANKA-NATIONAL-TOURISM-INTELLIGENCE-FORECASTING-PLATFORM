"""
New Streamlit Page: Weather & Tourism Information
Place this in: pages/weather_tourism.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from backend.api_services import (
    WeatherService,
    FlightService,
    ExchangeRateService,
    TourismDataAggregator
)
from backend.api_config import APIConfig

st.set_page_config(
    page_title="Weather & Tourism Info",
    page_icon="🌤️",
    layout="wide"
)

def main():
    st.title("🌤️ Real-Time Weather & Tourism Information")
    st.markdown("Live data from external APIs for Sri Lanka tourism")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        selected_city = st.selectbox(
            "Select City",
            [city["name"] for city in APIConfig.SRI_LANKA_CITIES]
        )

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "🌡️ Weather",
        "✈️ Flights",
        "💱 Exchange Rates"
    ])

    with tab1:
        display_weather_info(selected_city)

    with tab2:
        display_flight_info()

    with tab3:
        display_exchange_rates()


def display_weather_info(city: str):
    st.header(f"🌡️ Weather in {city}")

    city_info = next(
        (c for c in APIConfig.SRI_LANKA_CITIES if c["name"] == city),
        None
    )

    if not city_info:
        st.error("City not found")
        return

    col1, col2 = st.columns([1, 2])

    # Current weather
    with col1:
        st.subheader("Current Weather")
        weather = WeatherService.get_current_weather(
            city, city_info["lat"], city_info["lon"]
        )

        if weather:
            st.metric("Temperature", f"{weather['temperature']:.1f} °C")
            st.metric("Feels Like", f"{weather['feels_like']:.1f} °C")
            st.metric("Humidity", f"{weather['humidity']}%")
            st.metric("Wind Speed", f"{weather['wind_speed']} m/s")
            st.info(f"Condition: {weather['description'].title()}")
        else:
            st.warning("Weather data unavailable")

    # Forecast
    with col2:
        st.subheader("5-Day Forecast")
        forecast = WeatherService.get_forecast(
            city, city_info["lat"], city_info["lon"]
        )

        if forecast:
            df = pd.DataFrame(forecast)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["datetime"],
                y=df["temperature"],
                mode="lines+markers",
                name="Temperature"
            ))

            fig.update_layout(
                title="Temperature Forecast",
                xaxis_title="Date & Time",
                yaxis_title="Temperature (°C)",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                df[[
                    "datetime",
                    "temperature",
                    "description",
                    "humidity",
                    "rain_probability"
                ]].head(10),
                use_container_width=True
            )
        else:
            st.warning("Forecast data unavailable")

    # All cities comparison
    st.divider()
    st.subheader("🌍 Weather Across Sri Lanka")

    all_weather = TourismDataAggregator.get_all_cities_weather()
    if all_weather:
        df_all = pd.DataFrame(all_weather)

        fig = px.bar(
            df_all,
            x="city",
            y="temperature",
            color="temperature",
            labels={
                "city": "City",
                "temperature": "Temperature (°C)"
            },
            title="Temperature Comparison Across Cities"
        )

        st.plotly_chart(fig, use_container_width=True)


def display_flight_info():
    st.header("✈️ Arrivals to Colombo (CMB)")
    st.caption("Live international flight arrivals")

    with st.spinner("Loading flight data..."):
        flights = FlightService.get_flight_arrivals()

    if not flights:
        st.info("Enable AviationStack API key to view flight data.")
        return

    df = pd.DataFrame(flights)

    # --- Status mapping ---
    status_map = {
        "scheduled": "🟢 On Time",
        "active": "🟢 On Time",
        "delayed": "🟠 Delayed",
        "cancelled": "🔴 Cancelled",
        "landed": "✅ Landed"
    }

    df["status_label"] = df["status"].map(status_map).fillna("⚪ Unknown")

    # Format arrival time
    df["scheduled"] = pd.to_datetime(df["scheduled"]).dt.strftime("%d %b %Y • %H:%M")

    # --- Top metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Flights", len(df))
    col2.metric("On Time", sum(df["status"].isin(["scheduled", "active"])))
    col3.metric("Airlines", df["airline"].nunique())

    st.divider()

    # --- Filters ---
    col1, col2 = st.columns([2, 1])
    search = col1.text_input("🔍 Search flight / airline / origin")
    status_filter = col2.selectbox(
        "Status",
        ["All", "On Time", "Delayed", "Cancelled", "Landed"]
    )

    if search:
        df = df[
            df["flight_number"].str.contains(search, case=False, na=False) |
            df["airline"].str.contains(search, case=False, na=False) |
            df["origin"].str.contains(search, case=False, na=False)
        ]

    if status_filter != "All":
        df = df[df["status_label"].str.contains(status_filter)]

    # --- Display as cards ---
    for _, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1.2, 2.5, 2, 1.5])

            with col1:
                st.markdown(f"### {row['flight_number']}")
                st.caption(row["airline"])

            with col2:
                st.markdown(f"**From:** {row['origin']}, {row['origin_country']}")
                st.caption(f"🕒 {row['scheduled']}")

            with col3:
                st.markdown("**Status**")
                st.markdown(row["status_label"])

            with col4:
                st.markdown("**Arrival**")
                st.markdown("CMB")

            st.divider()



def display_exchange_rates():
    st.header("💱 Currency Exchange Rates")

    rates = ExchangeRateService.get_rates()

    if not rates:
        st.error("Exchange rate data unavailable")
        return

    st.info(f"Base: {rates['base']} | Updated: {rates['date']}")

    currencies = {
        "LKR": "🇱🇰 Sri Lankan Rupee",
        "USD": "🇺🇸 US Dollar",
        "EUR": "🇪🇺 Euro",
        "GBP": "🇬🇧 British Pound",
        "INR": "🇮🇳 Indian Rupee",
        "AUD": "🇦🇺 Australian Dollar"
    }

    cols = st.columns(2)
    for i, (code, label) in enumerate(currencies.items()):
        if code in rates:
            cols[i % 2].metric(label, f"{rates[code]:.2f}")

    st.divider()
    st.subheader("Currency Converter")

    col1, col2, col3 = st.columns(3)
    amount = col1.number_input("Amount", min_value=0.0, value=100.0)
    from_curr = col2.selectbox("From", currencies.keys())
    to_curr = col3.selectbox("To", currencies.keys(), index=1)

    if from_curr in rates and to_curr in rates:
        converted = amount * (rates[to_curr] / rates[from_curr])
        st.success(f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr}")


if __name__ == "__main__":
    main()
