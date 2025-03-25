"""Data Handler for saving trade history and staking rewards to local storage and MongoDB."""

import os
import json
import csv
import time
import logging
from typing import Dict, Optional, Tuple, List

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
            mongodb_client.store_trade_data(trade_data)
            mongodb_client.store_metadata(metadata)
    else:
        logger.error(f"❌ Unsupported storage location: {location}")

def save_staking_rewards(staking_data: Dict, format: str, location: str, logger: logging.Logger, mongodb_client=None, metadata: Optional[Dict] = None, filename: Optional[str] = None) -> None:
    """Handles saving staking rewards (via ledger entries) to the specified location and format."""
    if location == "local":
        logger.info(f"Saving {len(staking_data)} staking rewards to local storage...")
        file_path = _generate_filename("rewards", format, filename)
        _save_to_local(staking_data, format, file_path, logger)
    elif location == "mongodb" and mongodb_client:
        for reward_id, reward_data in staking_data.items():
            logger.debug(f"Storing staking reward in MongoDB: {reward_id}")
            mongodb_client.store_staking_data(reward_data)
            mongodb_client.store_metadata(metadata)
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
