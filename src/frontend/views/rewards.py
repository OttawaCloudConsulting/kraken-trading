"""Staking Rewards view for Kraken Trade History UI."""

import streamlit as st
import pandas as pd
from utils.mongo_client import MongoDBClient


def render_rewards() -> None:
    """Render the Staking Rewards view and allow export of data from MongoDB.

    Args:
        mongo_uri: Connection URI for MongoDB.
        db_name: Name of the database containing reward data.
    """
    st.title("🏆 Staking Rewards")

    client = MongoDBClient()
    collection = client.get_collection("kraken_rewards")
    if collection is None:
        st.error("Unable to connect to MongoDB or find the 'kraken_rewards' collection.")
        return

    documents = list(collection.find())
    if not documents:
        st.warning("No reward data available in MongoDB.")
        return

    st.success(f"Retrieved {len(documents)} staking reward records.")

    # 👉 Table Preview
    st.subheader("Table Preview")
    try:
        df = pd.DataFrame(documents)
        df["time"] = df["time"].astype(int)  # ⬅️ Ensure int format
        df["time"] = pd.to_datetime(df["time"], unit="s")  # ⬅️ Convert UNIX timestamp
        df.drop(columns=[
            "_id",
            "aclass",
            "subtype",
            "timestamp"
            ], inplace=True, errors="ignore")  ### cleanup
        config = {
            "time": st.column_config.DatetimeColumn("Time", format="iso8601"),
            "amount": st.column_config.NumberColumn("Price", format="dollar"),
            "balance": st.column_config.NumberColumn("Balance", format="None"),
            "fee": st.column_config.NumberColumn("Fee", format="dollar")
            }
        st.dataframe(df.head(10),
                    use_container_width=True,
                    column_order=[
                        "time",
                        "asset",
                        "amount",
                        "balance",
                        "fee",
                        "type",
                        "refid"                     
                    ],
                    column_config=config,
                    hide_index=True
                    )
    except Exception as e:
        st.error(f"Failed to generate table view: {e}")


    # Preview a few records
    st.subheader("Sample Records")
    st.json(documents[:1])

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

            df = pd.DataFrame(documents).drop(columns=["_id"], errors="ignore")
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name="kraken_rewards.csv",
                mime="text/csv",
            )