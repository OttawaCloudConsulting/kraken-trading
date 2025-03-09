"""Main entry point for Kraken trade retrieval and data storage."""

import os
import logging
from api_client import KrakenAPIClient
from data_handler import save_trades

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
    """Main execution function for Kraken trade history retrieval and storage."""
    logger = configure_logger()
    logger.info("🚀 Starting Kraken trade history retrieval...")
    
    # Initialize Kraken API Client with logger
    kraken_client = KrakenAPIClient(logger)
    trades = kraken_client.get_trade_history()

    if trades:
        logger.info("✅ Trade history retrieved successfully.")
        
        # Save as JSON
        save_trades(trades, format="json", location="local", logger=logger)
        
        # Save as CSV
        save_trades(trades, format="csv", location="local", logger=logger)
    else:
        logger.error("❌ Failed to retrieve trade history.")

if __name__ == "__main__":
    main()
