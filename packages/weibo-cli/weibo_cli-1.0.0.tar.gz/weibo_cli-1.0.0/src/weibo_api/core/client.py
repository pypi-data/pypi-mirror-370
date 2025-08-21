"""
Pure HTTP client for Weibo API

Simple, focused HTTP client that does one thing well.
No business logic, just HTTP requests.
"""

import asyncio
import json
import logging
from typing import Any

import httpx

from ..exceptions import NetworkError, ParseError


class HttpClient:
    """Pure HTTP client

    Responsibilities:
    - Make HTTP requests
    - Handle basic HTTP errors
    - Manage connection lifecycle

    Does NOT handle:
    - Authentication/cookies (that's auth.py)
    - Retries (that's retry.py)
    - Business logic parsing (that's parsers/)
    """

    def __init__(
        self,
        timeout: float = 10.0,
        max_connections: int = 20,
        max_keepalive_connections: int = 5,
        logger: logging.Logger | None = None,
    ):
        self._timeout = timeout
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections
        self._logger = logger or logging.getLogger(__name__)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            limits=httpx.Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
            ),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_json(
        self, url: str, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Get JSON response"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        try:
            response = await self._client.get(url, headers=headers or {})
            response.raise_for_status()

            data = response.json()
            self._logger.debug(f"GET {url} -> {response.status_code}")
            return data

        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON response: {url}")
            raise ParseError(f"Invalid JSON: {e}")

    async def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        """Get text response"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        try:
            response = await self._client.get(url, headers=headers or {})
            response.raise_for_status()

            self._logger.debug(f"GET {url} -> {response.status_code}")
            return response.text

        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

    async def post_form(
        self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """POST form data and get JSON response"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        try:
            response = await self._client.post(url, data=data, headers=headers or {})
            response.raise_for_status()

            result = response.json()
            self._logger.debug(f"POST {url} -> {response.status_code}")
            return result

        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON response: {url}")
            raise ParseError(f"Invalid JSON: {e}")

    async def post_form_raw(
        self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None
    ) -> httpx.Response:
        """POST form data and get raw response with cookies"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        try:
            response = await self._client.post(url, data=data, headers=headers or {})
            response.raise_for_status()

            self._logger.debug(f"POST {url} -> {response.status_code}")
            return response

        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")
