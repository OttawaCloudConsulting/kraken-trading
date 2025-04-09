import streamlit as st
import pandas as pd
from utils.mongo_client import MongoDBClient  # ✅ Correct import

def render_trades() -> None:
    """Render the Trades view and allow export of data from MongoDB."""
    st.title("📈 Trade History")

    client = MongoDBClient()
    collection = client.get_collection("kraken_trades")
    if collection is None:
        st.error("Unable to connect to MongoDB or find the 'kraken_trades' collection.")
        return


    documents = list(collection.find())
    if not documents:
        st.warning("No trade data available in MongoDB.")
        return

    st.success(f"Retrieved {len(documents)} trade records.")

    # 👉 Table Preview
    st.subheader("Table Preview")
    try:
        df = pd.DataFrame(documents)
        df["time"] = df["time"].astype(int) 
        df["time"] = pd.to_datetime(df["time"], unit="s")  
        df.drop(columns=[
            "_id",
            "postxid",
            "aclass",
            "margin",
            "leverage",
            "misc"
            ], inplace=True, errors="ignore")  ### cleanup
        df = df.sort_values("time", ascending=False)
        config = {
            "time": st.column_config.DatetimeColumn("Time", format="iso8601"),
            "price": st.column_config.NumberColumn("Price"),
            "cost": st.column_config.NumberColumn("Cost"),
            "fee": st.column_config.NumberColumn("Fee"),
            "vol": st.column_config.NumberColumn("Volume"),
            }
        st.dataframe(df.head(10),
                    use_container_width=True,
                    column_order=[
                        "time",
                        "wsname",
                        "type",
                        "ordertype",
                        "price",
                        "cost",
                        "fee",
                        "vol",
                        "ordertxid",
                        "trade_id",
                        "maker",
                        "base",
                        "pair"                        
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
    st.subheader("Download Trade Data")

    export_format = st.selectbox("Select export format:", ["JSON", "CSV"])

    if st.button("Download"):
        if export_format == "JSON":
            st.download_button(
                label="Download JSON",
                data=str(documents).encode("utf-8"),
                file_name="kraken_trades.json",
                mime="application/json",
            )
        else:
            df = pd.DataFrame(documents).drop(columns=["_id"], errors="ignore")
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name="kraken_trades.csv",
                mime="text/csv",
            )