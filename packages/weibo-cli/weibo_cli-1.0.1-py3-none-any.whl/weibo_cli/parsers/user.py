"""
User data parser

Parse raw user data from API responses into User entities.
Simple, focused parsing logic.
"""

import logging
from typing import Any

from ..exceptions import ParseError
from ..models.entities import User
from ..utils import parse_count_string


class UserParser:
    """Parse raw user data into User entities

    Responsibilities:
    - Extract user data from API response
    - Validate required fields
    - Handle missing/malformed data gracefully
    - Convert to User entity
    """

    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)

    def parse(self, raw_data: dict[str, Any]) -> User:
        """Parse raw user data into User entity

        Args:
            raw_data: Raw user data from API

        Returns:
            User entity

        Raises:
            ParseError: When required fields are missing or invalid
        """
        try:
            # Extract required fields
            user_id = self._extract_id(raw_data)
            screen_name = self._extract_screen_name(raw_data)
            profile_image_url = self._extract_profile_image(raw_data)

            # Extract optional fields
            followers_count = parse_count_string(raw_data.get("followers_count", 0))
            friends_count = parse_count_string(raw_data.get("friends_count", 0))
            location = raw_data.get("location")
            description = raw_data.get("description")
            verified = bool(raw_data.get("verified", False))
            verified_reason = raw_data.get("verified_reason")

            return User(
                id=user_id,
                screen_name=screen_name,
                profile_image_url=profile_image_url,
                followers_count=followers_count,
                friends_count=friends_count,
                location=location,
                description=description,
                verified=verified,
                verified_reason=verified_reason,
            )

        except (KeyError, ValueError, TypeError) as e:
            self._logger.error(f"Failed to parse user data: {e}")
            raise ParseError(f"Invalid user data: {e}")

    def _extract_id(self, data: dict[str, Any]) -> int:
        """Extract and validate user ID"""
        user_id = data.get("id")
        if not user_id:
            raise ValueError("Missing user ID")
        return int(user_id)

    def _extract_screen_name(self, data: dict[str, Any]) -> str:
        """Extract and validate screen name"""
        name = data.get("screen_name")
        if not name:
            raise ValueError("Missing screen name")
        return str(name).strip()

    def _extract_profile_image(self, data: dict[str, Any]) -> str:
        """Extract profile image URL"""
        # Try avatar_hd first, fallback to profile_image_url
        url = data.get("avatar_hd") or data.get("profile_image_url")
        if not url:
            raise ValueError("Missing profile image URL")
        return str(url)
