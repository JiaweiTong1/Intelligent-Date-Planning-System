# -*- coding: utf-8 -*-
"""
Streamlit UI for DateMate AI.

This app provides a friendly interface over the Google ADK-powered
multi-agent system defined in `datemate.agent`.
"""

from datetime import time

import streamlit as st
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from datemate.agent import root_agent

from dotenv import load_dotenv
load_dotenv()


st.set_page_config(
    page_title="DateMate AI 🌹",
    page_icon="🌹",
    layout="centered",
)


# --- SIDEBAR: Input Form ---
with st.sidebar:
    st.title("🌹 DateMate AI")
    st.caption("Plan the perfect date with AI")

    location = st.text_input("📍 Location", placeholder="Vancouver, BC")
    date = st.date_input("📅 Date")
    meeting_time = st.time_input("⏰ Meeting Time", value=time(17, 0))
    budget = st.slider("💰 Budget (CAD, for two)", 50, 400, 150, step=10)

    preferences = st.multiselect(
        "🎨 Interests",
        [
            "Art & Museums",
            "Outdoors & Nature",
            "Food & Cooking",
            "Music & Concerts",
            "Sports & Active",
            "Movies & Theater",
            "Spa & Wellness",
            "Shopping",
            "Escape Rooms",
            "Comedy Shows",
        ],
        default=["Art & Museums"],
    )

    cuisine = st.selectbox(
        "🍽️ Favourite Cuisine",
        [
            "Italian",
            "Japanese",
            "French",
            "Modern Canadian",
            "Mexican",
            "Thai",
            "Indian",
            "Mediterranean",
            "Surprise me!",
        ],
    )

    dietary = st.multiselect(
        "🥗 Dietary Restrictions",
        ["Vegetarian", "Vegan", "Gluten-free", "Halal", "Kosher", "None"],
        default=["None"],
    )

    plan_button = st.button("✨ Plan My Date!", type="primary", use_container_width=True)


# --- MAIN: Display Plan ---
if plan_button:
    user_prompt = f"""
    Plan a romantic date with these details:
    - Location: {location}
    - Date: {date}
    - Meeting time: {meeting_time}
    - Budget: ${budget} CAD for two people
    - Activity preferences: {', '.join(preferences)}
    - Cuisine preference: {cuisine}
    - Dietary restrictions: {', '.join(dietary)}

    Please create a complete date plan!
    """

    with st.spinner("🤖 Agents are planning your perfect date..."):
        col1, col2, col3 = st.columns(3)
        col1.info("🌤️ Checking weather...")
        col2.info("🎨 Finding activities...")
        col3.info("🍽️ Scouting restaurants...")

        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name="datemate",
            session_service=session_service,
        )

        session = asyncio.run(
            session_service.create_session(
                app_name="datemate",
                user_id="user_1",
            )
        )

        response_text = ""
        for event in runner.run(
            user_id="user_1",
            session_id=session.id,
            new_message=Content(role="user", parts=[Part(text=user_prompt)]),
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        response_text += part.text

        col1.success("🌤️ Weather checked!")
        col2.success("🎨 Activities found!")
        col3.success("🍽️ Restaurant selected!")

    st.success("✅ Your perfect date is planned!")
    st.divider()
    st.markdown(response_text)
    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Regenerate Plan"):
            st.rerun()
    with c2:
        st.button("💰 Adjust Budget")
    with c3:
        st.download_button(
            "📥 Save Plan",
            data=response_text,
            file_name=f"date_plan_{date}.txt",
            mime="text/plain",
        )
else:
    st.title("🌹 DateMate AI")
    st.subheader("Plan the perfect date in 45 seconds")

    st.markdown(
        """
    **How it works:**

    1. 📝 Fill in your preferences on the left  
    2. ✨ Hit "Plan My Date!"  
    3. 🤖 6 AI agents work simultaneously:  
       - 🌤️ WeatherAgent checks forecast  
       - 🎨 ActivityAgent finds perfect activities  
       - 🍽️ RestaurantAgent picks the best spot  
       - 🚗 TransportAgent plans your route  
       - 💰 BudgetAgent keeps you on track  
       - 📅 ItineraryAgent creates your timeline  
    4. 🎉 Get a beautiful, personalized date plan!
    """
    )

    st.info(
        "**Multi-Agent Architecture** (Google ADK)\n\n"
        "ParallelAgent → [Weather + Activity + Restaurant]\n"
        "SequentialAgent → [Transport → Budget → Itinerary]"
    )

