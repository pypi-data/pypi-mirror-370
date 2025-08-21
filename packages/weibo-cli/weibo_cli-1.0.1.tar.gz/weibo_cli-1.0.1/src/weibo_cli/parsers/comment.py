"""
Comment data parser

Parse raw comment data from API responses into Comment entities.
"""

import logging
from datetime import datetime
from typing import Any

from ..exceptions import ParseError
from ..models.entities import Comment, User
from .user import UserParser


class CommentParser:
    """Parse raw comment data into Comment entities

    Responsibilities:
    - Extract comment data from API response
    - Parse nested user data
    - Convert timestamps
    """

    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)
        self._user_parser = UserParser(logger)

    def parse(self, raw_data: dict[str, Any]) -> Comment:
        """Parse raw comment data into Comment entity

        Args:
            raw_data: Raw comment data from API

        Returns:
            Comment entity

        Raises:
            ParseError: When required fields are missing or invalid
        """
        try:
            # Extract required fields
            comment_id = self._extract_id(raw_data)
            created_at = self._extract_created_at(raw_data)
            text = self._extract_text(raw_data)
            user = self._extract_user(raw_data)

            # Extract optional fields
            rootid = int(raw_data.get("rootid", 0))
            floor_number = int(raw_data.get("floor_number", 0))
            like_count = int(raw_data.get("like_count", 0))

            return Comment(
                id=comment_id,
                created_at=created_at,
                text=text,
                rootid=rootid,
                floor_number=floor_number,
                like_count=like_count,
                user=user,
            )

        except (KeyError, ValueError, TypeError) as e:
            self._logger.error(f"Failed to parse comment data: {e}")
            raise ParseError(f"Invalid comment data: {e}")

    def _extract_id(self, data: dict[str, Any]) -> int:
        """Extract and validate comment ID"""
        comment_id = data.get("id")
        if not comment_id:
            raise ValueError("Missing comment ID")
        return int(comment_id)

    def _extract_created_at(self, data: dict[str, Any]) -> datetime:
        """Extract and parse created_at timestamp"""
        created_at = data.get("created_at")
        if not created_at:
            raise ValueError("Missing created_at")

        # Try different datetime formats
        formats = [
            "%a %b %d %H:%M:%S %z %Y",  # Mon Jan 01 12:00:00 +0800 2024
            "%Y-%m-%d %H:%M:%S%z",  # 2025-06-29 06:46:38+08:00
        ]

        for fmt in formats:
            try:
                return datetime.strptime(created_at, fmt)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse timestamp: {created_at}")

    def _extract_text(self, data: dict[str, Any]) -> str:
        """Extract and clean comment text"""
        text = data.get("text", "")
        return str(text).strip()

    def _extract_user(self, data: dict[str, Any]) -> User:
        """Extract user data"""
        user_data = data.get("user")
        if not user_data:
            raise ValueError("Missing user data")

        return self._user_parser.parse(user_data)
