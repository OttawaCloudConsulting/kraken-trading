"""Main entry point for the Kraken Trading Dashboard (Streamlit UI)."""

from utils.config import mongo_uri
import streamlit as st
# from utils.mongo_client import get_mongo_client
from utils.mongo_client import MongoDBClient

# Placeholder view imports — to be implemented in future steps
# from views.dashboard import render_dashboard
# from views.trades import render_trades_view
# from views.rewards import render_rewards_view
# from views.settings import render_settings_view

def main():
    # Initialize Kraken API Client and MongoDB Client
    # MONGO_URI = mongo_uri()

    """Launches the Streamlit frontend with navigation and MongoDB connection."""
    st.set_page_config(page_title="Kraken Trading Dashboard", layout="wide")
    st.title("📊 Kraken Trading Dashboard")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ("Dashboard", "Trades", "Rewards", "Settings")
    )

    # Initialize MongoDB client
    # mongo_client = get_mongo_client()
    mongo_client = MongoDBClient()

    # Route to selected page
    if page == "Dashboard":
        st.subheader("📈 Dashboard Overview")
        st.info("Dashboard view not yet implemented.")
        # render_dashboard(mongo_client)
    elif page == "Trades":
        st.subheader("💹 Trades Viewer")
        st.info("Trades view not yet implemented.")
        # render_trades_view(mongo_client)
    elif page == "Rewards":
        st.subheader("🎁 Staking Rewards Viewer")
        st.info("Rewards view not yet implemented.")
        # render_rewards_view(mongo_client)
    elif page == "Settings":
        st.subheader("⚙️ Settings & Manual Triggers")
        st.info("Settings view not yet implemented.")
        # render_settings_view(mongo_client)

if __name__ == "__main__":
    main()