"""Dashboard view for Kraken Trade History UI."""

import streamlit as st


def render_dashboard() -> None:
    """Render the main dashboard page."""
    st.title("📊 Kraken Trading Dashboard")
    st.markdown("Welcome to the Kraken Trade History and Staking Rewards Viewer.")
    st.markdown(
        """
        This application provides:
        - Full historical trade records.
        - Staking reward history.
        - CSV/JSON data export.
        - Manual data synchronization.
        """
    )

    st.info(
        "Use the sidebar to navigate to different sections: Trades, Rewards, or Settings."
    )