"""
API integration tests for the clean architecture
"""

import pytest

from weibo_api import WeiboClient, WeiboConfig
from weibo_api.exceptions import WeiboError, AuthError, NetworkError, ParseError


@pytest.mark.asyncio
class TestWeiboApiIntegration:
    """Integration tests that make real API calls"""
    
    async def test_get_user_success(self):
        """Test getting user information with real API"""
        async with WeiboClient() as client:
            try:
                user = await client.get_user("1749127163")  # 雷军
                assert user.id == 1749127163
                assert user.screen_name == "雷军"
                assert user.profile_image_url
                assert user.followers_count > 0
                print(f"✅ Got user: {user.screen_name}")
            except (AuthError, NetworkError) as e:
                pytest.skip(f"API call failed (expected in CI): {e}")
    
    async def test_get_user_posts_success(self):
        """Test getting user posts with real API"""
        async with WeiboClient() as client:
            try:
                posts = await client.get_user_posts("1749127163", page=1)
                assert len(posts) > 0
                
                first_post = posts[0]
                assert first_post.id > 0
                assert first_post.text
                assert first_post.user.id == 1749127163
                print(f"✅ Got {len(posts)} posts")
            except (AuthError, NetworkError) as e:
                pytest.skip(f"API call failed (expected in CI): {e}")
    
    async def test_get_post_detail_success(self):
        """Test getting post details with real API"""
        async with WeiboClient() as client:
            try:
                # First get a post ID from timeline
                posts = await client.get_user_posts("1749127163", page=1)
                if not posts:
                    pytest.skip("No posts found")
                
                post_id = str(posts[0].id)
                detail = await client.get_post(post_id)
                
                assert detail.id == posts[0].id
                assert detail.text
                assert detail.user.id == 1749127163
                print(f"✅ Got post detail: {detail.text[:50]}...")
            except (AuthError, NetworkError) as e:
                pytest.skip(f"API call failed (expected in CI): {e}")
    
    async def test_get_post_comments_success(self):
        """Test getting post comments with real API"""
        async with WeiboClient() as client:
            try:
                # First get a post ID from timeline
                posts = await client.get_user_posts("1749127163", page=1)
                if not posts:
                    pytest.skip("No posts found")
                
                post_id = str(posts[0].id)
                comments = await client.get_post_comments(post_id)
                
                # Comments might be empty, that's OK
                if comments:
                    first_comment = comments[0]
                    assert first_comment.id > 0
                    assert first_comment.text
                    assert first_comment.user.id > 0
                    print(f"✅ Got {len(comments)} comments")
                else:
                    print("✅ No comments found (OK)")
            except (AuthError, NetworkError) as e:
                pytest.skip(f"API call failed (expected in CI): {e}")
    
    async def test_error_handling_invalid_user(self):
        """Test error handling with invalid user ID"""
        async with WeiboClient() as client:
            try:
                with pytest.raises((NetworkError, ParseError)):
                    await client.get_user("0")  # Invalid user ID
            except (AuthError, NetworkError) as e:
                pytest.skip(f"API call failed (expected in CI): {e}")
    
    async def test_client_with_custom_config(self):
        """Test client with custom configuration"""
        config = WeiboConfig.create_fast()
        async with WeiboClient(config=config) as client:
            assert client._config.http.timeout == 5.0
            assert client._config.http.max_retries == 1
            
            try:
                user = await client.get_user("1749127163")
                assert user.id == 1749127163
                print("✅ Fast config works")
            except (AuthError, NetworkError) as e:
                pytest.skip(f"API call failed (expected in CI): {e}")


@pytest.mark.asyncio
class TestClientEdgeCases:
    """Test edge cases and error conditions"""
    
    async def test_client_context_manager_multiple_times(self):
        """Test using client context manager multiple times"""
        config = WeiboConfig.create_fast()
        
        # First use
        async with WeiboClient(config=config) as client1:
            assert client1 is not None
        
        # Second use should work fine
        async with WeiboClient(config=config) as client2:
            assert client2 is not None
            assert client2 is not client1  # Different instances
    
    async def test_client_without_context_manager(self):
        """Test client usage without context manager"""
        client = WeiboClient()
        # Should be able to create client
        assert client is not None
        
        # But HTTP client won't be initialized until context manager
        assert client._http_client._client is None