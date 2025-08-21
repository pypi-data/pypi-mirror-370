"""
Clean configuration classes

No backward compatibility, just what we need.
"""

from dataclasses import dataclass, field
import re


@dataclass
class HttpConfig:
    """HTTP client configuration"""

    timeout: float = 10.0
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    max_connections: int = 20
    max_keepalive_connections: int = 5

    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.base_delay < 0:
            raise ValueError("base_delay must be >= 0")


@dataclass
class AuthConfig:
    """Authentication configuration"""

    cookie_ttl: float = 300.0  # 5 minutes

    def __post_init__(self):
        if self.cookie_ttl < 0:
            raise ValueError("cookie_ttl must be >= 0")


@dataclass
class ApiConfig:
    """API endpoint configuration"""

    base_url: str = "https://weibo.com"
    mobile_url: str = "https://m.weibo.cn"
    visitor_url: str = "https://passport.weibo.com/visitor/genvisitor2"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def __post_init__(self):
        if not self.base_url or not isinstance(self.base_url, str):
            raise ValueError("base_url must be a non-empty string")
        if not re.match(r"^https?://", self.base_url):
            raise ValueError("base_url must start with http:// or https://")
        
        if not self.mobile_url or not isinstance(self.mobile_url, str):
            raise ValueError("mobile_url must be a non-empty string")
        if not re.match(r"^https?://", self.mobile_url):
            raise ValueError("mobile_url must start with http:// or https://")
        
        if not self.visitor_url or not isinstance(self.visitor_url, str):
            raise ValueError("visitor_url must be a non-empty string")
        if not re.match(r"^https?://", self.visitor_url):
            raise ValueError("visitor_url must start with http:// or https://")
        
        if not self.user_agent or not isinstance(self.user_agent, str):
            raise ValueError("user_agent must be a non-empty string")
        if len(self.user_agent) < 10:
            raise ValueError("user_agent is too short")
        if len(self.user_agent) > 500:
            raise ValueError("user_agent is too long")


@dataclass
class WeiboConfig:
    """Main configuration container"""

    http: HttpConfig = field(default_factory=HttpConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    api: ApiConfig = field(default_factory=ApiConfig)

    @classmethod
    def create_fast(cls) -> "WeiboConfig":
        """Fast configuration for quick operations"""
        return cls(
            http=HttpConfig(timeout=5.0, max_retries=1, base_delay=0.5),
            auth=AuthConfig(cookie_ttl=120.0),  # 2 minutes
        )

    @classmethod
    def create_conservative(cls) -> "WeiboConfig":
        """Conservative configuration for reliability"""
        return cls(
            http=HttpConfig(timeout=15.0, max_retries=5, base_delay=2.0),
            auth=AuthConfig(cookie_ttl=600.0),  # 10 minutes
        )
