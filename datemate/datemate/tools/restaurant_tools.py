# -*- coding: utf-8 -*-
"""
Restaurant tools for DateMate AI.

These tools search for romantic restaurants and simulate reservation checks,
using Google Places where possible and otherwise returning curated mock data.
"""

import os
from typing import Dict, List, Any, Optional

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


def _mock_restaurants(location: str, cuisine_type: str) -> Dict[str, Any]:
    """Return mock restaurant data for common cuisines."""
    base: List[Dict[str, Any]] = [
        {
            "name": "La Pentola",
            "cuisine": "Italian",
            "address": "350 Davie St, Vancouver, BC",
            "price_per_person": 45,
            "rating": 4.6,
            "atmosphere": "Cozy, candle-lit, intimate",
            "reservation_required": True,
            "romantic_score": 9,
            "specialties": ["Fresh pasta", "Seafood", "Tiramisu"],
            "dietary_options": ["Vegetarian"],
        },
        {
            "name": "Yuwa Japanese Cuisine",
            "cuisine": "Japanese",
            "address": "2775 W 16th Ave, Vancouver, BC",
            "price_per_person": 55,
            "rating": 4.7,
            "atmosphere": "Elegant, quiet, refined",
            "reservation_required": True,
            "romantic_score": 9,
            "specialties": ["Omakase", "Sashimi", "Sake"],
            "dietary_options": ["Gluten-free", "Pescatarian"],
        },
        {
            "name": "L'Abattoir",
            "cuisine": "French",
            "address": "217 Carrall St, Vancouver, BC",
            "price_per_person": 60,
            "rating": 4.6,
            "atmosphere": "Brick-and-glass, chic, candle-lit",
            "reservation_required": True,
            "romantic_score": 9,
            "specialties": ["French-inspired West Coast", "Cocktails"],
            "dietary_options": ["Vegetarian"],
        },
        {
            "name": "Hawksworth Restaurant",
            "cuisine": "Modern Canadian",
            "address": "801 W Georgia St, Vancouver, BC",
            "price_per_person": 70,
            "rating": 4.6,
            "atmosphere": "Upscale, modern, special-occasion",
            "reservation_required": True,
            "romantic_score": 9,
            "specialties": ["Seasonal tasting menus"],
            "dietary_options": ["Vegetarian", "Gluten-free"],
        },
        {
            "name": "La Mezcaleria",
            "cuisine": "Mexican",
            "address": "1622 Commercial Dr, Vancouver, BC",
            "price_per_person": 35,
            "rating": 4.5,
            "atmosphere": "Lively, colourful, fun date spot",
            "reservation_required": False,
            "romantic_score": 8,
            "specialties": ["Tacos", "Mezcal flights"],
            "dietary_options": ["Vegetarian", "Gluten-free"],
        },
    ]

    if cuisine_type.lower() == "surprise me!":
        filtered = base
    else:
        filtered = [r for r in base if r["cuisine"].lower() == cuisine_type.lower()]
        if not filtered:
            filtered = base

    return {"restaurants": filtered[:4], "total_found": len(filtered)}


@Tool
def search_restaurants(
    location: str,
    cuisine_type: str,
    max_price_per_person: int,
    dietary_restrictions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Search for romantic restaurants within a price range and dietary constraints.

    This tool:
    - Uses Google Places (if `GOOGLE_PLACES_API_KEY` is set) to search nearby restaurants
      that match the cuisine and budget.
    - Falls back to curated mock data when no API key is available.

    Args:
        location: Area to search around (e.g., "Vancouver, BC").
        cuisine_type: Cuisine preference (e.g., "Italian").
        max_price_per_person: Maximum acceptable price per person.
        dietary_restrictions: Optional list of dietary restrictions
            (e.g., ["Vegetarian", "Gluten-free"]).

    Returns:
        A dict containing:
        - restaurants: list of up to 4 restaurants, each:
            {
                "name", "cuisine", "address", "price_per_person", "rating",
                "atmosphere", "reservation_required", "romantic_score",
                "specialties", "dietary_options"
            }
        - total_found: total number matched before trimming.
    """
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key or googlemaps is None:
        base = _mock_restaurants(location, cuisine_type)
        # Filter by budget
        filtered = [
            r for r in base["restaurants"] if r["price_per_person"] <= max_price_per_person
        ]
        return {"restaurants": filtered[:4], "total_found": len(filtered)}

    try:
        client = googlemaps.Client(key=api_key)
        keyword = f"{cuisine_type} restaurant"
        response = client.places_nearby(
            location=location,
            radius=4000,
            type="restaurant",
            keyword=keyword,
        )
        restaurants: List[Dict[str, Any]] = []
        for place in response.get("results", []):
            price_level = place.get("price_level", 2)
            price = max(1, min(4, price_level)) * 15
            if price > max_price_per_person:
                continue
            restaurants.append(
                {
                    "name": place.get("name"),
                    "cuisine": cuisine_type,
                    "address": place.get("vicinity") or location,
                    "price_per_person": price,
                    "rating": place.get("rating", 4.3),
                    "atmosphere": "Romantic, cozy atmosphere",
                    "reservation_required": price > 40,
                    "romantic_score": 8,
                    "specialties": [cuisine_type],
                    "dietary_options": dietary_restrictions or ["None"],
                }
            )

        if not restaurants:
            base = _mock_restaurants(location, cuisine_type)
            filtered = [
                r for r in base["restaurants"] if r["price_per_person"] <= max_price_per_person
            ]
            if not filtered:
                filtered = base["restaurants"]
            return {"restaurants": filtered[:4], "total_found": len(filtered)}

        restaurants = sorted(restaurants, key=lambda r: (-r["romantic_score"], -r["rating"]))[
            :4
        ]
        return {"restaurants": restaurants, "total_found": len(restaurants)}
    except Exception as exc:  # pragma: no cover - network / API failures
        base = _mock_restaurants(location, cuisine_type)
        filtered = [
        r for r in base["restaurants"] if r["price_per_person"] <= max_price_per_person
        ]
        return {
            "error": str(exc),
            "fallback": True,
            "restaurants": filtered[:4],
            "total_found": len(filtered),
        }


@Tool
def check_reservation(
    restaurant_name: str,
    date: str,
    time: str,
    party_size: int = 2,
) -> Dict[str, Any]:
    """
    Simulate a reservation check for a restaurant.

    This tool does not perform real bookings; instead it returns a plausible
    availability schedule with helpful notes and a mock booking URL. It is
    designed for reasoning inside the agent and for user-facing explanations.

    Args:
        restaurant_name: Name of the restaurant to check.
        date: Target date in ISO format (YYYY-MM-DD).
        time: Desired time (e.g., "19:00").
        party_size: Number of guests for the reservation.

    Returns:
        A dict with keys:
        - available: bool indicating if the requested time is available.
        - available_times: list of alternative time strings.
        - booking_url: URL string to a mock or real booking page.
        - notes: Human-friendly notes on how likely a booking is.
    """
    # Simple heuristic: if time ends with ":00" or ":30", mark as available
    is_available = time.endswith(":00") or time.endswith(":30")
    alternatives = ["18:00", "18:30", "19:00", "19:30", "20:00"]
    if is_available and time in alternatives:
        alternatives.remove(time)

    notes = (
        "Good availability for this time; still recommend booking a few days in advance."
        if is_available
        else "Requested time may be busy; consider one of the suggested alternatives."
    )

    return {
        "available": is_available,
        "available_times": alternatives,
        "booking_url": f"https://example.com/reserve?restaurant={restaurant_name.replace(' ', '%20')}",
        "notes": notes,
        "date": date,
        "time": time,
        "party_size": party_size,
    }

