# -*- coding: utf-8 -*-
"""
Transport tools for DateMate AI.

These tools estimate walking or driving routes between locations, using Google
Maps when available or realistic heuristics when offline.
"""

import hashlib
import os
from typing import Dict, Any, List

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


def _estimate_distance_km(origin: str, destination: str) -> float:
    """Generate a deterministic pseudo-random distance based on inputs."""
    h = hashlib.sha256(f"{origin}-{destination}".encode("utf-8")).hexdigest()
    # Map hash to 0.3–3.0 km
    value = int(h[:8], 16) / 0xFFFFFFFF
    return round(0.3 + value * (3.0 - 0.3), 2)


def _romantic_tip(mode: str, distance_km: float) -> str:
    """Return a romantic tip string based on mode and distance."""
    if mode == "walking":
        if distance_km < 0.5:
            return "A perfect short stroll 💬"
        if distance_km <= 1.5:
            return "Lovely walk — perfect for conversation 🤝"
        return "Scenic walk if weather permits, or take transit"
    if mode == "driving":
        return "Great excuse for a music playlist 🎵"
    return "Use the travel time to share stories and plans for future adventures."


@Tool
def calculate_route(origin: str, destination: str, mode: str = "walking") -> Dict[str, Any]:
    """
    Calculate an approximate route between two locations.

    This tool:
    - Uses Google Maps Directions API when `GOOGLE_MAPS_API_KEY` is configured,
      returning realistic distance, duration, and navigation steps.
    - Falls back to a deterministic heuristic that produces plausible distances
      and times for walking or driving when offline.

    Args:
        origin: Starting location (name or address).
        destination: Destination location (name or address).
        mode: Transport mode, typically "walking" or "driving".

    Returns:
        A dict with:
        - origin, destination, mode
        - distance_km: float
        - duration_minutes: float
        - duration_text: str
        - steps: list[str] of simple navigation instructions
        - romantic_tip: str
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key or googlemaps is None:
        distance_km = _estimate_distance_km(origin, destination)
        if mode == "walking":
            minutes = distance_km / 4.5 * 60.0
        else:
            minutes = distance_km / 25.0 * 60.0
        duration_minutes = max(3, round(minutes))
        duration_text = f"{int(duration_minutes)} mins"
        steps = [
            f"Start at {origin}",
            f"Head towards {destination}",
            f"Arrive at {destination}",
        ]
        tip = _romantic_tip(mode, distance_km)
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_km": round(distance_km, 2),
            "duration_minutes": duration_minutes,
            "duration_text": duration_text,
            "steps": steps,
            "romantic_tip": tip,
        }

    try:
        client = googlemaps.Client(key=api_key)
        directions = client.directions(origin=origin, destination=destination, mode=mode)
        if not directions:
            raise ValueError("No directions returned from Google Maps")

        leg = directions[0]["legs"][0]
        distance_km = leg["distance"]["value"] / 1000.0
        duration_minutes = leg["duration"]["value"] / 60.0
        duration_text = leg["duration"]["text"]
        steps: List[str] = []
        for step in leg.get("steps", []):
            # Use plain text instructions by stripping HTML tags crudely
            instructions = step.get("html_instructions", "")
            for tag in ["<b>", "</b>", "<div>", "</div>", "<br>", "<br/>"]:
                instructions = instructions.replace(tag, " ")
            steps.append(instructions.strip())

        tip = _romantic_tip(mode, distance_km)
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(duration_minutes, 1),
            "duration_text": duration_text,
            "steps": steps,
            "romantic_tip": tip,
        }
    except Exception as exc:  # pragma: no cover - network / API failures
        # Fallback to the same mock logic we use when there is no API key
        distance_km = _estimate_distance_km(origin, destination)
        if mode == "walking":
            minutes = distance_km / 4.5 * 60.0
        else:
            minutes = distance_km / 25.0 * 60.0
        duration_minutes = max(3, round(minutes))
        duration_text = f"{int(duration_minutes)} mins"
        steps = [
            f"Start at {origin}",
            f"Head towards {destination}",
            f"Arrive at {destination}",
        ]
        tip = _romantic_tip(mode, distance_km)
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_km": round(distance_km, 2),
            "duration_minutes": duration_minutes,
            "duration_text": duration_text,
            "steps": steps,
            "romantic_tip": tip,
            "error": str(exc),
            "fallback": True,
        }

@Tool
def optimize_route(locations: List[str]) -> Dict[str, Any]:
    """
    Build an optimized multi-leg route for a list of locations.

    This tool calls `calculate_route` sequentially for each consecutive pair
    of locations, aggregating total distance and travel time.

    Args:
        locations: Ordered list of location names or addresses.

    Returns:
        A dict with:
        - legs: list of per-leg route dicts as returned by `calculate_route`
        - total_distance_km: float
        - total_time_minutes: float
        - summary: str human-friendly summary of travel effort.
    """
    legs: List[Dict[str, Any]] = []
    total_distance = 0.0
    total_minutes = 0.0

    for i in range(len(locations) - 1):
        origin = locations[i]
        dest = locations[i + 1]
        route = calculate_route(origin, dest, mode="walking")
        legs.append(route)
        total_distance += float(route.get("distance_km", 0.0))
        total_minutes += float(route.get("duration_minutes", 0.0))

    summary = (
        f"Approx. {round(total_distance, 1)} km total walking over "
        f"{int(total_minutes)} minutes across {len(legs)} legs."
    )

    return {
        "legs": legs,
        "total_distance_km": round(total_distance, 2),
        "total_time_minutes": round(total_minutes, 1),
        "summary": summary,
    }

