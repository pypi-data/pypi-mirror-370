import os
from typing import Any, Dict, Optional

import requests
from termcolor import colored


def http_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            try:
                error_details = e.response.json()
                print(colored(f"HTTP API error occurred (Status: {e.response.status_code}): {error_details}", "red"))
            except ValueError:
                error_text = e.response.text
                print(
                    colored(
                        f"HTTP API error occurred (Status: {e.response.status_code}): {error_text}",
                        "red",
                    )
                )
            raise
        except Exception as e:
            print(colored(f"An error occurred: {e!s}", "red"))
            raise

    return wrapper


class Client:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self._api_key = api_key
        self.base_url = base_url or os.getenv("GALTEA_API_URL") or "https://api.galtea.ai"

    def _get_headers(self) -> Dict[str, str]:
        headers = {"User-agent": "Galtea SDK user agent"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    @http_exception
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    @http_exception
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response

    @http_exception
    def patch(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.patch(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response

    @http_exception
    def delete(self, endpoint: str) -> requests.Response:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response
