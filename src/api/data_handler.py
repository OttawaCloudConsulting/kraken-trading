"""Data Handler for saving trade history and staking rewards to local storage and MongoDB."""

import os
import json
import csv
import time
import logging
from typing import Dict, Optional, Tuple, List

# Normalization maps for Kraken asset metadata
BASE_TRANSFORM_MAP = {
    "XXDG": "DOGE",
    "XETC": "ETC",
    "XETH": "ETH",
    "XLTC": "LTC",
    "XMLN": "MLN",
    "XREP": "REP",
    "XXBT": "BTC",
    "XXLM": "XLM",
    "XXMR": "XMR",
    "XXRP": "XRP",
    "XZEC": "ZEC",
}

WSNAME_TRANSFORM_MAP = {
    "XCN/USD": "XCN/USD",
    "XDG/USD": "DOGE/USD",
    "XRT/USD": "XRT/USD",
    "XTZ/USD": "XTZ/USD",
    "XLM/USD": "XLM/USD",
    "XMR/USD": "XMR/USD",
    "XRP/USD": "XRP/USD",
    "XBT/USD": "BTC/USD",
}

def _ensure_output_directory() -> None:
    """Ensures that the 'outputs/' directory exists."""
    os.makedirs("outputs", exist_ok=True)

def _generate_filename(file_type: str, extension: str, custom_filename: Optional[str] = None) -> str:
    """Generates a timestamped filename or uses a custom one.
    
    Args:
        file_type: Type of file ('trades' or 'rewards').
        extension: The file extension (json, csv, etc.).
        custom_filename: Optional custom filename.

    Returns:
        A string representing the generated filename.
    """
    timestamp = int(time.time())
    if custom_filename:
        return f"outputs/{custom_filename}_{file_type}.{extension}"
    return f"outputs/{file_type}_{timestamp}.{extension}"

def _save_to_local(data: Dict, format: str, filename: str, logger: logging.Logger) -> None:
    """Saves trade history or staking rewards locally as JSON or CSV."""
    _ensure_output_directory()
    
    if not data:
        logger.error("❌ No data to save. File will not be created.")
        return

    try:
        if format == "json":
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            logger.info(f"✅ JSON file saved: {filename}")
        elif format == "csv":
            field_list = list(data.keys())
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(field_list)
                writer.writerow([data[field] for field in field_list])
            logger.info(f"✅ CSV file saved: {filename}")
        else:
            logger.error(f"❌ Unsupported file format: {format}")
    except (IOError, OSError) as error:
        logger.error(f"❌ Failed to save file: {filename}. Error: {error}")

def save_trades(trades: Dict, format: str, location: str, logger: logging.Logger, mongodb_client=None, metadata: Optional[Dict] = None, filename: Optional[str] = None) -> None:
    """Handles saving trade history to the specified location and format."""
    if location == "local":
        logger.info(f"Saving {len(trades)} trades to local storage...")
        file_path = _generate_filename("trades", format, filename)
        _save_to_local(trades, format, file_path, logger)
    elif location == "mongodb" and mongodb_client:
        for trade_id, trade_data in trades.items():
            logger.debug(f"Storing trade in MongoDB: {trade_id}")
            mongodb_client.store_data("trades", trade_data)
            mongodb_client.store_data("metadata", metadata)
    else:
        logger.error(f"❌ Unsupported storage location: {location}")

def save_staking_rewards(staking_data: Dict, format: str, location: str, logger: logging.Logger, mongodb_client=None, metadata: Optional[Dict] = None, filename: Optional[str] = None) -> None:
    """Handles saving staking rewards (via ledger entries) to the specified location and format."""
    if location == "local":
        logger.info(f"Saving {len(staking_data)} staking rewards to local storage...")
        file_path = _generate_filename("rewards", format, filename)
        _save_to_local(staking_data, format, file_path, logger)
    elif location == "mongodb" and mongodb_client:
        for reward_id, reward_data in list(staking_data.items()):
            logger.debug(f"Storing staking reward in MongoDB: {reward_id}")
            mongodb_client.store_data("rewards", reward_data)
            mongodb_client.store_data("metadata", metadata)
    else:
        logger.error(f"❌ Unsupported storage location: {location}")

def extract_record_timestamps(logger: logging.Logger, records: List[Dict], timestamp_key: str) -> Tuple[Optional[int], Optional[int]]:
    """Extracts the earliest and latest timestamps from a list of records.
    
    Args:
        records: List of trade or staking reward records.
        timestamp_key: The key that holds the timestamp value.
    
    Returns:
        A tuple (record_timestamp_start, record_timestamp_end) with integer timestamps.
    """
    if not records:
        return None, None
    logger.info(f"Extracting timestamps from {len(records)} records...")
    timestamps = [int(record[timestamp_key]) for record in records if timestamp_key in record]
    
    if not timestamps:
        return None, None

    return min(timestamps), max(timestamps)

def enrich_trades_with_asset_metadata(trades: dict, logger: logging.Logger, mongodb_client) -> None:
    """
    Enriches trade records with `wsname` and `base` fields from cached Kraken asset pair metadata.

    Each trade will be modified in-place by adding:
    - `wsname`: The user-friendly asset pair name (e.g., 'ETH/USD').
    - `base`: The base asset name (e.g., 'ETH').

    If no metadata is found for a pair:
    - Both `wsname` and `base` default to the original `pair` string.
    - A warning will be logged once per missing pair.

    Args:
        trades: Dictionary of trade_id → trade_record.
        logger: Logger for recording actions and errors.
        mongodb_client: MongoDBClient instance to query the asset pair cache.
    """
    if not trades:
        logger.warning("No trades provided for enrichment.")
        return

    if not mongodb_client:
        logger.error("❌ MongoDB client is not initialized. Cannot enrich trades.")
        return

    seen_missing_pairs = set()
    enriched_count = 0

    for trade_id, trade_data in trades.items():
        pair = trade_data.get("pair")
        if not pair:
            logger.warning("Trade %s is missing 'pair' field. Skipping.", trade_id)
            continue

        asset_info = mongodb_client.get_asset_pair_metadata(pair)

        if asset_info:
            base_raw = asset_info.get("base", pair)
            wsname_raw = asset_info.get("wsname", pair)

            # Normalize using maps
            trade_data["base"] = BASE_TRANSFORM_MAP.get(base_raw, base_raw)
            trade_data["wsname"] = WSNAME_TRANSFORM_MAP.get(wsname_raw, wsname_raw)
        else:
            if pair not in seen_missing_pairs:
                logger.warning("No asset metadata found for pair: %s. Using fallback values.", pair)
                seen_missing_pairs.add(pair)
            trade_data["wsname"] = pair
            trade_data["base"] = pair

        enriched_count += 1

    logger.info("✅ Enriched %d trades with asset metadata.", enriched_count)