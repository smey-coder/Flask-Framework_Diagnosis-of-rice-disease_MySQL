import requests
import os
from typing import Optional, Dict, Any

class WeatherService:
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    API_KEY = os.environ.get("OPENWEATHER_API_KEY")

    # MAPPING ខេត្តទៅកាន់ទីប្រជុំជន/ក្រុង ដើម្បីឱ្យ API ស្វែងរកមិនខុស
    PROVINCE_MAP = {
        "Banteay Meanchey": "Sisophon",
        "Kampong Cham": "Kampong Cham",
        "Kampong Chhnang": "Kampong Chhnang",
        "Kampong Speu": "Chbar Mon",
        "Kampong Thom": "Steung Saen",
        "Kampot": "Kampot",
        "Kandal": "Ta Khmau",
        "Kep": "Kep",
        "Koh Kong": "Khemarak Phoumin",
        "Kratie": "Kratie",
        "Mondulkiri": "Sen Monorom",
        "Oddar Meanchey": "Samraong",
        "Pailin": "Pailin",
        "Phnom Penh": "Phnom Penh",
        "Preah Vihear": "Tbeng Meanchey",
        "Prey Veng": "Prey Veng",
        "Pursat": "Pursat",
        "Ratanakiri": "Banlung",
        "Siem Reap": "Siem Reap",
        "Preah Sihanouk": "Sihanoukville",
        "Stung Treng": "Stung Treng",
        "Svay Rieng": "Svay Rieng",
        "Takeo": "Takeo",
        "Tboung Khmum": "Suong"
    }

    @classmethod
    def get_weather_by_farm(cls, farm) -> Optional[Dict[str, Any]]:
        """
        Safely extract coordinates or fallback to province name.
        """
        weather_data = None

        if farm:
            # 1. Try GPS Coordinates first
            try:
                if farm.latitude is not None and farm.longitude is not None:
                    lat = float(farm.latitude)
                    lon = float(farm.longitude)
                    # Ensure coordinates are non-zero/valid
                    if lat != 0 and lon != 0:
                        weather_data = cls.get_weather_by_coords(lat, lon)
            except (ValueError, TypeError) as e:
                print(f"Coordinate conversion error: {e}")

            # 2. Fallback to Province name if GPS fails or returns no data
            if not weather_data and hasattr(farm, 'province') and farm.province:
                mapped_city = cls.PROVINCE_MAP.get(farm.province, farm.province)
                weather_data = cls.get_weather(mapped_city)

            # 3. Attach original farm province for correct front-end display
            if weather_data and hasattr(farm, 'province') and farm.province:
                weather_data['farm_province'] = farm.province

        return weather_data

    @classmethod
    def get_weather_by_coords(cls, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        params = {'lat': lat, 'lon': lon, 'appid': cls.API_KEY, 'units': 'metric'}
        return cls._fetch_api(params)

    @classmethod
    def get_weather(cls, city_name: str) -> Optional[Dict[str, Any]]:
        params = {'q': f"{city_name},KH", 'appid': cls.API_KEY, 'units': 'metric'}
        return cls._fetch_api(params)

    @classmethod
    def _fetch_api(cls, params: dict) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(cls.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            raw_visibility = data.get("visibility", 10000)
            visibility_km = round(raw_visibility / 1000, 1)

            clouds_pct = data.get("clouds", {}).get("all", 0)

            return {
                'city': data.get('name', ''),
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                "visibility": visibility_km,  # Properly formatted as km
                "clouds": clouds_pct,          # Properly extracted percentage
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
            }
        except (requests.RequestException, KeyError) as e:
            print(f"Error fetching weather: {e}")
            return None