from api_client import KrakenAPIClient
# from data_handler import save_trades_to_file
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    """Main execution function."""
    logger.info("🚀 Starting Kraken trade history retrieval...")
    
    # Initialize Kraken API Client
    kraken_client = KrakenAPIClient()
    trades = kraken_client.get_trade_history()

    if trades:
        logger.info("✅ Trade history retrieved successfully.")
        logger.debug(trades)
        # save_trades_to_file(trades)
    else:
        logger.error("❌ Failed to retrieve trade history.")

if __name__ == "__main__":
    main()