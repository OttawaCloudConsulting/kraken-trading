"""Staking Rewards view for Kraken Trade History UI."""

import streamlit as st
from utils.mongo_client import get_collection


def render_rewards(mongo_uri: str, db_name: str) -> None:
    """Render the Staking Rewards view and allow export of data from MongoDB.

    Args:
        mongo_uri: Connection URI for MongoDB.
        db_name: Name of the database containing reward data.
    """
    st.title("🏆 Staking Rewards")

    collection = get_collection(mongo_uri, db_name, "kraken_rewards")
    if collection is None:
        st.error("Unable to connect to MongoDB or find the 'kraken_rewards' collection.")
        return

    documents = list(collection.find())
    if not documents:
        st.warning("No reward data available in MongoDB.")
        return

    st.success(f"Retrieved {len(documents)} staking reward records.")

    # Preview a few records
    st.subheader("Sample Records")
    st.json(documents[:5])

    # Download options
    st.subheader("Download Staking Reward Data")

    export_format = st.selectbox("Select export format:", ["JSON", "CSV"])

    if st.button("Download"):
        if export_format == "JSON":
            st.download_button(
                label="Download JSON",
                data=str(documents).encode("utf-8"),
                file_name="kraken_rewards.json",
                mime="application/json",
            )
        else:
            import pandas as pd

            df = pd.DataFrame(documents).drop(columns=["_id"], errors="ignore")
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name="kraken_rewards.csv",
                mime="text/csv",
            )