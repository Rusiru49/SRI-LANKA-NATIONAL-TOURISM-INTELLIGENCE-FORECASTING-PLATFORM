import os
from typing import Dict
from dotenv import load_dotenv
import requests

# Load .env file
load_dotenv()

class APIConfig:
    """Configuration for external tourism APIs"""
    
    # Weather API (OpenWeatherMap)
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    
    # Booking.com API (RapidAPI)
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    BOOKING_API_URL = 'https://booking-com.p.rapidapi.com/v1'
    
    # Flight Data (AviationStack)
    AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY', '')
    AVIATIONSTACK_BASE_URL = 'http://api.aviationstack.com/v1'
    
    # Exchange Rates
    EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'
    
    # Travel Advisories
    TRAVEL_ADVISORY_URL = 'https://www.travel-advisory.info/api'
    
    # Amadeus API
    AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY', '')
    AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET', '')
    AMADEUS_BASE_URL = 'https://test.api.amadeus.com/v1'
    
    # Sri Lankan cities for weather/hotel searches
    SRI_LANKA_CITIES = [
        {'name': 'Colombo', 'lat': 6.9271, 'lon': 79.8612},
        {'name': 'Kandy', 'lat': 7.2906, 'lon': 80.6337},
        {'name': 'Galle', 'lat': 6.0535, 'lon': 80.2210},
        {'name': 'Jaffna', 'lat': 9.6615, 'lon': 80.0255},
        {'name': 'Nuwara Eliya', 'lat': 6.9497, 'lon': 80.7891},
        {'name': 'Anuradhapura', 'lat': 8.3114, 'lon': 80.4037},
        {'name': 'Trincomalee', 'lat': 8.5874, 'lon': 81.2152}
    ]
    
    @classmethod
    def get_api_status(cls) -> Dict[str, bool]:
        """Check which APIs are configured"""
        return {
            'openweather': bool(cls.OPENWEATHER_API_KEY and cls.OPENWEATHER_API_KEY != 'OPENWEATHER_API_KEY'),
            'rapidapi': bool(cls.RAPIDAPI_KEY and cls.RAPIDAPI_KEY != 'RAPIDAPI_KEY'),
            'aviationstack': bool(cls.AVIATIONSTACK_API_KEY and cls.AVIATIONSTACK_API_KEY != 'AVIATIONSTACK_API_KEY'),
            'amadeus': bool(cls.AMADEUS_API_KEY and cls.AMADEUS_API_KEY != 'your_amadeus_key_here')
        }


# =========================
# Sample Function to Fetch Weather
# =========================
def get_weather_for_city(city_name: str) -> Dict:
    """Fetch current weather for a given city in Sri Lanka"""
    city = next((c for c in APIConfig.SRI_LANKA_CITIES if c['name'].lower() == city_name.lower()), None)
    if not city:
        return {'error': 'City not found in Sri Lanka list.'}
    
    url = f"{APIConfig.OPENWEATHER_BASE_URL}/weather"
    params = {
        'lat': city['lat'],
        'lon': city['lon'],
        'appid': APIConfig.OPENWEATHER_API_KEY,
        'units': 'metric'  # Celsius
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {'error': f"Failed to fetch weather: {response.status_code}"}
    
    data = response.json()
    return {
        'city': city['name'],
        'temperature': data['main']['temp'],
        'weather': data['weather'][0]['description'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed']
    }


# =========================
# Quick Test
# =========================
if __name__ == "__main__":
    print("API Status:", APIConfig.get_api_status())
    print("Weather in Colombo:", get_weather_for_city('Colombo'))
