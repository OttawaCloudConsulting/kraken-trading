"""Kraken API Client for retrieving trade history and staking rewards via ledger entries."""

import time
import hmac
import hashlib
import base64
import requests
import json
import logging
from typing import Dict, Any
from urllib.parse import urlencode

KRAKEN_API_URL = "https://api.kraken.com"
TRADE_HISTORY_ENDPOINT = "/0/private/TradesHistory"
LEDGER_ENTRIES_ENDPOINT = "/0/private/Ledgers"

class KrakenAPIClient:
    """Client for interacting with Kraken's API."""

    def __init__(self, api_key: str, api_secret: str, logger: logging.Logger):
        """Initializes the Kraken API client.

        Args:
            api_key: The API key for Kraken authentication.
            api_secret: The API secret for Kraken authentication.
            logger: Logger instance for logging API interactions.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logger
        self.logger.debug("🔑 KrakenAPIClient initialized.")

    def _generate_signature(self, url_path: str, data: Dict[str, Any]) -> str:
        """Generates the Kraken API signature for authentication.

        Args:
            url_path: The API endpoint path.
            data: The request payload.

        Returns:
            A signature string for the API request.
        """
        secret_bytes = base64.b64decode(self.api_secret)
        nonce = str(int(time.time() * 1000))  # Convert nonce to string format
        data["nonce"] = nonce
        encoded_payload = urlencode(data)
        message = url_path.encode() + hashlib.sha256((nonce + encoded_payload).encode()).digest()
        signature = hmac.new(secret_bytes, message, hashlib.sha512)
        return base64.b64encode(signature.digest()).decode()

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Makes a request to Kraken's API.

        Args:
            endpoint: The Kraken API endpoint.
            payload: The request payload.

        Returns:
            The API response as a dictionary.
        """
        url = KRAKEN_API_URL + endpoint
        headers = {
            "API-Key": self.api_key,
            "API-Sign": self._generate_signature(endpoint, payload),
        }
        response = requests.post(url, headers=headers, data=payload)
        return response.json()

    def get_trade_history(self) -> Dict[str, Any]:
        """Fetches trade history from Kraken.

        Returns:
            A dictionary containing trade history data.
        """
        self.logger.info("📥 Fetching trade history from Kraken...")
        payload = {"nonce": int(time.time() * 1000)}
        response = self._make_request(TRADE_HISTORY_ENDPOINT, payload)

        if response.get("error"):
            self.logger.error(f"❌ API Error: {response['error']}")
            return {}

        self.logger.info("✅ Trade history retrieved successfully.")
        return response.get("result", {}).get("trades", {})

    def get_staking_rewards(self) -> Dict[str, Any]:
        """Fetches staking rewards from Kraken using ledger entries, filtering only actual staking earnings.

        Returns:
            A dictionary containing staking rewards data.
        """
        self.logger.info("📥 Fetching staking rewards from Kraken via ledgers...")
        payload = {"nonce": int(time.time() * 1000), "asset": "all", "type": "staking"}
        response = self._make_request(LEDGER_ENTRIES_ENDPOINT, payload)

        if response.get("error"):
            self.logger.error(f"❌ API Error: {response['error']}")
            return {}

        ledger_entries = response.get("result", {}).get("ledger", {})
        staking_rewards = {
            key: entry
            for key, entry in ledger_entries.items()
            if entry.get("type") == "staking" and entry.get("subtype") == ""
        }
        self.logger.info(f"✅ Retrieved {len(staking_rewards)} staking reward entries.")
        return staking_rewards
