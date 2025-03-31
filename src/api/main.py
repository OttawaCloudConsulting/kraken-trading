"""Main entry point for Kraken trade and staking rewards retrieval and data storage."""

import os
import logging
import time
from api_client import KrakenAPIClient
from data_handler import save_trades, save_staking_rewards
from config import KRAKEN_API_KEY, KRAKEN_API_SECRET
from mongodb_client import MongoDBClient

def configure_logger() -> logging.Logger:
    """Configures and returns the logger instance.
    
    Returns:
        A configured logger instance.
    """
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.info(f"🛠️ Logging level set to: {log_level}")
    return logger

def main() -> None:
    """Main execution function for Kraken trade and staking rewards retrieval and storage."""
    logger = configure_logger()
    logger.info("🚀 Starting Kraken trade and staking rewards retrieval...")
    
    # Initialize Kraken API Client and MongoDB Client
    mongodb_client = MongoDBClient(logger)
    kraken_client = KrakenAPIClient(KRAKEN_API_KEY, KRAKEN_API_SECRET, logger, mongodb_client=mongodb_client)

    # Enable MongoDB storage based on environment variable STORE_IN_MONGODB
    STORE_IN_MONGODB = os.getenv("STORE_IN_MONGODB", "false").lower() == "true"
    logger.debug(f"STORE_IN_MONGODB: {STORE_IN_MONGODB}")
    storage_location = "mongodb" if STORE_IN_MONGODB else "local"
    logger.info(f"📦 Data storage location: {storage_location}")
    
    # Fetch trade history
    # trades = kraken_client.get_trade_history()
    trades, metadata = kraken_client.get_trade_history()
    if trades:
        logger.info(f"✅ Retrieved {len(trades)} trades successfully.")
        logger.info(f"storage_location: {storage_location}")
        metadata = {"data_type": "trades", "timestamp": int(time.time())}
        save_trades(trades, format="json", location=storage_location, logger=logger, mongodb_client=mongodb_client, metadata=metadata)
        # save_trades(trades, format="csv", location="local", logger=logger)
        
        # Store metadata using retrieval timestamp
        # mongodb_client.store_metadata(metadata)
    else:
        logger.error("❌ Failed to retrieve trade history.")
    
    # Fetch staking rewards (excluding transfers)
    staking_rewards = kraken_client.get_staking_rewards()
    if staking_rewards:
        logger.info(f"✅ Retrieved {len(staking_rewards)} staking reward entries.")
        logger.info(f"storage_location: {storage_location}")
        metadata = {"data_type": "rewards", "timestamp": int(time.time())}
        save_staking_rewards(staking_rewards, format="json", location=storage_location, logger=logger, mongodb_client=mongodb_client, metadata=metadata)
        # save_staking_rewards(staking_rewards, format="csv", location="local", logger=logger)

    else:
        logger.error("❌ No staking rewards retrieved.")

if __name__ == "__main__":
    main()
