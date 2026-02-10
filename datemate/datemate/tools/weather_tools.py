# -*- coding: utf-8 -*-
"""
Weather tools for DateMate AI.

These tools fetch or simulate weather forecasts and sunset times to help
the agents choose appropriate activities and add romantic touches.
"""

import os
from typing import Dict, Any, List

import requests

try:
    from google.adk.tools import Tool  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback if ADK Tool is unavailable
    def Tool(func):  # type: ignore[override]
        """Fallback no-op decorator when google.adk.tools.Tool is missing."""
        return func


def _mock_weather(location: str, date: str) -> Dict[str, Any]:
    """Return realistic mock weather for Vancouver-style climates."""
    condition = "Partly cloudy"
    temperature_c = 10.0
    temperature_f = round(temperature_c * 9.0 / 5.0 + 32.0, 1)
    precipitation_chance = 30
    wind_speed_kmh = 10.0
    humidity = 75

    recommendations: List[str] = [
        "Bring a light jacket or sweater.",
        "Consider an umbrella or hooded coat, just in case.",
        "Outdoor walks are pleasant but have an indoor backup plan.",
    ]

    date_friendliness_score = 7

    return {
        "location": location,
        "date": date,
        "condition": condition,
        "temperature_c": temperature_c,
        "temperature_f": temperature_f,
        "precipitation_chance": precipitation_chance,
        "wind_speed_kmh": wind_speed_kmh,
        "humidity": humidity,
        "sunrise": "08:00",
        "sunset": "17:30",
        "recommendations": recommendations,
        "date_friendliness_score": date_friendliness_score,
    }


@Tool
def get_weather_forecast(location: str, date: str) -> Dict[str, Any]:
    """
    Get a weather forecast for a specific location and date.

    This tool:
    - Uses the OpenWeather 5-day / 3-hour forecast API when `OPENWEATHER_API_KEY`
      is configured to obtain conditions close to the requested date.
    - Falls back to realistic mock data (Vancouver-like climate) when no API key
      is available, so tests and development remain reliable.

    Args:
        location: City or "City, Country" string.
        date: Target date in ISO format (YYYY-MM-DD).

    Returns:
        A dict with:
        - condition: str
        - temperature_c: float
        - temperature_f: float
        - precipitation_chance: int (0–100)
        - wind_speed_kmh: float
        - humidity: int
        - sunrise: str (HH:MM)
        - sunset: str (HH:MM)
        - recommendations: list[str]
        - date_friendliness_score: int (0–10)
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return _mock_weather(location, date)

    try:
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
        }
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        # Pick the first forecast as an approximation for now
        first = (data.get("list") or [{}])[0]
        main = first.get("main", {})
        weather_list = first.get("weather") or [{}]
        weather_info = weather_list[0]

        temp_c = float(main.get("temp", 10.0))
        temp_f = round(temp_c * 9.0 / 5.0 + 32.0, 1)
        condition = weather_info.get("description", "Partly cloudy").title()
        precipitation_chance = int(first.get("pop", 0) * 100)
        wind_speed_kmh = float(first.get("wind", {}).get("speed", 3.0)) * 3.6
        humidity = int(main.get("humidity", 70))

        recommendations: List[str] = []
        if temp_c < 5:
            recommendations.append("Dress warmly with layers, scarf, and gloves.")
        elif temp_c < 15:
            recommendations.append("A medium jacket or coat is recommended.")
        else:
            recommendations.append("Light layers are ideal for this temperature.")

        if precipitation_chance > 50:
            recommendations.append("Bring an umbrella or plan more indoor activities.")

        if wind_speed_kmh > 20:
            recommendations.append("Wind may make it feel cooler near the water.")

        score = 8
        if precipitation_chance > 60:
            score -= 2
        if temp_c < 0 or temp_c > 28:
            score -= 2
        score = max(0, min(10, score))

        result = {
            "location": location,
            "date": date,
            "condition": condition,
            "temperature_c": temp_c,
            "temperature_f": temp_f,
            "precipitation_chance": precipitation_chance,
            "wind_speed_kmh": round(wind_speed_kmh, 1),
            "humidity": humidity,
            "sunrise": "08:00",
            "sunset": "17:30",
            "recommendations": recommendations,
            "date_friendliness_score": score,
        }
        return result
    except Exception as exc:  # pragma: no cover - network / API failures
        mock = _mock_weather(location, date)
        return {"error": str(exc), "fallback": True, **mock}


@Tool
def get_sunset_time(location: str, date: str) -> Dict[str, Any]:
    """
    Get an approximate sunset time and golden hour suggestion for a location and date.

    This tool currently returns realistic mock values that are sufficient for
    planning romantic evening activities, but can be extended to call external
    APIs such as sunrise-sunset.org.

    Args:
        location: City or coordinates where the date will happen.
        date: Target date in ISO format (YYYY-MM-DD).

    Returns:
        A dict with:
        - sunset_time: str (HH:MM)
        - golden_hour_start: str (HH:MM)
        - suggestion: str human-friendly suggestion for timing an activity.
    """
    # Simple mock approximation suitable for Vancouver winter / general use.
    sunset_time = "17:30"
    golden_hour_start = "16:30"
    suggestion = (
        "Plan any waterfront walk or viewpoint stop to arrive around 30 minutes "
        "before sunset for the best golden-hour light."
    )

    return {
        "location": location,
        "date": date,
        "sunset_time": sunset_time,
        "golden_hour_start": golden_hour_start,
        "suggestion": suggestion,
    }

