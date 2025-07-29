import os
import tempfile
import time

import pytest

from app.lock_manager import SQLiteLockManager


class TestSQLiteLockManager:
    """Test the SQLite-based lock manager"""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        try:
            os.unlink(db_path)
        except OSError:
            pass

    @pytest.fixture
    def lock_manager(self, temp_db_path):
        """Create a lock manager instance with temporary database"""
        return SQLiteLockManager(db_path=temp_db_path)

    def test_init_creates_database(self, temp_db_path):
        """Test that initialization creates the database and table"""
        lock_manager = SQLiteLockManager(db_path=temp_db_path)

        # Check that the database file exists
        assert os.path.exists(temp_db_path)

        # Check that the locks table exists by trying to acquire a lock
        result = lock_manager.try_acquire_lock("test", 123, 60)
        assert result is True

    def test_try_acquire_lock_success(self, lock_manager):
        """Test successful lock acquisition"""
        result = lock_manager.try_acquire_lock("test_lock", 123, 60)
        assert result is True

        # Verify lock info
        lock_info = lock_manager.get_lock_info("test_lock")
        assert lock_info is not None
        assert lock_info["worker_pid"] == 123
        assert lock_info["age_seconds"] >= 0

    def test_try_acquire_lock_already_held(self, lock_manager):
        """Test that second attempt to acquire same lock fails"""
        # First worker acquires the lock
        result1 = lock_manager.try_acquire_lock("test_lock", 123, 60)
        assert result1 is True

        # Second worker tries to acquire the same lock
        result2 = lock_manager.try_acquire_lock("test_lock", 456, 60)
        assert result2 is False

    def test_release_lock_success(self, lock_manager):
        """Test successful lock release"""
        # Acquire the lock
        lock_manager.try_acquire_lock("test_lock", 123, 60)

        # Release the lock
        result = lock_manager.release_lock("test_lock", 123)
        assert result is True

        # Verify lock is gone
        lock_info = lock_manager.get_lock_info("test_lock")
        assert lock_info is None

    def test_release_lock_not_held(self, lock_manager):
        """Test releasing a lock that wasn't held"""
        result = lock_manager.release_lock("test_lock", 123)
        assert result is False

    def test_release_lock_wrong_worker(self, lock_manager):
        """Test releasing a lock held by a different worker"""
        # Worker 123 acquires the lock
        lock_manager.try_acquire_lock("test_lock", 123, 60)

        # Worker 456 tries to release it
        result = lock_manager.release_lock("test_lock", 456)
        assert result is False

        # Lock should still be held by worker 123
        lock_info = lock_manager.get_lock_info("test_lock")
        assert lock_info is not None
        assert lock_info["worker_pid"] == 123

    def test_get_lock_info_nonexistent(self, lock_manager):
        """Test getting info for a lock that doesn't exist"""
        lock_info = lock_manager.get_lock_info("nonexistent_lock")
        assert lock_info is None

    def test_get_lock_info_existing(self, lock_manager):
        """Test getting info for an existing lock"""
        # Acquire a lock
        lock_manager.try_acquire_lock("test_lock", 123, 60)

        # Get lock info
        lock_info = lock_manager.get_lock_info("test_lock")
        assert lock_info is not None
        assert lock_info["worker_pid"] == 123
        assert lock_info["acquired_at"] > 0
        assert lock_info["expires_at"] > lock_info["acquired_at"]
        assert lock_info["age_seconds"] >= 0

    def test_cleanup_expired_locks(self, lock_manager):
        """Test that expired locks are cleaned up"""
        # Acquire a lock with very short timeout
        lock_manager.try_acquire_lock("test_lock", 123, 1)

        # Wait for the lock to expire
        time.sleep(1.1)

        # Try to acquire the same lock again - should succeed because expired lock was cleaned up
        result = lock_manager.try_acquire_lock("test_lock", 456, 60)
        assert result is True

    def test_multiple_locks(self, lock_manager):
        """Test that multiple different locks can be held simultaneously"""
        # Acquire multiple different locks
        result1 = lock_manager.try_acquire_lock("lock1", 123, 60)
        result2 = lock_manager.try_acquire_lock("lock2", 456, 60)
        result3 = lock_manager.try_acquire_lock("lock3", 789, 60)

        assert result1 is True
        assert result2 is True
        assert result3 is True

        # Verify all locks exist
        assert lock_manager.get_lock_info("lock1") is not None
        assert lock_manager.get_lock_info("lock2") is not None
        assert lock_manager.get_lock_info("lock3") is not None

    def test_lock_timeout(self, lock_manager):
        """Test that locks expire after timeout"""
        # Acquire a lock with short timeout
        lock_manager.try_acquire_lock("test_lock", 123, 1)

        # Wait for expiration
        time.sleep(1.1)

        # Lock should be cleaned up and available again
        result = lock_manager.try_acquire_lock("test_lock", 456, 60)
        assert result is True

    def test_database_error_handling(self, lock_manager):
        """Test handling of database errors"""
        # Mock a database error by using an invalid path
        bad_lock_manager = SQLiteLockManager(db_path="/invalid/path/db.sqlite")

        # These should not raise exceptions but return False
        result = bad_lock_manager.try_acquire_lock("test", 123, 60)
        assert result is False

        result = bad_lock_manager.release_lock("test", 123)
        assert result is False

        info = bad_lock_manager.get_lock_info("test")
        assert info is None

    def test_concurrent_access_simulation(self, lock_manager):
        """Test simulating concurrent access from multiple workers"""
        # Simulate multiple workers trying to acquire the same lock
        results = []
        for worker_pid in [100, 101, 102, 103, 104]:
            result = lock_manager.try_acquire_lock("scraper", worker_pid, 60)
            results.append(result)

        # Only one should succeed
        assert sum(results) == 1

        # The successful worker should be able to release the lock
        successful_worker = [
            pid
            for pid, result in zip([100, 101, 102, 103, 104], results)
            if result
        ][0]
        release_result = lock_manager.release_lock(
            "scraper", successful_worker
        )
        assert release_result is True

    def test_lock_info_accuracy(self, lock_manager):
        """Test that lock info is accurate"""
        # Acquire a lock
        start_time = time.time()
        lock_manager.try_acquire_lock("test_lock", 123, 60)

        # Get lock info
        lock_info = lock_manager.get_lock_info("test_lock")

        # Verify timing is reasonable
        assert lock_info["acquired_at"] >= start_time
        assert lock_info["acquired_at"] <= time.time()
        assert lock_info["expires_at"] == lock_info["acquired_at"] + 60
        assert lock_info["age_seconds"] >= 0
        assert lock_info["age_seconds"] <= 1  # Should be very recent


class TestGlobalLockManager:
    """Test the global lock manager instance"""

    def test_global_instance_exists(self):
        """Test that the global lock manager instance exists"""
        from app.lock_manager import lock_manager

        assert lock_manager is not None
        assert isinstance(lock_manager, SQLiteLockManager)

    def test_global_instance_singleton(self):
        """Test that the global instance is a singleton"""
        from app.lock_manager import lock_manager
        from app.lock_manager import lock_manager as lock_manager2

        assert lock_manager is lock_manager2
        assert lock_manager.db_path == lock_manager2.db_path
