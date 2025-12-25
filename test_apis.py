# test_apis.py
from backend.api_config import APIConfig, get_weather_for_city
import requests

def test_apis():
    print("Testing API Integrations...")
    print("=" * 60)
    
    # 1️⃣ Check API status
    status = APIConfig.get_api_status()
    print("\nAPI Configuration Status:")
    for api, configured in status.items():
        print(f"  {api}: {'✓ Configured' if configured else '✗ Not configured'}")
    
    # 2️⃣ Test Weather API
    print("\n1. Testing Weather API...")
    weather = get_weather_for_city('Colombo')
    if 'error' not in weather:
        print(f"   ✓ Weather in {weather['city']}: {weather['temperature']}°C, {weather['weather']}, Humidity: {weather['humidity']}%, Wind: {weather['wind_speed']} m/s")
    else:
        print(f"   ✗ Weather API failed: {weather['error']}")
    
    # 3️⃣ Test Exchange Rate API
    print("\n2. Testing Exchange Rate API...")
    try:
        response = requests.get(APIConfig.EXCHANGE_RATE_API_URL)
        if response.status_code == 200:
            data = response.json()
            lkr_rate = data.get('rates', {}).get('LKR', 'N/A')
            print(f"   ✓ Exchange Rate USD → LKR: {lkr_rate}")
        else:
            print(f"   ✗ Exchange Rate API failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Exchange Rate API exception: {e}")
    
    # 4️⃣ Test Flight Data API (AviationStack)
    print("\n3. Testing Flight Data API (AviationStack)...")
    if not APIConfig.AVIATIONSTACK_API_KEY:
        print("   ✗ AviationStack API key not configured")
    else:
        try:
            url = f"{APIConfig.AVIATIONSTACK_BASE_URL}/flights"
            params = {
                'access_key': APIConfig.AVIATIONSTACK_API_KEY,
                'limit': 1
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                flights = data.get('data', [])
                if flights:
                    flight = flights[0]
                    airline = flight.get('airline', {}).get('name', 'N/A')
                    flight_iata = flight.get('flight', {}).get('iata', 'N/A')
                    print(f"   ✓ Flight found: {airline} - {flight_iata}")
                else:
                    print("   ✗ No flight data available")
            else:
                print(f"   ✗ AviationStack API request failed: Status {response.status_code}")
        except Exception as e:
            print(f"   ✗ AviationStack API exception: {e}")
    
    # 5️⃣ Test RapidAPI / Booking.com
    print("\n4. Testing RapidAPI (Booking.com)...")
    if not APIConfig.RAPIDAPI_KEY:
        print("   ✗ RapidAPI key not configured")
    else:
        try:
            url = f"{APIConfig.BOOKING_API_URL}/hotels/search"
            headers = {
                'X-RapidAPI-Key': APIConfig.RAPIDAPI_KEY,
                'X-RapidAPI-Host': 'booking-com.p.rapidapi.com'
            }
            params = {
                'city_name': 'Colombo',
                'checkin_date': '2025-12-25',
                'checkout_date': '2025-12-26',
                'adults_number': 1,
                'locale': 'en-gb',
                'order_by': 'popularity',
                'filter_by_currency': 'USD',
                'room_number': 1
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and len(data['result']) > 0:
                    hotel = data['result'][0]['hotel_name']
                    print(f"   ✓ Hotel found: {hotel}")
                else:
                    print("   ✗ No hotels found")
            else:
                print(f"   ✗ RapidAPI request failed: Status {response.status_code}")
        except Exception as e:
            print(f"   ✗ RapidAPI exception: {e}")
    
    # 6️⃣ Test Travel Advisory API
    print("\n5. Testing Travel Advisory API...")
    try:
        response = requests.get(APIConfig.TRAVEL_ADVISORY_URL)
        if response.status_code == 200:
            data = response.json()
            score = data.get('data', {}).get('LK', {}).get('advisory', {}).get('score', 'N/A')
            print(f"   ✓ Sri Lanka Travel Advisory Score: {score}/5")
        else:
            print(f"   ✗ Travel Advisory API failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Travel Advisory API exception: {e}")
    
    # 7️⃣ Optional: Test Amadeus API (if keys provided)
    print("\n6. Testing Amadeus API (Optional)...")
    if not (APIConfig.AMADEUS_API_KEY and APIConfig.AMADEUS_API_SECRET):
        print("   ✗ Amadeus API key/secret not configured")
    else:
        try:
            # Get access token first
            token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
            data = {
                'grant_type': 'client_credentials',
                'client_id': APIConfig.AMADEUS_API_KEY,
                'client_secret': APIConfig.AMADEUS_API_SECRET
            }
            token_resp = requests.post(token_url, data=data)
            if token_resp.status_code == 200:
                access_token = token_resp.json().get('access_token')
                print(f"   ✓ Amadeus access token retrieved: {access_token[:10]}...")  # show first 10 chars
            else:
                print(f"   ✗ Amadeus token request failed: Status {token_resp.status_code}")
        except Exception as e:
            print(f"   ✗ Amadeus API exception: {e}")
    
    print("\n" + "=" * 60)
    print("All API testing complete!")


if __name__ == "__main__":
    test_apis()
