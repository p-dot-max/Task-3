# https://docs.langchain.com/oss/python/langchain/overview

import json
from pathlib import Path
from typing import Dict, Any, Optional
from langchain.tools import tool

@tool
def get_weather(city: str) -> Dict[str, Any]:

    """

    Retrieves weather data for a specific city, including current temperature, 
    conditions, and a multi-day forecast. Use this for all weather-related queries.

    """

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

    return {"error": f"Weather data is not available for the {city}"}







