# -*- coding: utf-8 -*-
"""
Budget tools for DateMate AI.

These tools compute total date costs, check budget compliance, and produce
friendly alternative suggestions when the plan is over budget.
"""

from typing import Dict, Any, List

try:
    from google.adk.tools import Tool  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback if ADK Tool is unavailable
    def Tool(func):  # type: ignore[override]
        """Fallback no-op decorator when google.adk.tools.Tool is missing."""
        return func


@Tool
def calculate_total_cost(
    activities: List[Dict[str, Any]],
    restaurant: Dict[str, Any],
    transport_extra: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate the total estimated cost for the date.

    This tool:
    - Sums prices of all activities for two people.
    - Uses `price_per_person` from the restaurant for two people plus a 15% tip.
    - Adds any additional transport costs.

    Args:
        activities: List of activities; each should include a `price` field
            representing cost for two people.
        restaurant: Restaurant info including `price_per_person`.
        transport_extra: Additional estimated amount for transit, parking, etc.

    Returns:
        A dict with:
        - breakdown: {
            "activities": float,
            "restaurant": float,
            "tip": float,
            "transport": float,
        }
        - subtotal: float
        - total: float
        - per_person: float
        - currency: "CAD"
    """
    activities_cost = float(sum(float(a.get("price", 0.0)) for a in activities))
    price_per_person = float(restaurant.get("price_per_person", 0.0))
    restaurant_cost = price_per_person * 2
    tip = restaurant_cost * 0.15
    transport_cost = float(transport_extra)

    subtotal = activities_cost + restaurant_cost
    total = subtotal + tip + transport_cost
    per_person = total / 2.0 if total > 0 else 0.0

    return {
        "breakdown": {
            "activities": round(activities_cost, 2),
            "restaurant": round(restaurant_cost, 2),
            "tip": round(tip, 2),
            "transport": round(transport_cost, 2),
        },
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
        "per_person": round(per_person, 2),
        "currency": "CAD",
    }


@Tool
def check_budget_compliance(total: float, budget: float) -> Dict[str, Any]:
    """
    Check whether the total cost fits within the user's budget.

    This tool categorizes the status as:
    - within_budget: comfortably under budget
    - close: near the budget limit but acceptable
    - over_budget: exceeds budget

    Args:
        total: Total estimated cost for the date.
        budget: User-specified budget limit.

    Returns:
        A dict with:
        - status: "within_budget" | "close" | "over_budget"
        - message: human-friendly explanation
        - remaining: budget minus total (may be negative)
        - percentage_used: float 0–100+
        - emoji: str representing the situation mood
    """
    remaining = budget - total
    percentage_used = (total / budget * 100.0) if budget > 0 else 100.0

    if remaining >= budget * 0.2:
        status = "within_budget"
        emoji = "✅"
        message = "Comfortably within budget with room for extras."
    elif remaining >= 0:
        status = "close"
        emoji = "⚠️"
        message = "Very close to your budget; consider keeping some buffer."
    else:
        status = "over_budget"
        emoji = "❌"
        message = "This plan is above your budget; consider adjusting activities or restaurant."

    return {
        "status": status,
        "message": message,
        "remaining": round(remaining, 2),
        "percentage_used": round(percentage_used, 1),
        "emoji": emoji,
    }


@Tool
def suggest_alternatives(
    current_cost: float,
    budget: float,
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Suggest concrete ways to reduce the date cost while keeping it special.

    This tool analyzes the difference between `current_cost` and `budget` and
    proposes a few high-impact adjustments.

    Args:
        current_cost: Current total estimated cost.
        budget: User's desired budget.
        plan: High-level plan dictionary, which may include activities and restaurant.

    Returns:
        A dict with:
        - alternatives: list of up to 3 suggestions, each:
            {
                "category": str,
                "suggestion": str,
                "estimated_savings": float,
                "impact_on_experience": str,
            }
        - total_possible_savings: float
    """
    over_amount = max(0.0, current_cost - budget)
    alternatives: List[Dict[str, Any]] = []

    # 1) Swap premium activity for free/low-cost outdoor walk
    alternatives.append(
        {
            "category": "activities",
            "suggestion": "Swap a premium paid activity for a free scenic walk or viewpoint.",
            "estimated_savings": round(over_amount * 0.4 if over_amount else 20.0, 2),
            "impact_on_experience": "Keeps things romantic while lowering structured costs.",
        }
    )

    # 2) Choose a slightly less expensive restaurant
    alternatives.append(
        {
            "category": "restaurant",
            "suggestion": "Choose a slightly more casual restaurant or share dishes.",
            "estimated_savings": round(over_amount * 0.4 if over_amount else 30.0, 2),
            "impact_on_experience": "Still a cozy dinner, just with a lighter bill.",
        }
    )

    # 3) Reduce transport costs
    alternatives.append(
        {
            "category": "transport",
            "suggestion": "Walk or take transit instead of rideshare where feasible.",
            "estimated_savings": round(over_amount * 0.2 if over_amount else 10.0, 2),
            "impact_on_experience": "More time side by side, less time sitting in traffic.",
        }
    )

    total_possible_savings = round(
        sum(a["estimated_savings"] for a in alternatives),
        2,
    )

    return {
        "alternatives": alternatives,
        "total_possible_savings": total_possible_savings,
        "note": "The best dates are about the company, not the cost 💕",
        "plan_snapshot": {
            "current_cost": current_cost,
            "budget": budget,
        },
    }

