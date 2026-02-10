![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Google ADK](https://img.shields.io/badge/Google%20ADK-Agents-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## DateMate AI 🌹

DateMate AI is a **multi-agent date planning system** built with the **Google Agent Development Kit (ADK)**.  
It coordinates specialized AI agents to research weather, activities, restaurants, transport, and budget, and then builds a **complete, romantic date itinerary**.

### Architecture

```text
              refinement_loop (LoopAgent, max_iterations=3)
                              │
                        root_agent (Sequential)
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
 research_phase (Parallel)                 planning_phase (Sequential)
        │                                           │
  ┌─────┼───────────────┐                 ┌────────┴───────────────┐
  │     │               │                 │        │               │
WeatherAgent     ActivityAgent     RestaurantAgent  TransportAgent  BudgetAgent  ItineraryAgent
 (LlmAgent)        (LlmAgent)         (LlmAgent)      (LlmAgent)     (LlmAgent)    (LlmAgent)
```

### Quick Start

```bash
git clone <your-repo-url>
cd datemate
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run with Google ADK (CLI):

```bash
adk run datemate
```

Run the ADK web UI:

```bash
adk web datemate
```

Run the Streamlit UI:

```bash
streamlit run app.py
```

### Agents

| Agent Name          | Type             | Purpose                                             | Tools Used                                   |
|---------------------|------------------|-----------------------------------------------------|----------------------------------------------|
| WeatherAgent        | LlmAgent         | Fetch and interpret weather for the date           | `get_weather_forecast`, `get_sunset_time`    |
| ActivityAgent       | LlmAgent         | Propose activities based on prefs & weather        | `search_activities`, `get_activity_details`  |
| RestaurantAgent     | LlmAgent         | Pick the best romantic restaurant                  | `search_restaurants`, `check_reservation`    |
| TransportAgent      | LlmAgent         | Plan routes between all locations                  | `calculate_route`, `optimize_route`          |
| BudgetAgent         | LlmAgent         | Ensure the plan stays within budget                | `calculate_total_cost`, `check_budget_compliance`, `suggest_alternatives` |
| ItineraryAgent      | LlmAgent         | Generate the final, formatted itinerary            | (uses context only)                          |
| ResearchPhase       | ParallelAgent    | Run weather, activity, and restaurant in parallel  | sub-agents                                   |
| PlanningPhase       | SequentialAgent  | Transport → Budget → Itinerary                     | sub-agents                                   |
| DatePlannerCoordinator | SequentialAgent | Orchestrate the whole planning flow              | sub-agents                                   |
| RefinementLoop      | LoopAgent        | Optional refinement over multiple user turns       | `root_agent` as sub-agent                    |

### Environment & APIs

See `.env.example` for environment variables:

- **Google Cloud / Vertex AI** via `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
- Or **Google AI Studio** key via `GOOGLE_API_KEY`
- Optional external APIs:
  - `GOOGLE_PLACES_API_KEY` for activities and restaurants
  - `GOOGLE_MAPS_API_KEY` for transport routes
  - `OPENWEATHER_API_KEY` for weather forecasting

All tools implement **graceful fallback**: if an API key is not provided, they return **realistic mock data** so that tests and local development still work.

### Example Input

> Location: Vancouver, BC  
> Date: 2026-02-14 at 17:00  
> Budget: $150 for two  
> Preferences: Art & Museums, Outdoors & Nature  
> Cuisine: Italian  
> Dietary: Vegetarian

### Example Output (Excerpt)

> 🌹 **“An Artsy Evening in Vancouver”**  
> 🌤️ *Weather:* Partly cloudy, 10°C — ideal for an evening stroll by the water.  
> 5:00 PM – 🎨 Vancouver Art Gallery (90 min, $30 for 2)  
> 6:45 PM – 🚶 Walk to dinner (0.7 km, 9 min) – perfect moment for holding hands  
> 7:00 PM – 🍝 La Pentola (2 hours, ~$95 for 2) – cozy Italian with great vegetarian options  
> 9:15 PM – 🌊 English Bay Beach (45 min, free) – catch the last light over the ocean  
> 💰 Total: $135 / $150 ✅  

### Development

Run tests:

```bash
pytest tests/ -v
```

DateMate AI is designed to be **production-ready** with clear separation between agents, tools, and UI, and follows **Google ADK** best practices.

