"""
Integration tests for session management functionality.
"""

import pytest
import asyncio
import tempfile
import os
import time

from multi_browser_crawler import BrowserCrawler, BrowserConfig
from multi_browser_crawler.core.session_manager import SessionManager


@pytest.mark.integration
@pytest.mark.browser
class TestSessionManagement:
    """Integration tests for session management."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield BrowserConfig(
                headless=True,
                max_sessions=3,
                data_folder=temp_dir,
                fetch_limit=50
            )
    
    @pytest.mark.asyncio
    async def test_session_creation_and_isolation(self, config):
        """Test session creation and isolation."""
        async with BrowserCrawler(config) as crawler:
            # Create multiple sessions
            result1 = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="test_session_1"
            )
            
            result2 = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="test_session_2"
            )
            
            assert result1.success is True
            assert result2.success is True
            
            # Sessions should have different IDs
            session1_id = result1.metadata.get('session_id')
            session2_id = result2.metadata.get('session_id')
            
            assert session1_id is not None
            assert session2_id is not None
            assert session1_id != session2_id
    
    @pytest.mark.asyncio
    async def test_session_reuse(self, config):
        """Test session reuse functionality."""
        async with BrowserCrawler(config) as crawler:
            # First request with named session
            result1 = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="reuse_session"
            )
            
            # Second request with same session name
            result2 = await crawler.fetch(
                "https://httpbin.org/json",
                session_name="reuse_session"
            )
            
            assert result1.success is True
            assert result2.success is True
            
            # Should reuse the same session
            session1_id = result1.metadata.get('session_id')
            session2_id = result2.metadata.get('session_id')
            
            assert session1_id == session2_id
    
    @pytest.mark.asyncio
    async def test_session_limits(self, config):
        """Test session limits enforcement."""
        # Set a low session limit for testing
        config.max_sessions = 2
        
        async with BrowserCrawler(config) as crawler:
            # Create sessions up to the limit
            results = []
            for i in range(3):  # Try to create more than the limit
                try:
                    result = await crawler.fetch(
                        "https://httpbin.org/html",
                        session_name=f"limit_session_{i}"
                    )
                    results.append(result)
                except Exception as e:
                    # Should handle session limit gracefully
                    assert "limit" in str(e).lower() or "maximum" in str(e).lower()
            
            # Should have created at least some sessions
            successful_results = [r for r in results if r.success]
            assert len(successful_results) >= 1
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self, config):
        """Test session cleanup functionality."""
        async with BrowserCrawler(config) as crawler:
            # Create a session
            result = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="cleanup_session"
            )
            
            assert result.success is True
            
            # Get session stats before cleanup
            stats_before = await crawler.get_stats()
            active_before = stats_before.get('active_sessions', 0)
            
            # Cleanup specific session
            cleanup_success = await crawler.cleanup_session("cleanup_session")
            assert cleanup_success is True
            
            # Get session stats after cleanup
            stats_after = await crawler.get_stats()
            active_after = stats_after.get('active_sessions', 0)
            
            # Should have fewer active sessions
            assert active_after <= active_before
    
    @pytest.mark.asyncio
    async def test_session_directory_structure(self, config):
        """Test session directory structure."""
        async with BrowserCrawler(config) as crawler:
            # Create a session
            result = await crawler.fetch(
                "https://httpbin.org/html",
                session_name="directory_test"
            )
            
            assert result.success is True
            
            # Check that session directory was created
            sessions_dir = os.path.join(config.data_folder, "browser_sessions")
            assert os.path.exists(sessions_dir)
            
            # Should have session directories
            session_dirs = [d for d in os.listdir(sessions_dir) 
                          if d.startswith("session_") and os.path.isdir(os.path.join(sessions_dir, d))]
            assert len(session_dirs) > 0
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, config):
        """Test session persistence across requests."""
        async with BrowserCrawler(config) as crawler:
            # Make multiple requests with the same session
            session_name = "persistent_session"
            
            for i in range(3):
                result = await crawler.fetch(
                    f"https://httpbin.org/json",
                    session_name=session_name
                )
                
                assert result.success is True
                
                # All should use the same session ID
                if i == 0:
                    first_session_id = result.metadata.get('session_id')
                else:
                    current_session_id = result.metadata.get('session_id')
                    assert current_session_id == first_session_id
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, config):
        """Test concurrent session operations."""
        async with BrowserCrawler(config) as crawler:
            # Create multiple concurrent sessions
            tasks = []
            for i in range(3):
                task = crawler.fetch(
                    "https://httpbin.org/html",
                    session_name=f"concurrent_session_{i}"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), f"Task {i} failed: {result}"
                assert result.success is True
            
            # All should have different session IDs
            session_ids = [r.metadata.get('session_id') for r in results]
            assert len(set(session_ids)) == len(session_ids)  # All unique
    
    @pytest.mark.asyncio
    async def test_session_stats(self, config):
        """Test session statistics."""
        async with BrowserCrawler(config) as crawler:
            # Create some sessions
            await crawler.fetch("https://httpbin.org/html", session_name="stats_session_1")
            await crawler.fetch("https://httpbin.org/json", session_name="stats_session_2")
            
            # Get stats
            stats = await crawler.get_stats()
            
            assert isinstance(stats, dict)
            assert 'total_sessions' in stats
            assert 'active_sessions' in stats
            assert 'current_session' in stats
            assert 'fetch_count' in stats
            
            # Should have created sessions
            assert stats['total_sessions'] >= 2
            assert stats['active_sessions'] >= 2
            assert stats['fetch_count'] >= 2


@pytest.mark.integration
class TestSessionManagerDirect:
    """Direct tests for SessionManager class."""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield SessionManager(data_folder=temp_dir, max_sessions=3)
    
    def test_session_manager_initialization(self, session_manager):
        """Test session manager initialization."""
        assert session_manager.data_folder is not None
        assert session_manager.sessions_folder is not None
        assert session_manager.MAX_CONCURRENT_SESSIONS == 3
        assert os.path.exists(session_manager.sessions_folder)
    
    def test_session_id_creation(self, session_manager):
        """Test session ID creation."""
        # Test named session
        session_id1 = session_manager.create_session_id("test_session")
        session_id2 = session_manager.create_session_id("test_session")
        
        # Same name should produce same ID (for reuse)
        assert session_id1 == session_id2
        
        # Different names should produce different IDs
        session_id3 = session_manager.create_session_id("different_session")
        assert session_id1 != session_id3
        
        # Force unique should always be different
        unique_id1 = session_manager.create_session_id("test", force_unique=True)
        unique_id2 = session_manager.create_session_id("test", force_unique=True)
        assert unique_id1 != unique_id2
    
    def test_session_directory_creation(self, session_manager):
        """Test session directory creation."""
        session_id = "test_session_123"
        
        # Create directory
        session_dir = session_manager.get_session_directory(session_id, create=True)
        
        assert os.path.exists(session_dir)
        assert session_id in session_dir
        
        # Get without creating
        session_dir2 = session_manager.get_session_directory(session_id, create=False)
        assert session_dir == session_dir2
    
    def test_session_registration(self, session_manager):
        """Test session registration."""
        session_id = "test_registration"
        pid = 12345
        session_name = "test_session"
        
        # Register session
        session_info = session_manager.register_session(session_id, pid, session_name)
        
        assert session_info['session_id'] == session_id
        assert session_info['pid'] == pid
        assert session_info['session_name'] == session_name
        assert 'created_at' in session_info
        assert 'last_used' in session_info
        assert 'user_data_dir' in session_info
        
        # Should be in registry
        assert session_id in session_manager.registry['sessions']
    
    def test_session_strategy(self, session_manager):
        """Test session strategy."""
        session_name = "strategy_test"
        
        # First call should create new session
        session_id1, user_data_dir1, is_new1 = session_manager.get_session_strategy(session_name)
        
        assert is_new1 is True
        assert session_id1 is not None
        assert user_data_dir1 is not None
        assert os.path.exists(user_data_dir1)
        
        # Register the session (simulate browser creation)
        session_manager.register_session(session_id1, 12345, session_name)
        
        # Second call should reuse existing session
        session_id2, user_data_dir2, is_new2 = session_manager.get_session_strategy(session_name)
        
        assert is_new2 is False
        assert session_id2 == session_id1
        assert user_data_dir2 == user_data_dir1
    
    def test_session_listing(self, session_manager):
        """Test session listing."""
        # Register some sessions
        session_manager.register_session("session1", 11111, "test1")
        session_manager.register_session("session2", 22222, "test2")
        
        # List sessions
        sessions = session_manager.list_sessions()
        
        assert len(sessions) == 2
        
        for session in sessions:
            assert 'session_id' in session
            assert 'session_name' in session
            assert 'pid' in session
            assert 'is_active' in session
            assert 'age_hours' in session
            assert 'last_used_hours' in session
    
    def test_session_cleanup(self, session_manager):
        """Test session cleanup."""
        # Register a session
        session_id = "cleanup_test"
        session_manager.register_session(session_id, 99999, "cleanup")

        # Unregister session
        session_manager.unregister_session(session_id, cleanup_directory=True)

        # Should be removed from registry
        assert session_id not in session_manager.registry['sessions']

    def test_dead_process_detection(self, session_manager):
        """Test detection and cleanup of dead processes."""
        # Create a session ID with a fake PID that doesn't exist
        session_name = "dead_process_test"
        fake_pid = 999999  # Very unlikely to exist

        # Create session ID and register with fake PID
        session_id = session_manager.create_session_id(session_name)
        user_data_dir = session_manager.get_session_directory(session_id)
        session_manager.register_session(session_id, user_data_dir, fake_pid)

        # Verify session is registered
        assert session_id in session_manager.registry["sessions"]

        # Try to get the same session again - should detect dead process
        new_session_id, new_user_data_dir, is_new = session_manager.get_session_strategy(session_name)

        # Should reuse the same ID but treat as new since process is dead
        assert new_session_id == session_id
        assert is_new is True

    def test_session_conflict_resolution(self, session_manager):
        """Test session ID conflict resolution."""
        # Create multiple sessions with the same name
        session_id1 = session_manager.create_session_id("conflict_test")
        session_id2 = session_manager.create_session_id("conflict_test", force_unique=True)

        # Should have different IDs when force_unique is True
        assert session_id1 != session_id2
        assert "conflict_test" in session_id1
        assert "conflict_test" in session_id2
