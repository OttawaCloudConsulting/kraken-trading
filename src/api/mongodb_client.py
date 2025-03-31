"""MongoDB Client for Storing Trade History, Staking Rewards, and Metadata."""

import logging
from typing import Optional, Dict
from pymongo import MongoClient, errors
from config import MONGO_URI, DB_NAME

class MongoDBClient:
    """Handles MongoDB operations for Kraken trade history, staking rewards, and metadata."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initializes MongoDB client and collections.
        
        Args:
            logger: Logger instance for logging MongoDB interactions.
        """
        self.logger = logger
        self.client = None
        self.db = None
        self.trades_collection = None
        self.rewards_collection = None
        self.metadata_collection = None
        
        self._connect()

    def _connect(self) -> None:
        """Establishes connection to MongoDB and initializes collections."""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
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
            self.logger.error("MongoDB connection failed: %s", e)
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
                self.logger.error("Collection '%s' does not exist on MongoDBClient.", collection_name)
                return False
            collection.insert_one(data)
            self.logger.info("Data stored successfully in '%s': %s", collection_name, data)
            return True
        except errors.DuplicateKeyError:
            self.logger.warning("Duplicate key error for collection '%s'. Skipping insertion.", collection_name)
            return False
        except errors.PyMongoError as e:
            self.logger.error("Failed to store data in collection '%s': %s", collection_name, e)
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
            self.logger.error(f"Error retrieving metadata: {e}")
            return None