"""
Modern Weibo API Client

Simple, clean, focused API for Weibo data extraction.

Example:
    async with WeiboClient() as client:
        user = await client.get_user("123456")
        posts = await client.get_user_posts("123456")
        comments = await client.get_post_comments("456789")
"""

from .config import WeiboConfig
from .exceptions import AuthError, NetworkError, ParseError, WeiboError
from .models import Comment, Image, Post, User, Video
from .utils import parse_count_string, validate_user_id
from .weibo_client import WeiboClient

__version__ = "2.0.0"
__author__ = "Linus Torvalds"
__description__ = "Simple, focused Weibo API client"

__all__ = [
    # Main client
    "WeiboClient",
    # Configuration
    "WeiboConfig",
    # Data models
    "User",
    "Post",
    "Comment",
    "Image",
    "Video",
    # Exceptions
    "WeiboError",
    "AuthError",
    "NetworkError",
    "ParseError",
    # Utilities
    "validate_user_id",
    "parse_count_string",
]
