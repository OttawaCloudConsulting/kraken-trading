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
            self.metadata_collection.create_index("timestamp", unique=True)  # Ensure unique timestamps
            
            self.logger.info("MongoDB Client initialized successfully.")
        except errors.ConnectionFailure as e:
            self.logger.error("MongoDB connection failed: %s", e)
            raise

    def store_metadata(self, metadata: Dict) -> bool:
        """Stores metadata such as last retrieval timestamps.
        
        Args:
            metadata: Dictionary containing metadata details.
        
        Returns:
            bool: True if stored successfully, False otherwise.
        """
        if not metadata:
            self.logger.warning("No metadata provided.")
            return False
        try:
            self.metadata_collection.insert_one(metadata)
            self.logger.info("Metadata stored successfully: %s", metadata)
            return True
        except errors.DuplicateKeyError:
            self.logger.warning("Duplicate metadata timestamp, skipping insertion.")
            return False
        except errors.PyMongoError as e:
            self.logger.error("Failed to store metadata: %s", e)
            return False

    def store_trade_data(self, trade_data: Dict) -> bool:
        """Stores trade data into MongoDB."""
        if not trade_data:
            self.logger.warning("No trade data provided.")
            return False
        try:
            self.trades_collection.insert_one(trade_data)
            self.logger.info("Trade data stored successfully.")
            return True
        except errors.PyMongoError as e:
            self.logger.error("Failed to store trade data: %s", e)
            return False

    def store_staking_data(self, staking_data: Dict) -> bool:
        """Stores staking reward data into MongoDB."""
        if not staking_data:
            self.logger.warning("No staking data provided.")
            return False
        try:
            self.rewards_collection.insert_one(staking_data)
            self.logger.info("Staking data stored successfully.")
            return True
        except errors.PyMongoError as e:
            self.logger.error("Failed to store staking data: %s", e)
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