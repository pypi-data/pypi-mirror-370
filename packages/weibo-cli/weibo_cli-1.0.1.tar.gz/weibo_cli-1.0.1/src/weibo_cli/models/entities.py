"""
Business entities

Simple dataclasses for business objects.
Clear, focused models without complex validation logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class User:
    """Weibo user entity"""

    id: int
    screen_name: str
    profile_image_url: str
    followers_count: int = 0
    friends_count: int = 0
    location: Optional[str] = None
    description: Optional[str] = None
    verified: bool = False
    verified_reason: Optional[str] = None


@dataclass
class Image:
    """Weibo image attachment"""

    id: str
    thumbnail_url: str
    large_url: str
    original_url: str
    width: int = 0
    height: int = 0


@dataclass
class Video:
    """Weibo video attachment"""

    duration: float = 0.0
    play_count: int = 0
    urls: Dict[str, str] = field(default_factory=dict)  # quality -> url mapping


@dataclass
class Post:
    """Weibo post entity"""

    id: int
    created_at: datetime
    text: str
    user: User
    text_raw: Optional[str] = None
    region_name: Optional[str] = None
    source: Optional[str] = None
    reposts_count: int = 0
    comments_count: int = 0
    attitudes_count: int = 0
    images: List[Image] = field(default_factory=list)
    video: Optional[Video] = None


@dataclass
class Comment:
    """Weibo comment entity"""

    id: int
    created_at: datetime
    text: str
    user: User
    rootid: int = 0
    floor_number: int = 0
    like_count: int = 0
