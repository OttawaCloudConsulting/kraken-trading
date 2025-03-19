"""Kraken API Client for retrieving trade history and staking rewards via ledger entries."""

import time
import hmac
import hashlib
import base64
import requests
# import json
import logging
from typing import Dict, Any
from urllib.parse import urlencode

KRAKEN_API_URL = "https://api.kraken.com"
TRADE_HISTORY_ENDPOINT = "/0/private/TradesHistory"
LEDGER_ENTRIES_ENDPOINT = "/0/private/Ledgers"

class KrakenAPIClient:
    """Client for interacting with Kraken's API."""

    def __init__(self, api_key: str, api_secret: str, logger: logging.Logger):
        """Initialize the Kraken API client.
        
        Args:
            api_key: Kraken API key.
            api_secret: Kraken API secret.
            logger: Logger instance for logging API interactions.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logger

    def get_trade_history(self) -> Dict[str, Any]:
        """Fetches trade history from Kraken.
        
        Returns:
            Dictionary containing trade history.
        """
        response = self._make_request("POST", TRADE_HISTORY_ENDPOINT, {})
        if response:
            trades = response.get("result", {}).get("trades", {})
            self.logger.debug(f"Raw trade history response: {trades}")
            for trade_id, trade_data in trades.items():
                self.logger.debug(f"Trade ID: {trade_id}, Timestamp: {trade_data.get('time')}")
            return trades
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
