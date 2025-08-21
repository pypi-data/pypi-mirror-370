import time
import hmac
import hashlib
import requests


class FintagClient:
    def __init__(self, api_key: str, base_url: str = "https://api.fintag.io"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _get_headers(self):
        timestamp = str(int(time.time() * 1000))  # ms
        signature = hmac.new(
            self.api_key.encode("utf-8"),
            timestamp.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return {
            "authorization": self.api_key,
            "x-timestamp": timestamp,
            "x-signature": signature,
        }

    def verify(self, fintag: str):
        cleaned_fintag = fintag[1:] if fintag.startswith("#") else fintag
        url = f"{self.base_url}/fintag/verify/{cleaned_fintag}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_wallet_info(self, fintag: str):
        cleaned_fintag = fintag[1:] if fintag.startswith("#") else fintag
        url = f"{self.base_url}/fintag/wallet/{cleaned_fintag}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
