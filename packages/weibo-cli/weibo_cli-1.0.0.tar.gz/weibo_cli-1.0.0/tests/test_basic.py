"""
Basic tests for the new clean architecture
"""

import pytest

from weibo_api import WeiboClient, WeiboConfig, User, Post, Comment, Image, Video
from weibo_api.exceptions import WeiboError, AuthError, NetworkError, ParseError


class TestBasicImports:
    """Test that all basic imports work"""
    
    def test_main_imports(self):
        """Test main component imports"""
        assert WeiboClient is not None
        assert WeiboConfig is not None
    
    def test_model_imports(self):
        """Test model imports"""
        assert User is not None
        assert Post is not None
        assert Comment is not None
        assert Image is not None
        assert Video is not None
    
    def test_exception_imports(self):
        """Test exception imports"""
        assert WeiboError is not None
        assert AuthError is not None
        assert NetworkError is not None
        assert ParseError is not None


class TestConfig:
    """Test configuration classes"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = WeiboConfig()
        assert config.http.timeout == 10.0
        assert config.auth.cookie_ttl == 300.0
        assert config.api.base_url == "https://weibo.com"
    
    def test_fast_config(self):
        """Test fast configuration"""
        config = WeiboConfig.create_fast()
        assert config.http.timeout == 5.0
        assert config.http.max_retries == 1
        assert config.auth.cookie_ttl == 120.0
    
    def test_conservative_config(self):
        """Test conservative configuration"""
        config = WeiboConfig.create_conservative()
        assert config.http.timeout == 15.0
        assert config.http.max_retries == 5
        assert config.auth.cookie_ttl == 600.0


class TestModels:
    """Test basic model creation"""
    
    def test_user_creation(self):
        """Test User model creation"""
        user = User(
            id=123,
            screen_name="Test User",
            profile_image_url="https://example.com/avatar.jpg"
        )
        assert user.id == 123
        assert user.screen_name == "Test User"
        assert user.verified is False
    
    def test_image_creation(self):
        """Test Image model creation"""
        image = Image(
            id="img123",
            thumbnail_url="https://example.com/thumb.jpg",
            large_url="https://example.com/large.jpg",
            original_url="https://example.com/original.jpg"
        )
        assert image.id == "img123"
        assert image.width == 0  # default
        assert image.height == 0  # default
    
    def test_video_creation(self):
        """Test Video model creation"""
        video = Video(
            duration=120.5,
            play_count=1000
        )
        assert video.duration == 120.5
        assert video.play_count == 1000
        assert video.urls == {}  # default


@pytest.mark.asyncio
class TestClientBasics:
    """Test basic client functionality"""
    
    async def test_client_context_manager(self):
        """Test client can be used as context manager"""
        async with WeiboClient() as client:
            assert client is not None
            assert hasattr(client, 'get_user')
            assert hasattr(client, 'get_user_posts')
            assert hasattr(client, 'get_post')
            assert hasattr(client, 'get_post_comments')
    
    async def test_client_with_config(self):
        """Test client creation with custom config"""
        config = WeiboConfig.create_fast()
        async with WeiboClient(config=config) as client:
            assert client._config.http.timeout == 5.0