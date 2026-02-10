# -*- coding: utf-8 -*-
"""
Activity tools for DateMate AI.

These tools search for romantic activities and fetch detailed information
using Google Places when API keys are available, and otherwise return
rich mock data suitable for testing and offline development.
"""

import os
from typing import Dict, List, Any

try:
    from google.adk.tools import Tool  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback if ADK Tool is unavailable
    def Tool(func):  # type: ignore[override]
        """Fallback no-op decorator when google.adk.tools.Tool is missing."""
        return func

try:
    import googlemaps
except Exception:  # pragma: no cover - optional dependency
    googlemaps = None


def _mock_activities(location: str, preferences: List[str]) -> Dict[str, Any]:
    """Return a rich set of mock activities for fallback usage."""
    base_activities = [
        {
            "name": "Vancouver Art Gallery",
            "address": "750 Hornby St, Vancouver, BC",
            "type": "Art & Museums",
            "price": 30,
            "duration_minutes": 90,
            "rating": 4.6,
            "romantic_score": 8,
            "weather_dependent": False,
            "description": "Explore world-class art exhibits in an intimate, inspiring setting.",
        },
        {
            "name": "Granville Island",
            "address": "1661 Duranleau St, Vancouver, BC",
            "type": "Shopping",
            "price": 0,
            "duration_minutes": 120,
            "rating": 4.7,
            "romantic_score": 8,
            "weather_dependent": True,
            "description": "Stroll through the public market, artisan shops, and waterfront views.",
        },
        {
            "name": "Stanley Park Seawall",
            "address": "Stanley Park, Vancouver, BC",
            "type": "Outdoors & Nature",
            "price": 0,
            "duration_minutes": 90,
            "rating": 4.9,
            "romantic_score": 9,
            "weather_dependent": True,
            "description": "Iconic seawall walk with ocean and mountain views, perfect for sunset.",
        },
        {
            "name": "VanDusen Botanical Garden",
            "address": "5251 Oak St, Vancouver, BC",
            "type": "Outdoors & Nature",
            "price": 24,
            "duration_minutes": 90,
            "rating": 4.7,
            "romantic_score": 9,
            "weather_dependent": True,
            "description": "Beautiful botanical garden with winding paths and quiet corners.",
        },
        {
            "name": "Capilano Suspension Bridge Park",
            "address": "3735 Capilano Rd, North Vancouver, BC",
            "type": "Outdoors & Nature",
            "price": 70,
            "duration_minutes": 120,
            "rating": 4.6,
            "romantic_score": 8,
            "weather_dependent": True,
            "description": "Suspension bridge, treetop walks, and canyon views for adventurous couples.",
        },
        {
            "name": "Breakout Escape Rooms",
            "address": "Various locations",
            "type": "Escape Rooms",
            "price": 35,
            "duration_minutes": 60,
            "rating": 4.5,
            "romantic_score": 7,
            "weather_dependent": False,
            "description": "Work together to solve puzzles and escape within 60 minutes.",
        },
        {
            "name": "Clay Cafe Pottery Studio",
            "address": "Local pottery studio",
            "type": "Pottery Class",
            "price": 45,
            "duration_minutes": 90,
            "rating": 4.6,
            "romantic_score": 9,
            "weather_dependent": False,
            "description": "Hand-paint pottery pieces together for a keepsake from your date.",
        },
        {
            "name": "Gourmet Cooking Class",
            "address": "Local cooking school",
            "type": "Cooking Class",
            "price": 80,
            "duration_minutes": 150,
            "rating": 4.8,
            "romantic_score": 9,
            "weather_dependent": False,
            "description": "Learn to cook a multi-course meal side by side, then enjoy it together.",
        },
    ]

    if not preferences:
        return {"activities": base_activities, "total_found": len(base_activities)}

    lowered_prefs = [p.lower() for p in preferences]
    filtered = [
        a
        for a in base_activities
        if any(pref in a["type"].lower() or pref in a["name"].lower() for pref in lowered_prefs)
    ]
    if not filtered:
        filtered = base_activities
    return {"activities": filtered, "total_found": len(filtered)}


@Tool
def search_activities(
    location: str,
    preferences: List[str],
    date: str,
    budget_per_activity: int = 50,
) -> Dict[str, Any]:
    """
    Search for romantic date activities near a location, optionally using Google Places.

    This tool:
    - Uses Google Places API (if `GOOGLE_PLACES_API_KEY` is set) to search nearby activities
      that match the user's preferences and budget.
    - Falls back to realistic mock data for Vancouver and general cities when no API key
      is available.

    Args:
        location: City or address to search around (e.g., "Vancouver, BC").
        preferences: List of interest keywords (e.g., ["art", "outdoors"]).
        date: Date of the planned activity in ISO format (YYYY-MM-DD).
        budget_per_activity: Approximate budget in local currency per activity (for 2 people).

    Returns:
        A dict with:
        - activities: list of activities, each:
            {
                "name": str,
                "address": str,
                "type": str,
                "price": int,
                "duration_minutes": int,
                "rating": float,
                "romantic_score": int,
                "weather_dependent": bool,
                "description": str,
            }
        - total_found: total number of activities considered
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key or googlemaps is None:
        return _mock_activities(location, preferences)

    try:
        client = googlemaps.Client(key=api_key)
        keyword = ", ".join(preferences) if preferences else "date activities"
        response = client.places_nearby(
            location=location,
            radius=5000,
            keyword=keyword,
        )
        activities: List[Dict[str, Any]] = []
        for place in response.get("results", [])[:10]:
            price_level = place.get("price_level", 2)
            price = max(0, min(4, price_level)) * 15
            activities.append(
                {
                    "name": place.get("name"),
                    "address": place.get("vicinity") or place.get("formatted_address", location),
                    "type": keyword,
                    "price": price,
                    "duration_minutes": 90,
                    "rating": place.get("rating", 4.5),
                    "romantic_score": 8,
                    "weather_dependent": True,
                    "description": place.get("types", ["Fun date activity"])[0].replace("_", " ").title(),
                }
            )
        if not activities:
            return _mock_activities(location, preferences)
        return {"activities": activities, "total_found": len(activities)}
    except Exception as exc:  # pragma: no cover - network / API failures
        mock_data = _mock_activities(location, preferences)
        return {"error": str(exc), "fallback": True, **mock_data}


@Tool
def get_activity_details(place_name: str, location: str) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific activity or place.

    This tool:
    - Uses Google Places `find_place` and `place` endpoints when `GOOGLE_PLACES_API_KEY`
      is configured.
    - Falls back to structured mock details when no API key is available.

    Args:
        place_name: Name of the activity or venue (e.g., "Vancouver Art Gallery").
        location: City or area for disambiguation (e.g., "Vancouver, BC").

    Returns:
        A dict with:
        - name: str
        - opening_hours: str
        - photos_url: str
        - tips: list[str]
        - website: str
        - phone: str
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key or googlemaps is None:
        return {
            "name": place_name,
            "opening_hours": "Varies by season, typically 10:00–18:00",
            "photos_url": "https://example.com/photos/" + place_name.replace(" ", "_"),
            "tips": [
                "Arrive 10–15 minutes early to avoid lines.",
                "Look for quieter corners to sit and talk.",
                "Check for special exhibitions or events on the date.",
            ],
            "website": "https://example.com/" + place_name.replace(" ", "").lower(),
            "phone": "+1-000-000-0000",
        }

    try:
        client = googlemaps.Client(key=api_key)
        find_resp = client.find_place(
            input=place_name,
            input_type="textquery",
            fields=["place_id"],
        )
        candidates = find_resp.get("candidates") or []
        if not candidates:
            return {
                "name": place_name,
                "opening_hours": "See venue website for exact hours.",
                "photos_url": "",
                "tips": [
                    "Could not fetch live details; consider checking their website.",
                ],
                "website": "",
                "phone": "",
            }

        place_id = candidates[0]["place_id"]
        details = client.place(place_id=place_id, fields=["opening_hours", "photos", "website", "formatted_phone_number"])
        result = details.get("result", {})

        opening_hours = "See venue website for exact hours."
        if "opening_hours" in result and result["opening_hours"].get("weekday_text"):
            opening_hours = "; ".join(result["opening_hours"]["weekday_text"])

        photos_url = ""
        photos = result.get("photos")
        if photos:
            photos_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photos[0]['photo_reference']}"

        return {
            "name": result.get("name", place_name),
            "opening_hours": opening_hours,
            "photos_url": photos_url,
            "tips": [
                "Consider booking ahead if visiting during peak hours.",
                "Use this stop as a chance to take photos together.",
            ],
            "website": result.get("website", ""),
            "phone": result.get("formatted_phone_number", ""),
        }
    except Exception as exc:  # pragma: no cover - network / API failures
        mock = {
            "name": place_name,
            "opening_hours": "See venue website for exact hours.",
            "photos_url": "",
            "tips": [
                "Could not fetch live details; consider checking their website.",
            ],
            "website": "",
            "phone": "",
        }
        return {"error": str(exc), "fallback": True, **mock}

