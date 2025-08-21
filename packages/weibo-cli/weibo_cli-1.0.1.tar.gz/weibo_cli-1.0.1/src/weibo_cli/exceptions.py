"""
Clean exception hierarchy

Simple, focused exception types.
"""


class WeiboError(Exception):
    """Base exception for all Weibo API errors"""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthError(WeiboError):
    """Authentication/authorization errors"""

    pass


class NetworkError(WeiboError):
    """Network/HTTP related errors"""

    pass


class ParseError(WeiboError):
    """Data parsing errors"""

    pass
