"""Kraken API Client for retrieving trade history and staking rewards via ledger entries."""

import time
import hmac
import hashlib
import base64
import requests
# import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from data_handler import extract_record_timestamps

KRAKEN_API_URL = "https://api.kraken.com"
TRADE_HISTORY_ENDPOINT = "/0/private/TradesHistory"
LEDGER_ENTRIES_ENDPOINT = "/0/private/Ledgers"

class KrakenAPIClient:
    """Client for interacting with Kraken's API."""

    def __init__(self, api_key: str, api_secret: str, logger: logging.Logger, mongodb_client=None):
        """Initialize the Kraken API client.
        
        Args:
            api_key: Kraken API key.
            api_secret: Kraken API secret.
            logger: Logger instance for logging API interactions.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logger
        self.mongodb_client = mongodb_client

    def get_trade_history(self) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Retrieve the complete trade history using Kraken's paginated API.

        Returns:
            A tuple containing:
                - all_trades: Dictionary of all retrieved trades.
                - metadata: Dictionary containing retrieval metadata including:
                    - data_type (str): Type of data, i.e., 'trades'.
                    - timestamp (int): Time of execution.
                    - record_timestamp_start (int): Earliest trade timestamp.
                    - record_timestamp_end (int): Latest trade timestamp.
                    - last_trade_id (str): Kraken trade ID of the most recent trade.
        """
        all_trades = {}
        seen_trade_ids = set()
        offset = 0
        batch = 1
        last_trade_id = None
        first_batch_processed = False
        total_expected = None

        self.logger.info("Retrieving Kraken trade history using offset pagination.")

        while True:
            self.logger.debug("Fetching trade history batch %d with offset=%d", batch, offset)
            payload = {"ofs": offset}
            response = self._make_request_with_backoff("POST", TRADE_HISTORY_ENDPOINT, payload)

            if not response or "result" not in response or "trades" not in response["result"]:
                self.logger.warning("No response or invalid structure from Kraken.")
                break

            result = response["result"]
            trades = result.get("trades", {})
            self.logger.debug("Raw trade history response: %s", trades)

            if not trades:
                self.logger.info("Reached end of trade history.")
                break

            if not first_batch_processed:
                # Capture the total expected trade count and most recent trade ID
                total_expected = result.get("count", 0)
                last_trade_id = next(iter(trades.keys()), None)
                self.logger.debug("Total trades reported by Kraken: %d", total_expected)
                self.logger.debug("Last trade ID from first batch: %s", last_trade_id)
                first_batch_processed = True

            new_trades_added = 0
            for trade_id, trade_data in trades.items():
                if trade_id not in seen_trade_ids:
                    all_trades[trade_id] = trade_data
                    seen_trade_ids.add(trade_id)
                    new_trades_added += 1
                    self.logger.debug("Trade ID: %s, Timestamp: %s", trade_id, trade_data.get("time"))

            self.logger.debug("Batch %d - New trades added: %d", batch, new_trades_added)

            offset += 50
            batch += 1
            time.sleep(2.5)  # Throttle to avoid rate limits

            if total_expected is not None and offset >= total_expected:
                self.logger.info("Reached total trade count: %d. Ending pagination.", total_expected)
                break

        record_timestamp_start, record_timestamp_end = extract_record_timestamps(
            self.logger, list(all_trades.values()), "time")

        self.logger.info("✅ Retrieved %d total trades.", len(all_trades))
        self.logger.info("Trade timestamp range: %s to %s",
                        record_timestamp_start, record_timestamp_end)

        metadata = {
            "data_type": "trades",
            "timestamp": int(time.time()),
            "record_timestamp_start": record_timestamp_start,
            "record_timestamp_end": record_timestamp_end,
            "last_trade_id": last_trade_id,
        }

        return all_trades, metadata

    def _make_request_with_backoff(self, method: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with exponential backoff on rate limit errors.

        Args:
            method: HTTP method.
            endpoint: Kraken API endpoint.
            data: Request payload.

        Returns:
            Response from the API.
        """
        max_retries = 5
        backoff = 2

        for attempt in range(1, max_retries + 1):
            response = self._make_request(method, endpoint, data)
            error = response.get("error", [])

            if error and any("rate limit exceeded" in e.lower() for e in error):
                self.logger.warning("Rate limit hit. Backing off for %d seconds (attempt %d/%d)...",
                                    backoff, attempt, max_retries)
                time.sleep(backoff)
                backoff *= 2
            else:
                return response

        self.logger.error("Max retries exceeded for Kraken API request.")
        return {}

    def get_staking_rewards(self) -> Dict[str, Any]:
        """Fetches staking rewards from Kraken's ledger entries.
        
        Returns:
            Dictionary containing staking rewards.
        """
        response = self._make_request("POST", LEDGER_ENTRIES_ENDPOINT, {"asset": "all"})
        if response:
            ledger_entries = response.get("result", {}).get("ledger", {})
            self.logger.debug(f"Raw ledger response: {ledger_entries}")
            for entry_id, entry_data in ledger_entries.items():
                if entry_data.get("type") == "staking":
                    self.logger.debug(f"Ledger ID: {entry_id}, Timestamp: {entry_data.get('time')}")
            return ledger_entries
        return {}

    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handles making authenticated API requests to Kraken.
        
        Args:
            method: HTTP method (e.g., "POST").
            endpoint: Kraken API endpoint.
            data: Request parameters.
        
        Returns:
            Dictionary containing the API response.
        """
        url = f"{KRAKEN_API_URL}{endpoint}"
        headers = self._generate_headers(endpoint, data)
        response = requests.request(method, url, headers=headers, data=urlencode(data))
        
        try:
            response_json = response.json()
            if response_json.get("error"):
                self.logger.error(f"Kraken API error: {response_json['error']}")
            return response_json
        except Exception as e:
            self.logger.error(f"Failed to parse response JSON: {e}")
            return {}

    def _generate_headers(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, str]:
        """Generates Kraken API authentication headers.
        
        Args:
            endpoint: Kraken API endpoint.
            data: Request parameters.
        
        Returns:
            Dictionary containing authentication headers.
        """
        nonce = str(int(time.time() * 1000))
        data["nonce"] = nonce
        post_data = urlencode(data).encode()
        
        api_sign = hmac.new(base64.b64decode(self.api_secret),
                            (endpoint.encode() + hashlib.sha256(nonce.encode() + post_data).digest()),
                            hashlib.sha512)
        
        return {
            "API-Key": self.api_key,
            "API-Sign": base64.b64encode(api_sign.digest()).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _get_last_trade_id(self) -> Optional[str]:
        """Retrieve the last recorded trade ID from metadata.

        Returns:
            Optional[str]: The last recorded trade ID, or None if not found or if MongoDB is uninitialized.
        """
        if not self.mongodb_client:
            self.logger.warning("MongoDB client is not initialized. Cannot retrieve last trade ID.")
            return None

        latest_metadata = self.mongodb_client.get_latest_metadata("trades")
        if not latest_metadata:
            self.logger.info("No metadata found for trades.")
            return None

        last_trade_id = latest_metadata.get("last_trade_id")
        if last_trade_id:
            self.logger.debug("Retrieved last trade ID from metadata: %s", last_trade_id)
        else:
            self.logger.info("No 'last_trade_id' field found in latest metadata entry.")

        return last_trade_id
    
    def _get_min_trade_timestamp(self) -> Optional[int]:
        """Retrieve the most recent trade timestamp from metadata.

        Returns:
            Optional[int]: The latest trade record's timestamp, or None if not found or unavailable.
        """
        if not self.mongodb_client:
            self.logger.warning("MongoDB client is not initialized. Cannot retrieve trade timestamp.")
            return None

        latest_metadata = self.mongodb_client.get_latest_metadata("trades")
        if not latest_metadata:
            self.logger.info("No metadata found for trades.")
            return None

        min_timestamp = latest_metadata.get("record_timestamp_end")
        if min_timestamp is not None:
            self.logger.debug("Retrieved latest trade timestamp from metadata: %s", min_timestamp)
        else:
            self.logger.info("No 'record_timestamp_end' field found in latest metadata entry.")

        return min_timestamp