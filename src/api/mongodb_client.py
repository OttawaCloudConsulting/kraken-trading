"""MongoDB Client for Storing Trade History, Staking Rewards, and Metadata."""

import logging
from typing import Optional, Dict
from pymongo import MongoClient, errors
from config import DB_NAME

class MongoDBClient:
    """Handles MongoDB operations for Kraken trade history, staking rewards, and metadata."""

    def __init__(self, logger: logging.Logger, mongo_uri: str) -> None:
        """Initializes MongoDB client and collections.
        
        Args:
            logger: Logger instance for logging MongoDB interactions.
        """
        self.logger = logger
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
        self.trades_collection = None
        self.rewards_collection = None
        self.metadata_collection = None
        
        self._connect()

    def _connect(self) -> None:
        """Establishes connection to MongoDB and initializes collections."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.client.server_info()  # Trigger connection error if MongoDB is unreachable
            self.db = self.client[DB_NAME]
            self.trades_collection = self.db["kraken_trades"]
            self.rewards_collection = self.db["kraken_rewards"]
            self.metadata_collection = self.db["kraken_metadata"]
            
            # Ensure indexes for efficient queries
            self.trades_collection.create_index("timestamp", unique=False)
            self.rewards_collection.create_index("timestamp", unique=False)
            self.metadata_collection.create_index(
                [("data_type", 1), ("record_timestamp_end", -1)]
            )  # Ensure unique timestamps
            
            self.logger.info("MongoDB Client initialized successfully.")
        except errors.ConnectionFailure as e:
            self.logger.error("❌ MongoDB connection failed: %s", e)
            raise

    def store_data(self, collection_name: str, data: Dict) -> bool:
        """Stores metadata,trades or rewards including 
            last retrieval timestamps.
        
        Args:
            metadata: Dictionary containing metadata details.
        
        Returns:
            bool: True if stored successfully, False otherwise.
        """
        if not data:
            self.logger.warning("No data provided for collection '%s'.", collection_name)
            return False
        try:
            collection = getattr(self, f"{collection_name}_collection", None)
            if collection is None:
                self.logger.error("❌ Collection '%s' does not exist on MongoDBClient.", collection_name)
                return False
            collection.insert_one(data)
            self.logger.info("Data stored successfully in '%s': %s", collection_name, data)
            return True
        except errors.DuplicateKeyError:
            self.logger.warning("Duplicate key error for collection '%s'. Skipping insertion.", collection_name)
            return False
        except errors.PyMongoError as e:
            self.logger.error("❌ Failed to store data in collection '%s': %s", collection_name, e)
            return False

    def get_latest_metadata(self, data_type: str) -> Optional[Dict]:
        """Retrieves the most recent metadata entry for a given data type.

        Args:
            data_type: Either 'trades' or 'rewards'.

        Returns:
            The latest metadata document or None if not found.
        """
        try:
            result = self.metadata_collection.find_one(
                {"data_type": data_type},
                sort=[("record_timestamp_end", -1)]
            )
            if result:
                self.logger.debug(f"Retrieved latest metadata: {result}")
            return result
        except Exception as e:
            self.logger.error(f"❌ Error retrieving metadata: {e}")
            return None

        
    def upsert_asset_pair_metadata(self, asset_pairs: dict) -> None:
        """Upserts Kraken asset pair metadata into the MongoDB collection.

        Args:
            asset_pairs: Dictionary of asset pair metadata from Kraken API.
        """
        if self.db is None:
            self.logger.warning("MongoDB client is not initialized. Cannot upsert asset pairs.")
            return

        collection = self.db["kraken_asset_pairs"]
        upsert_count = 0

        for pair_key, pair_data in asset_pairs.items():
            try:
                result = collection.update_one(
                    {"pair_key": pair_key},
                    {"$set": {"pair_key": pair_key, "data": pair_data}},
                    upsert=True
                )
                if result.upserted_id:
                    self.logger.debug("Inserted new asset pair: %s", pair_key)
                elif result.modified_count:
                    self.logger.debug("Updated asset pair: %s", pair_key)
                upsert_count += 1
            except Exception as e:
                self.logger.error("❌ Failed to upsert asset pair %s: %s", pair_key, str(e))

        self.logger.info("✅ Upserted %d asset pair records into MongoDB.", upsert_count)

    # def get_asset_pair_metadata(self, pair: str, kraken_client) -> dict:
    #     """Retrieve asset pair info (wsname, base) from MongoDB or fetch from Kraken if missing.
        
    #     Args:
    #         pair: Kraken asset pair identifier (e.g., 'XETHZUSD')
    #         kraken_client: Instance of KrakenAPIClient used to fetch asset pairs if needed.

    #     Returns:
    #         Dictionary with 'wsname' and 'base' fields, falling back to the input `pair` if not found.
    #     """
    #     collection = self.db["kraken_asset_pairs"]
    #     document = collection.find_one({"pair_key": pair})

    #     if document:
    #         data = document.get("data", {})
    #         wsname = data.get("wsname", pair)
    #         base = data.get("base", pair)
    #         return {"wsname": wsname, "base": base}

    #     self.logger.warning("Asset pair '%s' not found in MongoDB. Fetching from Kraken...", pair)
    #     fetched = kraken_client.fetch_asset_pairs_from_kraken()

    #     if not fetched:
    #         self.logger.error("❌ Unable to retrieve asset pairs from Kraken. Returning fallback values.")
    #         return {"wsname": pair, "base": pair}

    #     # Retry lookup after attempted insert
    #     document = collection.find_one({"pair_key": pair})
    #     if document:
    #         data = document.get("data", {})
    #         wsname = data.get("wsname", pair)
    #         base = data.get("base", pair)
    #         return {"wsname": wsname, "base": base}

    #     self.logger.error("❌ Asset pair '%s' still not found after Kraken fetch. Using fallback.", pair)
    #     return {"wsname": pair, "base": pair}

    def get_asset_pair_metadata(self, pair: str) -> dict:
        """
        Retrieve asset pair metadata from MongoDB.

        This method queries the 'kraken_asset_pairs' collection to fetch cached metadata
        for the specified Kraken asset pair. It does not call Kraken if the data is missing.

        Args:
            pair: Kraken asset pair identifier (e.g., 'XETHZUSD')

        Returns:
            Dictionary containing metadata fields like 'wsname' and 'base'.
            If not found, returns empty dict.
        """
        if self.db is None:
            self.logger.error("❌ MongoDB client is not initialized. Cannot retrieve asset pair metadata.")
            return {}

        try:
            collection = self.db["kraken_asset_pairs"]
            document = collection.find_one({"pair_key": pair})

            if document and "data" in document:
                return {
                    "wsname": document["data"].get("wsname", pair),
                    "base": document["data"].get("base", pair)
                }

            self.logger.warning("No cached asset pair metadata found for pair: %s", pair)
            return {}
        except Exception as e:
            self.logger.error("❌ Error retrieving asset metadata for pair %s: %s", pair, str(e))
            return {}