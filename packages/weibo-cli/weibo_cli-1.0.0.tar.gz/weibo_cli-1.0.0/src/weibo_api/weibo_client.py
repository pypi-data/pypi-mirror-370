"""
Simple Weibo API client facade

Clean, focused interface that does what you need.
No dependency injection, no complex configuration.
Just works.
"""

import logging

from .config import WeiboConfig
from .core.auth import CookieManager
from .core.client import HttpClient
from .core.retry import RetryStrategy
from .exceptions import WeiboError
from .models.entities import Comment, Post, User
from .parsers import CommentParser, PostParser, UserParser
from .utils import validate_user_id


class WeiboClient:
    """Simple Weibo API client

    Easy to use facade for Weibo API operations.
    Handles authentication, retries, and parsing automatically.

    Example:
        async with WeiboClient() as client:
            user = await client.get_user("123456")
            posts = await client.get_user_posts("123456")
    """

    def __init__(
        self,
        cookies: str | None = None,
        config: WeiboConfig | None = None,
        logger: logging.Logger | None = None,
    ):
        self._config = config or WeiboConfig()
        self._logger = logger or logging.getLogger(__name__)

        # Initialize components
        self._http_client = HttpClient(
            timeout=self._config.http.timeout,
            max_connections=self._config.http.max_connections,
            max_keepalive_connections=self._config.http.max_keepalive_connections,
            logger=self._logger,
        )

        self._cookie_manager = CookieManager(
            http_client=self._http_client,
            ttl=self._config.auth.cookie_ttl,
            user_agent=self._config.api.user_agent,
            logger=self._logger,
        )

        self._retry_strategy = RetryStrategy(
            max_attempts=self._config.http.max_retries,
            base_delay=self._config.http.base_delay,
            max_delay=self._config.http.max_delay,
            logger=self._logger,
        )

        # Initialize parsers
        self._user_parser = UserParser(self._logger)
        self._post_parser = PostParser(self._logger)
        self._comment_parser = CommentParser(self._logger)

        # Set initial cookies if provided
        if cookies:
            self._cookie_manager.set_cookies(cookies)

    async def __aenter__(self) -> "WeiboClient":
        await self._http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._http_client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_user(self, user_id: str) -> User:
        """Get user profile

        Args:
            user_id: User ID to fetch

        Returns:
            User entity with profile information

        Raises:
            WeiboError: When request fails or data is invalid
        """
        # Validate user_id format
        user_id = validate_user_id(user_id)

        async def fetch_user() -> User:
            cookies = await self._cookie_manager.ensure_valid_cookies()
            headers = {
                "Cookie": cookies,
                "User-Agent": self._config.api.user_agent,
                "Referer": "https://weibo.com/",
            }

            url = f"{self._config.api.base_url}/ajax/profile/info?uid={user_id}"
            response = await self._http_client.get_json(url, headers)

            if response.get("ok") != 1:
                raise WeiboError(f"API returned error: {response}")

            user_data = response.get("data", {}).get("user", {})
            if not user_data:
                raise WeiboError("No user data in response")

            return self._user_parser.parse(user_data)

        return await self._retry_strategy.execute(fetch_user)

    async def get_user_posts(self, user_id: str, page: int = 1) -> list[Post]:
        """Get user's posts (timeline)

        Args:
            user_id: User ID to fetch posts for
            page: Page number (default 1)

        Returns:
            List of Post entities

        Raises:
            WeiboError: When request fails or data is invalid
        """
        # Validate user_id format
        user_id = validate_user_id(user_id)

        async def fetch_posts() -> list[Post]:
            cookies = await self._cookie_manager.ensure_valid_cookies()
            headers = {
                "Cookie": cookies,
                "User-Agent": self._config.api.user_agent,
                "Referer": "https://weibo.com/",
            }

            url = f"{self._config.api.base_url}/ajax/statuses/mymblog?uid={user_id}&page={page}"
            response = await self._http_client.get_json(url, headers)

            if response.get("ok") != 1:
                raise WeiboError(f"API returned error: {response}")

            posts_data = response.get("data", {}).get("list", [])
            posts = []
            total_posts = len(posts_data)
            failed_posts = 0

            for post_data in posts_data:
                try:
                    post = self._post_parser.parse(post_data)
                    posts.append(post)
                except ParseError as e:
                    failed_posts += 1
                    self._logger.warning(f"Skipping post with invalid data: {e}")
                except (KeyError, ValueError, TypeError) as e:
                    failed_posts += 1
                    self._logger.warning(f"Skipping post with malformed data: {e}")

            # Log parsing statistics
            success_rate = (
                ((total_posts - failed_posts) / total_posts * 100)
                if total_posts > 0
                else 100
            )
            self._logger.info(
                f"Posts parsed: {len(posts)}/{total_posts} ({success_rate:.1f}% success)"
            )

            return posts

        return await self._retry_strategy.execute(fetch_posts)

    async def get_post(self, post_id: str) -> Post:
        """Get post details

        Args:
            post_id: Post ID to fetch

        Returns:
            Post entity with full details

        Raises:
            WeiboError: When request fails or data is invalid
        """

        async def fetch_post() -> Post:
            url = f"{self._config.api.mobile_url}/detail/{post_id}"
            headers = {}  # No cookies needed for detail page

            html_content = await self._http_client.get_text(url, headers)
            return self._post_parser.parse_detail_page(html_content)

        return await self._retry_strategy.execute(fetch_post)

    async def get_post_comments(self, post_id: str) -> list[Comment]:
        """Get post comments

        Args:
            post_id: Post ID to fetch comments for

        Returns:
            List of Comment entities

        Raises:
            WeiboError: When request fails or data is invalid
        """

        async def fetch_comments() -> list[Comment]:
            cookies = await self._cookie_manager.ensure_valid_cookies()
            headers = {
                "Cookie": cookies,
                "User-Agent": self._config.api.user_agent,
                "Referer": "https://weibo.com/",
            }

            url = f"{self._config.api.mobile_url}/comments/hotflow?mid={post_id}"
            response = await self._http_client.get_json(url, headers)

            if response.get("ok") != 1:
                raise WeiboError(f"API returned error: {response}")

            comments_data = response.get("data", {}).get("data", [])
            comments = []
            total_comments = len(comments_data)
            failed_comments = 0

            for comment_data in comments_data:
                try:
                    comment = self._comment_parser.parse(comment_data)
                    comments.append(comment)
                except ParseError as e:
                    failed_comments += 1
                    self._logger.warning(f"Skipping comment with invalid data: {e}")
                except (KeyError, ValueError, TypeError) as e:
                    failed_comments += 1
                    self._logger.warning(f"Skipping comment with malformed data: {e}")

            # Log parsing statistics
            success_rate = (
                ((total_comments - failed_comments) / total_comments * 100)
                if total_comments > 0
                else 100
            )
            self._logger.info(
                f"Comments parsed: {len(comments)}/{total_comments} ({success_rate:.1f}% success)"
            )

            return comments

        return await self._retry_strategy.execute(fetch_comments)
