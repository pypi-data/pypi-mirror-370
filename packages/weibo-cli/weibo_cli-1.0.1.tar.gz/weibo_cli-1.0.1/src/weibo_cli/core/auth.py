"""
Cookie authentication manager

Simple cookie management with clear state.
No complex state machines, just basic validation and generation.
"""

import json
import logging
import re
import time

import httpx

from .client import HttpClient
from ..exceptions import AuthError, ParseError, NetworkError


class CookieManager:
    """Simple cookie manager

    Responsibilities:
    - Generate visitor cookies
    - Validate cookies
    - Cache cookies for configured TTL

    Does NOT handle:
    - Complex state management
    - Retry logic (that's retry.py)
    - HTTP requests (uses HttpClient)
    """

    def __init__(
        self,
        http_client: HttpClient,
        ttl: float = 300.0,  # 5 minutes
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        logger: logging.Logger | None = None,
    ):
        self._http = http_client
        self._ttl = ttl
        self._user_agent = user_agent
        self._logger = logger or logging.getLogger(__name__)

        # Simple state
        self._cookies: str | None = None
        self._expires_at: float | None = None

    def set_cookies(self, cookies: str) -> None:
        """Set cookies manually"""
        self._cookies = cookies
        self._expires_at = time.time() + self._ttl

    def get_cookies(self) -> str | None:
        """Get current valid cookies"""
        if self._is_expired():
            return None
        return self._cookies

    def _is_expired(self) -> bool:
        """Check if cookies are expired"""
        if not self._cookies or not self._expires_at:
            return True
        return time.time() >= self._expires_at

    def _is_valid_format(self, cookies: str) -> bool:
        """Basic cookie format validation"""
        return "SUB=" in cookies and "SUBP=" in cookies

    async def ensure_valid_cookies(self) -> str:
        """Ensure we have valid cookies, generate if needed"""
        # Return cached cookies if still valid
        if not self._is_expired() and self._cookies:
            if self._is_valid_format(self._cookies):
                return self._cookies
            else:
                self._logger.warning("Cached cookies have invalid format")

        # Generate new cookies
        await self._generate_cookies()

        if not self._cookies:
            raise AuthError("Failed to generate cookies")

        return self._cookies

    async def _generate_cookies(self) -> None:
        """Generate visitor cookies"""
        url = "https://passport.weibo.com/visitor/genvisitor2"
        data = {
            "cb": "visitor_gray_callback",
            "tid": "",
            "from": "weibo",
            "webdriver": "false",
        }
        headers = {
            "User-Agent": self._user_agent,
            "Referer": "https://passport.weibo.com/visitor/visitor",
        }

        self._logger.info("Generating visitor cookies...")

        try:
            # Use HTTP client's new method to get raw response
            response = await self._http.post_form_raw(url, data, headers)

            # Try to get cookies from response headers first
            sub = response.cookies.get("SUB")
            subp = response.cookies.get("SUBP")
            if sub and subp:
                cookies = f"SUB={sub}; SUBP={subp}"
                self._cookies = cookies
                self._expires_at = time.time() + self._ttl
                self._logger.info("✅ Generated visitor cookies from headers")
                return

            # Try to parse JSONP response from text
            text = response.text
            match = re.search(r"\((.*)\)", text)
            if match:
                json_data = json.loads(match.group(1))
                if json_data.get("retcode") == 20000000 and "data" in json_data:
                    data_obj = json_data["data"]
                    if "sub" in data_obj and "subp" in data_obj:
                        cookies = f"SUB={data_obj['sub']}; SUBP={data_obj['subp']}"
                        self._cookies = cookies
                        self._expires_at = time.time() + self._ttl
                        self._logger.info("✅ Generated visitor cookies from JSONP")
                        return

            raise ParseError("Cannot extract cookies from response")

        except httpx.HTTPStatusError as e:
            self._logger.error(
                f"HTTP error during cookie generation: {e.response.status_code}"
            )
            raise AuthError(f"HTTP error {e.response.status_code}")
        except httpx.RequestError as e:
            self._logger.error(f"Request error during cookie generation: {e}")
            raise AuthError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON parsing error: {e}")
            raise ParseError(f"Invalid JSON in response: {e}")
        except Exception as e:
            self._logger.error(f"Cookie generation failed: {e}")
            raise AuthError(f"Failed to generate cookies: {e}")

    async def validate_cookies(self, cookies: str) -> bool:
        """Validate cookies by making test request"""
        if not self._is_valid_format(cookies):
            return False

        try:
            url = "https://weibo.com/ajax/profile/info?uid=1"
            headers = {
                "Cookie": cookies,
                "User-Agent": self._user_agent,
                "Referer": "https://weibo.com/",
            }

            response = await self._http.get_json(url, headers)
            return response.get("ok") == 1

        except Exception as e:
            self._logger.debug(f"Cookie validation failed: {e}")
            return False
