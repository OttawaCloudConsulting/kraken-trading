"""Data Handler for saving trade history to local storage in JSON and CSV formats."""

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

def _save_to_local(trades: Dict, format: str, filename: str, logger: logging.Logger) -> None:
    """Saves trade data locally as JSON or CSV.
    
    Args:
        trades: The trade data to save.
        format: The output format ('json' or 'csv').
        filename: The filename to save the data.
        logger: Logger instance for logging messages.
    """
    _ensure_output_directory()
    
    if not trades or "trades" not in trades:
        logger.error("❌ No valid trade data found in API response. File will not be created.")
        return

    trade_entries = trades["trades"]  # Extract only the trades dictionary
    
    try:
        if format == "json":
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(trade_entries, file, indent=4)
            file_size = os.path.getsize(filename) / 1024  # Convert bytes to KB
            logger.info(f"✅ JSON file saved: {filename} (Size: {file_size:.2f} KB)")
        
        elif format == "csv":
            # Convert trade dictionary to list of trade entries, ensuring trade_id is included
            trade_list = [
                {**trade, "trade_id": trade_id} for trade_id, trade in trade_entries.items() if isinstance(trade, dict)
            ]
            
            if not trade_list:
                logger.error("❌ No valid trade records found for CSV export.")
                return
            
            if len(trade_list) != len(trade_entries):
                logger.warning("⚠️ Some trade entries were not dictionaries and were skipped.")
            
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(ALL_TRADE_FIELDS)
                
                for trade in trade_list:
                    # Convert list fields to comma-separated strings for CSV
                    for key, value in trade.items():
                        if isinstance(value, list):
                            trade[key] = ",".join(map(str, value))
                    
                    # Ensure all expected fields are present, fill missing fields with empty strings
                    row_data = [trade.get(field, "") for field in ALL_TRADE_FIELDS]
                    writer.writerow(row_data)
                    
                    # Log warnings for missing fields
                    missing_fields = [field for field in ALL_TRADE_FIELDS if field not in trade]
                    if missing_fields:
                        logger.warning(f"⚠️ Trade {trade['trade_id']} is missing fields: {missing_fields}")
            
            file_size = os.path.getsize(filename) / 1024
            logger.info(f"✅ CSV file saved: {filename} (Size: {file_size:.2f} KB)")
        
        else:
            logger.error(f"❌ Unsupported file format: {format}")
    except (IOError, OSError) as error:
        logger.error(f"❌ Failed to save file: {filename}. Error: {error}")

def save_trades(trades: Dict, format: str, location: str, logger: logging.Logger, filename: Optional[str] = None) -> None:
    """Handles saving trade data to the specified location and format.
    
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
