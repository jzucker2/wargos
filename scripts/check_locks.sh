#!/bin/bash

# Script to check and fix the SQLite lock database

DB_PATH="/tmp/wargos_locks.db"

echo "Checking SQLite lock database: $DB_PATH"

if [ -f "$DB_PATH" ]; then
    echo "Database file exists"

    # Check if the locks table exists
    if sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='locks';" 2>/dev/null | grep -q "locks"; then
        echo "✅ Locks table exists"

        # Show current locks
        echo "Current locks:"
        sqlite3 "$DB_PATH" "SELECT lock_name, worker_pid, acquired_at, expires_at FROM locks;" 2>/dev/null || echo "Error reading locks table"

        # Show expired locks
        echo "Expired locks:"
        sqlite3 "$DB_PATH" "SELECT lock_name, worker_pid, acquired_at, expires_at FROM locks WHERE expires_at < $(date +%s);" 2>/dev/null || echo "Error reading expired locks"

    else
        echo "❌ Locks table does not exist"
        echo "Recreating database..."
        rm -f "$DB_PATH"
        sqlite3 "$DB_PATH" "
            PRAGMA journal_mode=WAL;
            CREATE TABLE locks (
                lock_name TEXT PRIMARY KEY,
                worker_pid INTEGER,
                acquired_at REAL,
                expires_at REAL
            );
        " && echo "✅ Database recreated successfully"
    fi
else
    echo "❌ Database file does not exist"
    echo "Creating new database..."
    sqlite3 "$DB_PATH" "
        PRAGMA journal_mode=WAL;
        CREATE TABLE locks (
            lock_name TEXT PRIMARY KEY,
            worker_pid INTEGER,
            acquired_at REAL,
            expires_at REAL
        );
    " && echo "✅ Database created successfully"
fi
