"""Main entry point for the Kraken Trading Dashboard (Streamlit UI)."""

from utils.config import mongo_uri
import streamlit as st
from utils.mongo_client import MongoDBClient

# Placeholder view imports — to be implemented in future steps
from views.dashboard import render_dashboard
from views.trades import render_trades
from views.rewards import render_rewards
from views.settings import render_settings
from views.alltrades import render_alltrades

def main():

    """Launches the Streamlit frontend with navigation and MongoDB connection."""
    st.set_page_config(page_title="Kraken Trading Dashboard", layout="wide")
    st.title("📊 Kraken Trading Dashboard")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ("Dashboard", "Trades", "All Trades", "Rewards", "Settings")
    )

    # Initialize MongoDB client
    mongo_client = MongoDBClient()

    # Route to selected page
    if page == "Dashboard":
        st.subheader("📈 Dashboard Overview")
        st.info("Dashboard view")
        render_dashboard()
    elif page == "Trades":
        st.subheader("💹 Trades Viewer")
        st.info("Trades view")
        render_trades()
    elif page == "All Trades":
        st.subheader("💹 All Trades Viewer")
        st.info("All Trades view")
        render_alltrades()
    elif page == "Rewards":
        st.subheader("🎁 Staking Rewards Viewer")
        st.info("Rewards view")
        render_rewards()
    elif page == "Settings":
        st.subheader("⚙️ Settings & Manual Triggers")
        st.info("Settings view")
        render_settings()

if __name__ == "__main__":
    main()