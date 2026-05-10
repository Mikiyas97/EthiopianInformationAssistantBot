import requests
from utils.config import WEATHER_API_KEY

def get_weather_report(city_name, safety_guideline):
    """
    Fetches weather from OpenWeatherMap and returns a formatted string.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={WEATHER_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            main = data['main']
            desc = data['weather'][0]['description']
            
            return (
                f"⛅️ **Weather: {city_name}**\n"
                f"🌡️ Temp: {main['temp']}°C\n"
                f"🤗 Feels Like: {main['feels_like']}°C\n"
                f"💧 Humidity: {main['humidity']}%\n"
                f"☁️ Condition: {desc.capitalize()}\n\n"
            )
        else:
            return f"⚠️ Weather data unavailable for '{city_name}'.\n"
    except Exception as e:
        return "❌ Connection error fetching weather data."