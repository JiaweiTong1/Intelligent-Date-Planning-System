# -*- coding: utf-8 -*-
"""
DateMate AI - Multi-Agent Date Planning System
Built with Google Agent Development Kit (ADK).
"""

import os

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent

from datemate.tools.activity_tools import search_activities, get_activity_details
from datemate.tools.restaurant_tools import search_restaurants, check_reservation
from datemate.tools.weather_tools import get_weather_forecast, get_sunset_time
from datemate.tools.transport_tools import calculate_route, optimize_route
from datemate.tools.budget_tools import (
    calculate_total_cost,
    check_budget_compliance,
    suggest_alternatives,
)


MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


# ─────────────────────────────────────────────────
# RESEARCH PHASE — run in parallel for speed
# ─────────────────────────────────────────────────

weather_agent = LlmAgent(
    name="WeatherAgent",
    model=MODEL,
    description="Checks weather forecast and provides clothing + activity recommendations",
    instruction="""
    You are a weather expert helping plan the perfect outdoor/indoor date experience.

    When given a location and date:
    1. Call get_weather_forecast() with the location and date
    2. Optionally call get_sunset_time() if the date is suitable for evening outdoor activity
    3. Summarize:
       - Temperature and conditions
       - Whether to plan indoor vs outdoor activities
       - Clothing recommendations
       - Any special notes (e.g., "perfect for sunset walk at 5:45 PM")

    Be concise, practical, and add a romantic touch when weather permits.
    """,
    tools=[get_weather_forecast, get_sunset_time],
    output_key="weather_info",
)

activity_agent = LlmAgent(
    name="ActivityAgent",
    model=MODEL,
    description="Suggests creative and romantic date activities matching preferences",
    instruction="""
    You are an expert at planning memorable date activities.

    Context available:
    - Weather info: {weather_info?}

    When given preferences, location, date, and budget:
    1. Call search_activities() with the user's preferences and location
    2. If weather is bad (from weather_info), filter to indoor options
    3. Select the TOP 2 best activities considering:
       - Romantic atmosphere
       - Preference match
       - Weather appropriateness
       - Budget fit
       - Logical timing (e.g., art gallery before dinner)
    4. For each activity, call get_activity_details() for extra info

    Output a clear list: name, address, duration, cost, why it's romantic.
    """,
    tools=[search_activities, get_activity_details],
    output_key="selected_activities",
)

restaurant_agent = LlmAgent(
    name="RestaurantAgent",
    model=MODEL,
    description="Finds the best restaurant matching cuisine preference, budget, and vibe",
    instruction="""
    You are a restaurant expert specializing in romantic dining experiences.

    When given cuisine type, location, and budget:
    1. Call search_restaurants() with the criteria
    2. Call check_reservation() on the top 2 picks
    3. Select the BEST ONE based on:
       - Romantic atmosphere (highest priority)
       - Cuisine match
       - Price fits budget
       - Good reviews
       - Reservation availability

    Output: restaurant name, address, price estimate for 2, reservation info, and why it's perfect.
    """,
    tools=[search_restaurants, check_reservation],
    output_key="selected_restaurant",
)


# ─────────────────────────────────────────────────
# PLANNING PHASE — run sequentially (order matters)
# ─────────────────────────────────────────────────

transport_agent = LlmAgent(
    name="TransportAgent",
    model=MODEL,
    description="Plans optimal routes between date locations",
    instruction="""
    You are a logistics expert who creates seamless date routes.

    Context available:
    - Activities: {selected_activities?}
    - Restaurant: {selected_restaurant?}
    - Weather: {weather_info?}

    For each pair of consecutive locations:
    1. Call calculate_route() between them
    2. Prefer walking for distances under 1.5km (more romantic)
    3. Use optimize_route() if there are 3+ stops

    Output: a clean list of each leg — from → to, distance, duration, transport mode, and a romantic tip.
    """,
    tools=[calculate_route, optimize_route],
    output_key="transport_plan",
)

budget_agent = LlmAgent(
    name="BudgetAgent",
    model=MODEL,
    description="Ensures the date stays within budget and suggests alternatives if needed",
    instruction="""
    You are a smart financial planner making sure dates are special AND affordable.

    Context available:
    - Activities: {selected_activities?}
    - Restaurant: {selected_restaurant?}

    Steps:
    1. Call calculate_total_cost() with all selected items
    2. Call check_budget_compliance() against the user's budget
    3. If OVER BUDGET: call suggest_alternatives() and revise the plan
    4. If UNDER BUDGET (good buffer): note how much is left for spontaneous extras

    Output: itemized cost breakdown, budget status (✅/⚠️/❌), and any adjustments made.
    Always include a warm note: "The best dates are about the company, not the cost 💕"
    """,
    tools=[calculate_total_cost, check_budget_compliance, suggest_alternatives],
    output_key="budget_summary",
)

itinerary_agent = LlmAgent(
    name="ItineraryAgent",
    model=MODEL,
    description="Creates the final beautiful, detailed date itinerary",
    instruction="""
    You are a master date planner. Your job is to combine everything into a perfect itinerary.

    Context available:
    - Weather: {weather_info?}
    - Activities: {selected_activities?}
    - Restaurant: {selected_restaurant?}
    - Transport: {transport_plan?}
    - Budget: {budget_summary?}

    Create a complete, emoji-rich itinerary with:
    - A romantic title for the date
    - Time-by-time schedule (start from the user's meeting time)
    - Each stop: time, place, emoji, address, duration, cost
    - Travel legs between stops with duration and mode
    - Weather note at the top
    - Budget summary at the bottom
    - One personalized romantic tip

    Format example:
    ---
    🌹 "An Artsy Evening in Vancouver"

    🌤️ Weather: Clear skies, 12°C — perfect for an evening stroll!

    5:00 PM  🎨 Vancouver Art Gallery
             750 Hornby St · 90 min · $30 for 2
             Contemporary exhibitions + stunning architecture

    6:45 PM  🚶 Walk to dinner (0.7km · 9 min)
             💬 Romantic tip: This is the perfect walk to hold hands

    7:00 PM  🍝 La Pentola della Quercia
             1983 Cornwall Ave · ~2 hrs · $95 for 2
             Award-winning Italian · intimate lighting · reserve ahead

    9:15 PM  🌊 English Bay Beach
             Beach Ave · 45 min · Free
             🌅 Catch the last light reflecting on the water

    💰 Total: $125 / $150 ✅  ($25 left for dessert or drinks!)
    ---

    Be warm, thoughtful, and make it feel special.
    """,
    output_key="final_itinerary",
)


# ─────────────────────────────────────────────────
# ORCHESTRATION
# ─────────────────────────────────────────────────

research_phase = ParallelAgent(
    name="ResearchPhase",
    description="Simultaneously gathers weather, activities, and restaurant options",
    sub_agents=[weather_agent, activity_agent, restaurant_agent],
)

planning_phase = SequentialAgent(
    name="PlanningPhase",
    description="Sequentially plans transport, checks budget, and builds itinerary",
    sub_agents=[transport_agent, budget_agent, itinerary_agent],
)

root_agent = SequentialAgent(
    name="DatePlannerCoordinator",
    description="""
    DateMate AI: Plans the perfect personalized date.

    Tell me:
    - Where you are (city/neighbourhood)
    - When (date + meeting time)
    - Budget (e.g., $150 for two)
    - Preferences (e.g., 'she loves art and Italian food')
    - Any dietary restrictions or constraints

    I'll coordinate 6 specialized agents to create your perfect date plan!
    """,
    sub_agents=[research_phase, planning_phase],
)

refinement_loop = LoopAgent(
    name="RefinementLoop",
    description="Refines the date plan based on user feedback (max 3 iterations)",
    max_iterations=3,
    sub_agents=[root_agent],
)

