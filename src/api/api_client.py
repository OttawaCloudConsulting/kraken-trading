"""Kraken API Client for retrieving historical trade data."""

import time
import hashlib
import hmac
import base64
import requests
import urllib.parse
import logging
from typing import Optional, Dict, Any
import config

class KrakenAPIClient:
    """Client for interacting with Kraken's API."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initializes the Kraken API Client with authentication credentials."""
        self.api_key: str = config.KRAKEN_API_KEY
        self.api_secret: str = config.KRAKEN_API_SECRET
        self.logger = logger

        if not self.api_key or not self.api_secret:
            self.logger.error("❌ API credentials are missing. Ensure they are set in the .env file.")
            raise ValueError("API credentials are missing.")
        
        self.logger.debug("🔑 API Key loaded successfully.")
        self.logger.debug("🔒 API Secret loaded successfully.")

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
        encoded_payload = urllib.parse.urlencode(data)
        message = url_path.encode() + hashlib.sha256((nonce + encoded_payload).encode()).digest()
        signature = hmac.new(secret_bytes, message, hashlib.sha512)
        return base64.b64encode(signature.digest()).decode()

    def _make_request(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Sends a signed request to the Kraken API.
        
        Args:
            endpoint: The Kraken API endpoint to call.
            payload: Optional request payload.
        
        Returns:
            The JSON response as a dictionary, or None if an error occurs.
        """
        url = f"https://api.kraken.com{endpoint}"
        headers = {
            "API-Key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = payload or {}
        headers["API-Sign"] = self._generate_signature(endpoint, payload)
        encoded_payload = urllib.parse.urlencode(payload)
        
        self.logger.debug(f"📤 Sending request to: {url}")
        self.logger.debug(f"📄 Payload: {encoded_payload}")

        try:
            response = requests.post(url, data=encoded_payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("error"):
                self.logger.warning(f"⚠️ API Error: {data['error']}")
                return None
            self.logger.debug("✅ API response received successfully.")
            return data.get("result")
        except requests.exceptions.RequestException as error:
            self.logger.error(f"❌ API Request Failed: {error}")
            return None

    def get_trade_history(self) -> Optional[Dict[str, Any]]:
        """Retrieves all historical trade data from Kraken.
        
        Returns:
            A dictionary containing trade history, or None if the request fails.
        """
        self.logger.info("📥 Fetching trade history from Kraken...")
        return self._make_request("/0/private/TradesHistory")