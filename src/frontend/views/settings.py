"""Settings and Manual Triggers for Kraken Trade UI."""

import streamlit as st
import requests


def render_settings() -> None:
    """Render the settings view, including manual sync triggers."""
    st.title("⚙️ Settings & Manual Sync")

    st.subheader("Manually Update Feeds")

    st.write(
        "Use the button below to manually trigger the trade and staking reward sync process."
    )

    trigger_url = st.text_input(
        "Trigger Endpoint URL",
        placeholder="https://your-api-service/trigger-sync",
        help="This should point to an endpoint exposed by your backend to trigger sync.",
    )

    if st.button("Update Feeds Now"):
        if not trigger_url:
            st.warning("Please enter a valid trigger URL.")
            return

        try:
            response = requests.post(trigger_url, timeout=10)
            if response.status_code == 200:
                st.success("✅ Sync triggered successfully.")
            else:
                st.error(f"❌ Failed to trigger sync: {response.status_code}")
        except requests.RequestException as e:
            st.error(f"❌ Error occurred: {str(e)}")