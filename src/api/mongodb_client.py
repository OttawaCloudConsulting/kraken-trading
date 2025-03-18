"""MongoDB Client for Storing Trade History & Staking Rewards."""

import os
import logging
from typing import Optional, Dict
from pymongo import MongoClient, errors

# MongoDB Connection Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "kraken_data"

class MongoDBClient:
    """Handles MongoDB operations for Kraken trade history & staking rewards."""

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
            
            self.logger.info("MongoDB Client initialized successfully.")
        except errors.ConnectionFailure as e:
            self.logger.error("MongoDB connection failed: %s", e)
            raise

    def get_last_retrieval_timestamp(self, data_type: str) -> Optional[int]:
        """Retrieves the last stored timestamp for trades or rewards."""
        valid_types = {"trades": self.trades_collection, "rewards": self.rewards_collection}
        if data_type not in valid_types:
            self.logger.error("Invalid data_type: %s", data_type)
            return None
        
        result = self.metadata_collection.find_one({"data_type": data_type}, sort=[("timestamp", -1)])
        return result["timestamp"] if result else None

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
