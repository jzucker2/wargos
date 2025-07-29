import logging
import os
import sqlite3
import time
from typing import Optional

log = logging.getLogger(__name__)


class SQLiteLockManager:
    """SQLite-based lock manager for coordinating background tasks across multiple workers"""

    def __init__(self, db_path: str = "/tmp/wargos_locks.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_db()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                log.info(f"Created database directory: {db_dir}")
        except Exception as e:
            log.error(f"Failed to create database directory: {e}")

    def _init_db(self):
        """Initialize the SQLite database with the locks table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS locks (
                        lock_name TEXT PRIMARY KEY,
                        worker_pid INTEGER,
                        acquired_at REAL,
                        expires_at REAL
                    )
                """
                )
                conn.commit()
                log.info(f"Initialized SQLite lock database: {self.db_path}")
        except Exception as e:
            log.error(f"Failed to initialize SQLite lock database: {e}")
            # Try to create a new database file if the current one is corrupted
            try:
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                    log.info(
                        f"Removed corrupted database file: {self.db_path}"
                    )
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS locks (
                            lock_name TEXT PRIMARY KEY,
                            worker_pid INTEGER,
                            acquired_at REAL,
                            expires_at REAL
                        )
                    """
                    )
                    conn.commit()
                    log.info(f"Recreated SQLite lock database: {self.db_path}")
            except Exception as recreate_error:
                log.error(
                    f"Failed to recreate SQLite lock database: {recreate_error}"
                )

    def _cleanup_expired_locks(self):
        """Clean up expired locks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                current_time = time.time()
                cursor = conn.execute(
                    "DELETE FROM locks WHERE expires_at < ?", (current_time,)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                if deleted_count > 0:
                    log.debug(f"Cleaned up {deleted_count} expired locks")
        except Exception as e:
            log.error(f"Failed to cleanup expired locks: {e}")

    def try_acquire_lock(
        self, lock_name: str, worker_pid: int, timeout_seconds: int = 300
    ) -> bool:
        """
        Try to acquire a lock atomically

        Args:
            lock_name: Name of the lock
            worker_pid: PID of the worker trying to acquire the lock
            timeout_seconds: How long the lock is valid (default 5 minutes)

        Returns:
            True if lock was acquired, False otherwise
        """
        try:
            self._cleanup_expired_locks()

            with sqlite3.connect(self.db_path) as conn:
                current_time = time.time()
                expires_at = current_time + timeout_seconds

                # Try to insert the lock (will fail if it already exists)
                conn.execute(
                    "INSERT INTO locks (lock_name, worker_pid, acquired_at, expires_at) VALUES (?, ?, ?, ?)",
                    (lock_name, worker_pid, current_time, expires_at),
                )
                conn.commit()

                log.info(f"Worker {worker_pid} acquired lock '{lock_name}'")
                return True

        except sqlite3.IntegrityError:
            # Lock already exists
            log.debug(
                f"Worker {worker_pid} failed to acquire lock '{lock_name}' - already held"
            )
            return False
        except Exception as e:
            log.error(f"Error acquiring lock '{lock_name}': {e}")
            return False

    def release_lock(self, lock_name: str, worker_pid: int) -> bool:
        """
        Release a lock

        Args:
            lock_name: Name of the lock
            worker_pid: PID of the worker that holds the lock

        Returns:
            True if lock was released, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM locks WHERE lock_name = ? AND worker_pid = ?",
                    (lock_name, worker_pid),
                )
                conn.commit()

                if cursor.rowcount > 0:
                    log.info(
                        f"Worker {worker_pid} released lock '{lock_name}'"
                    )
                    return True
                else:
                    log.warning(
                        f"Worker {worker_pid} tried to release lock '{lock_name}' but didn't hold it"
                    )
                    return False

        except Exception as e:
            log.error(f"Error releasing lock '{lock_name}': {e}")
            return False

    def get_lock_info(self, lock_name: str) -> Optional[dict]:
        """Get information about a lock"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT worker_pid, acquired_at, expires_at FROM locks WHERE lock_name = ?",
                    (lock_name,),
                )
                row = cursor.fetchone()

                if row:
                    return {
                        "worker_pid": row[0],
                        "acquired_at": row[1],
                        "expires_at": row[2],
                        "age_seconds": time.time() - row[1] if row[1] else 0,
                    }
                return None

        except Exception as e:
            log.error(f"Error getting lock info for '{lock_name}': {e}")
            return None


# Global lock manager instance
lock_manager = SQLiteLockManager()
