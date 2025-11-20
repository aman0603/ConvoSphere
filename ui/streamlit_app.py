import streamlit as st
import requests
import json
import os

# --- Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000") # Ensure your FastAPI is running

st.set_page_config(layout="wide", page_title="ConvoSphere - Sales Intelligence")

# --- Helper Functions ---
def post_new_session(name, phone, context, goal, owner_id):
    url = f"{API_BASE_URL}/api/sessions"
    payload = {
        "name": name,
        "phone": phone,
        "context": context,
        "goal": goal,
        "owner_id": owner_id,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        if response is not None:
            st.error(f"Response: {response.text}")
        return None

# --- Streamlit UI ---
st.title("🚀 ConvoSphere: Sales Intelligence System")

# Sidebar for navigation or other controls
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Start New Conversation", "Sessions List (Coming Soon)"])

if page == "Start New Conversation":
    st.header("Start a New Sales Conversation")

    with st.form("new_conversation_form"):
        st.subheader("Customer Details")
        name = st.text_input("Customer Name", help="Full name of the prospect.")
        phone = st.text_input("Customer Phone", help="Phone number with country code (e.g., +1234567890).")
        context = st.text_area("Customer Context", help="Brief background or any known information about the prospect.")
        goal = st.text_input("Conversation Goal", help="What do you aim to achieve with this conversation? (e.g., Sell DSA course, Schedule demo).")
        owner_id = st.text_input("Your Agent ID", value="sales_agent_001", help="Your unique ID as a sales agent.")

        submitted = st.form_submit_button("Start Conversation")

        if submitted:
            if not all([name, phone, context, goal, owner_id]):
                st.error("Please fill in all fields.")
            else:
                st.info("Creating new session...")
                new_session_data = post_new_session(name, phone, context, goal, owner_id)
                if new_session_data:
                    st.success(f"Session created successfully! Session ID: **{new_session_data['session_id']}**")
                    st.json(new_session_data) # Display raw session data for now
                    st.subheader("Session Overview (Coming Soon)")
                    st.write("This area will show the full session details, messages, and intelligence.")
                else:
                    st.error("Failed to create session. Check API logs.")

elif page == "Sessions List (Coming Soon)":
    st.header("Your Active Sales Sessions")
    st.write("This page will list all your active sales sessions and provide quick insights.")
    st.info("Feature under development.")
