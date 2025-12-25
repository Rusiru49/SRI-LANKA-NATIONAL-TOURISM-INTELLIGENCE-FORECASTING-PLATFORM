"""
External API Integration Services
Place this in: backend/api_services.py
"""

import requests
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from backend.api_config import APIConfig

class WeatherService:
    """OpenWeatherMap API integration"""
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_current_weather(city: str, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather for a city"""
        try:
            url = f"{APIConfig.OPENWEATHER_BASE_URL}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': APIConfig.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'city': city,
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed']
            }
        except Exception as e:
            st.warning(f"Weather data unavailable for {city}: {str(e)}")
            return None
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_forecast(city: str, lat: float, lon: float, days: int = 5) -> Optional[List[Dict]]:
        """Get weather forecast"""
        try:
            url = f"{APIConfig.OPENWEATHER_BASE_URL}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': APIConfig.OPENWEATHER_API_KEY,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data['list']:
                forecasts.append({
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description'],
                    'humidity': item['main']['humidity'],
                    'rain_probability': item.get('pop', 0) * 100
                })
            return forecasts
        except Exception as e:
            st.warning(f"Forecast unavailable for {city}: {str(e)}")
            return None


class HotelService:
    """Booking.com API integration (via RapidAPI)"""
    
    @staticmethod
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def search_hotels(city: str, checkin: str, checkout: str, adults: int = 2) -> Optional[List[Dict]]:
        """Search hotels in a city"""
        try:
            url = f"{APIConfig.BOOKING_API_URL}/hotels/search"
            headers = {
                'X-RapidAPI-Key': APIConfig.RAPIDAPI_KEY,
                'X-RapidAPI-Host': 'booking-com.p.rapidapi.com'
            }
            params = {
                'query': f"{city}, Sri Lanka",
                'checkin_date': checkin,
                'checkout_date': checkout,
                'adults_number': adults,
                'locale': 'en-us',
                'currency': 'USD',
                'units': 'metric'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            hotels = []
            for hotel in data.get('result', [])[:10]:  # Top 10 hotels
                hotels.append({
                    'name': hotel.get('hotel_name', 'N/A'),
                    'price': hotel.get('min_total_price', 0),
                    'rating': hotel.get('review_score', 0),
                    'review_count': hotel.get('review_nr', 0),
                    'url': hotel.get('url', '#'),
                    'address': hotel.get('address', 'N/A')
                })
            return hotels
        except Exception as e:
            st.warning(f"Hotel search unavailable: {str(e)}")
            return None


class FlightService:
    """Flight data using AviationStack API"""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_flight_arrivals(airport_code: str = 'CMB') -> Optional[List[Dict]]:
        """Get arrivals to Colombo (CMB) airport"""
        try:
            url = f"{APIConfig.AVIATIONSTACK_BASE_URL}/flights"
            params = {
                'access_key': APIConfig.AVIATIONSTACK_API_KEY,
                'arr_iata': airport_code,
                'limit': 20
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            flights = []
            for flight in data.get('data', []):
                flights.append({
                    'flight_number': flight.get('flight', {}).get('iata', 'N/A'),
                    'airline': flight.get('airline', {}).get('name', 'N/A'),
                    'origin': flight.get('departure', {}).get('airport', 'N/A'),
                    'origin_country': flight.get('departure', {}).get('timezone', 'N/A'),
                    'scheduled': flight.get('arrival', {}).get('scheduled', 'N/A'),
                    'status': flight.get('flight_status', 'N/A')
                })
            return flights
        except Exception as e:
            st.warning(f"Flight data unavailable: {str(e)}")
            return None


class ExchangeRateService:
    """Currency exchange rates"""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_rates() -> Optional[Dict]:
        """Get current exchange rates"""
        try:
            response = requests.get(APIConfig.EXCHANGE_RATE_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Focus on major currencies for Sri Lanka tourism
            relevant_currencies = ['LKR', 'EUR', 'GBP', 'INR', 'AUD', 'CNY', 'JPY']
            rates = {curr: data['rates'].get(curr, 0) for curr in relevant_currencies}
            rates['base'] = data['base']
            rates['date'] = data['date']
            
            return rates
        except Exception as e:
            st.warning(f"Exchange rates unavailable: {str(e)}")
            return None


class TravelAdvisoryService:
    """Travel safety advisories"""
    
    @staticmethod
    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def get_advisory(country_code: str = 'LK') -> Optional[Dict]:
        """Get travel advisory for Sri Lanka"""
        try:
            url = f"{APIConfig.TRAVEL_ADVISORY_URL}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            advisory = data.get('data', {}).get(country_code, {})
            
            return {
                'score': advisory.get('advisory', {}).get('score', 0),
                'message': advisory.get('advisory', {}).get('message', 'No advisory'),
                'sources': advisory.get('advisory', {}).get('sources', []),
                'updated': advisory.get('advisory', {}).get('updated', 'Unknown')
            }
        except Exception as e:
            st.warning(f"Travel advisory unavailable: {str(e)}")
            return None


class TourismDataAggregator:
    """Aggregate data from all services"""
    
    @staticmethod
    def get_comprehensive_data(city: str) -> Dict:
        """Get all available data for a city"""
        city_info = next((c for c in APIConfig.SRI_LANKA_CITIES if c['name'] == city), None)
        if not city_info:
            return {}
        
        return {
            'weather': WeatherService.get_current_weather(city, city_info['lat'], city_info['lon']),
            'forecast': WeatherService.get_forecast(city, city_info['lat'], city_info['lon']),
            'exchange_rates': ExchangeRateService.get_rates(),
            'travel_advisory': TravelAdvisoryService.get_advisory()
        }
    
    @staticmethod
    def get_all_cities_weather() -> List[Dict]:
        """Get weather for all major Sri Lankan cities"""
        weather_data = []
        for city in APIConfig.SRI_LANKA_CITIES:
            weather = WeatherService.get_current_weather(city['name'], city['lat'], city['lon'])
            if weather:
                weather_data.append(weather)
        return weather_data