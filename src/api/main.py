"""Main entry point for Kraken trade and staking rewards retrieval and data storage."""

import os
import logging
from api_client import KrakenAPIClient
from data_handler import save_trades, save_staking_rewards
from config import KRAKEN_API_KEY, KRAKEN_API_SECRET

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
    
    # Initialize Kraken API Client with logger
    kraken_client = KrakenAPIClient(KRAKEN_API_KEY, KRAKEN_API_SECRET, logger)
    
    # Fetch trade history
    trades = kraken_client.get_trade_history()
    if trades:
        logger.info("✅ Trade history retrieved successfully.")
        save_trades(trades, format="json", location="local", logger=logger)
        save_trades(trades, format="csv", location="local", logger=logger)
    else:
        logger.error("❌ Failed to retrieve trade history.")
    
    # Fetch staking rewards (excluding transfers)
    staking_rewards = kraken_client.get_staking_rewards()
    if staking_rewards:
        logger.info(f"✅ Retrieved {len(staking_rewards)} staking reward entries.")
        save_staking_rewards(staking_rewards, format="json", location="local", logger=logger, filename="staking_rewards")
        save_staking_rewards(staking_rewards, format="csv", location="local", logger=logger, filename="staking_rewards")
    else:
        logger.error("❌ No staking rewards retrieved.")

if __name__ == "__main__":
    main()