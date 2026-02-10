# -*- coding: utf-8 -*-
"""
Tests for DateMate AI tools.
"""

from datemate.tools.activity_tools import search_activities
from datemate.tools.restaurant_tools import search_restaurants
from datemate.tools.weather_tools import get_weather_forecast
from datemate.tools.transport_tools import calculate_route
from datemate.tools.budget_tools import calculate_total_cost, check_budget_compliance


def test_search_activities_returns_list():
    result = search_activities("Vancouver, BC", ["art"], "2026-02-15")
    assert "activities" in result
    assert isinstance(result["activities"], list)
    assert len(result["activities"]) > 0
    assert "name" in result["activities"][0]
    assert "price" in result["activities"][0]


def test_restaurant_respects_budget():
    result = search_restaurants("Vancouver, BC", "Italian", max_price_per_person=30)
    for r in result["restaurants"]:
        assert r["price_per_person"] <= 30


def test_weather_forecast_structure():
    result = get_weather_forecast("Vancouver, BC", "2026-02-15")
    assert "condition" in result
    assert "temperature_c" in result
    assert "recommendations" in result
    assert "date_friendliness_score" in result
    assert 0 <= result["date_friendliness_score"] <= 10


def test_route_calculation():
    result = calculate_route("Vancouver Art Gallery", "La Pentola", "walking")
    assert "duration_minutes" in result
    assert "distance_km" in result
    assert result["duration_minutes"] > 0


def test_budget_within_limit():
    activities = [{"price": 15}, {"price": 0}]
    restaurant = {"price_per_person": 40}
    result = calculate_total_cost(activities, restaurant)
    assert result["total"] > 0
    compliance = check_budget_compliance(result["total"], 150)
    assert compliance["status"] in ["within_budget", "close", "over_budget"]


def test_over_budget_detection():
    result = check_budget_compliance(200, 150)
    assert result["status"] == "over_budget"
    assert result["remaining"] < 0

