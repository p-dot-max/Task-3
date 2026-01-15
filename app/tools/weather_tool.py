# https://docs.langchain.com/oss/python/langchain/overview

import json
from pathlib import Path
from typing import Dict, Any, Optional

def get_weather(city: str) -> Dict[str, Any]:
    project_root = Path(__file__).parent.parent.parent
    # Hardcoded here to get the ehweater data
    weather_file = project_root / "data" / "weather.json"
    
    # Read and load the data
    with open(weather_file, 'r', encoding='utf-8') as f:
        weather_data = json.load(f)
    
    if city.lower() in weather_data["location"]["city"].lower():
        return {
            "city": weather_data["location"]["city"],
            "country": weather_data["location"]["country"],
            "current": weather_data["current_weather"],
            "forecast": weather_data["forecast"]
        }

    else:
        return {
            "error": f"Weather data not available for {city}",
            "available_city": weather_data["location"]["city"]
        }


def get_current_weather(city: str) -> str:
    data = get_weather(city)
    
    if "error" in data:
        return data["error"]
    
    current = data["current"]

    return f"{data['city']}: {current['temperature_cel']}, {current['condition']}"


def get_forecast(city: str, days: int = 3) -> str:
    data = get_weather(city)
    
    if "error" in data:
        return str("Error in data")
    
    result = f"Forecast for {data['city']}:\n"
    
    for day in data["forecast"][:days]:
        
        max_temp = day['max_temp_celsius']
        
        min_temp = day['min_temp_celsius']

        result += f"{day['day_of_week']}: {max_temp}/{min_temp} - {day['condition']}\n"
    
    return result.strip()





