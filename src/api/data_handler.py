"""Data Handler for saving trade history and staking rewards to local storage in JSON and CSV formats."""

import os
import json
import csv
import time
import logging
from typing import Dict, Optional

def _ensure_output_directory() -> None:
    """Ensures that the 'outputs/' directory exists."""
    os.makedirs("outputs", exist_ok=True)

def _generate_filename(extension: str, custom_filename: Optional[str] = None) -> str:
    """Generates a timestamped filename or uses a custom one.
    
    Args:
        extension: The file extension (json, csv, etc.).
        custom_filename: Optional custom filename.

    Returns:
        A string representing the generated filename.
    """
    timestamp = int(time.time())
    if custom_filename:
        return f"outputs/{custom_filename}.{extension}"
    return f"outputs/my_trades_{timestamp}.{extension}"

# Predefined trade fields based on Kraken's API schema
ALL_TRADE_FIELDS = [
    "trade_id", "ordertxid", "postxid", "pair", "time", "type", "ordertype",
    "price", "cost", "fee", "vol", "margin", "leverage", "misc",
    "ledgers", "maker", "posstatus", "cprice"
]

# Predefined staking rewards fields based on Kraken's API schema (via ledger entries)
ALL_STAKING_FIELDS = [
    "ledger_id", "refid", "time", "asset", "amount", "balance"
]

def _save_to_local(data: Dict, format: str, filename: str, logger: logging.Logger) -> None:
    """Saves trade history or staking rewards locally as JSON or CSV.
    
    Args:
        data: The data to save (trade history or staking rewards).
        format: The output format ('json' or 'csv').
        filename: The filename to save the data.
        logger: Logger instance for logging messages.
    """
    _ensure_output_directory()
    
    if not data:
        logger.error("❌ No data to save. File will not be created.")
        return

    try:
        if format == "json":
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            file_size = os.path.getsize(filename) / 1024  # Convert bytes to KB
            logger.info(f"✅ JSON file saved: {filename} (Size: {file_size:.2f} KB)")
        
        elif format == "csv":
            field_list = ALL_STAKING_FIELDS if "staking_rewards" in filename else ALL_TRADE_FIELDS
            data_list = [
                {**entry, "ledger_id": key} for key, entry in data.items()
                if isinstance(entry, dict)
            ]
            
            if not data_list:
                logger.error("❌ No valid records found for CSV export.")
                return
            
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(field_list)
                
                for entry in data_list:
                    row_data = [entry.get(field, "") for field in field_list]
                    writer.writerow(row_data)
            
            file_size = os.path.getsize(filename) / 1024
            logger.info(f"✅ CSV file saved: {filename} (Size: {file_size:.2f} KB)")
        
        else:
            logger.error(f"❌ Unsupported file format: {format}")
    except (IOError, OSError) as error:
        logger.error(f"❌ Failed to save file: {filename}. Error: {error}")

def save_trades(trades: Dict, format: str, location: str, logger: logging.Logger, filename: Optional[str] = None) -> None:
    """Handles saving trade history to the specified location and format.
    
    Args:
        trades: The trade data retrieved from Kraken.
        format: The output format ('json' or 'csv').
        location: The storage location ('local').
        logger: Logger instance for logging messages.
        filename: Optional custom filename.
    """
    if location == "local":
        file_path = _generate_filename(format, filename)
        _save_to_local(trades, format, file_path, logger)
    else:
        logger.error(f"❌ Unsupported storage location: {location}")

def save_staking_rewards(staking_data: Dict, format: str, location: str, logger: logging.Logger, filename: Optional[str] = None) -> None:
    """Handles saving staking rewards (via ledger entries) to the specified location and format.
    
    Args:
        staking_data: The staking rewards data retrieved from Kraken's ledger.
        format: The output format ('json' or 'csv').
        location: The storage location ('local').
        logger: Logger instance for logging messages.
        filename: Optional custom filename.
    """
    if location == "local":
        file_path = _generate_filename(format, filename)
        _save_to_local(staking_data, format, file_path, logger)
    else:
        logger.error(f"❌ Unsupported storage location: {location}")
