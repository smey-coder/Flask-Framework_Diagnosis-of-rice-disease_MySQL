import requests
import os
from typing import Optional, Dict, Any

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""

    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    API_KEY = os.environ.get("OPENWEATHER_API_KEY")

    @staticmethod
    def get_weather(city_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a city by name.

        Args:
            city_name: City name

        Returns:
            Weather data dict or None if error
        """
        try:
            params = {
                'q': city_name + ',KH',  # Add country code for Cambodia
                'appid': WeatherService.API_KEY,
                'units': 'metric'  # Celsius
            }

            response = requests.get(WeatherService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract relevant weather info
            weather_info = {
                'city': data['name'],
                'country': data.get('sys', {}).get('country', ''),
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # km
                'clouds': data['clouds']['all'],
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
            return weather_info

        except requests.RequestException as e:
            print(f"Error fetching weather: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing weather data: {e}")
            return None

    @staticmethod
    def get_countries() -> Dict[str, str]:
        """Return a dict of country codes to country names (deprecated - now Cambodia only)"""
        return {'KH': 'Cambodia'}