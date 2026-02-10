# -*- coding: utf-8 -*-
"""
Basic tests for DateMate AI agents wiring.
"""

from datemate.agent import (
    root_agent,
    weather_agent,
    activity_agent,
    restaurant_agent,
    transport_agent,
    budget_agent,
    itinerary_agent,
    research_phase,
    planning_phase,
    refinement_loop,
)


def test_root_agent_structure():
    assert root_agent is not None
    assert research_phase in root_agent.sub_agents
    assert planning_phase in root_agent.sub_agents


def test_research_phase_agents():
    names = {a.name for a in research_phase.sub_agents}
    assert "WeatherAgent" in names
    assert "ActivityAgent" in names
    assert "RestaurantAgent" in names


def test_planning_phase_agents():
    names = {a.name for a in planning_phase.sub_agents}
    assert "TransportAgent" in names
    assert "BudgetAgent" in names
    assert "ItineraryAgent" in names


def test_loop_wraps_root_agent():
    assert refinement_loop.sub_agents[0] is root_agent

