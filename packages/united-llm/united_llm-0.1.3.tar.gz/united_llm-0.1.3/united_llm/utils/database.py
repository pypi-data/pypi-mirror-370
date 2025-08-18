#!/usr/bin/env python3
"""
Database module for logging LLM calls to SQLite.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMCallRecord(BaseModel):
    """Pydantic model for LLM call records"""

    id: Optional[int] = None
    timestamp: datetime
    model: str
    provider: str
    prompt: str
    response: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    search_type: Optional[str] = None  # 'anthropic_web_search', 'duckduckgo_search', or None
    request_schema: Optional[str] = None  # JSON string of the schema used for structured generation


class LLMDatabase:
    """SQLite database for logging LLM calls"""

    def __init__(self, db_path: str):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
        self._create_tables()

    def _ensure_db_exists(self):
        """Ensure the database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn

    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT,
                    token_usage TEXT,  -- JSON string
                    error TEXT,
                    duration_ms INTEGER,
                    search_type TEXT,
                    request_schema TEXT,  -- JSON string of the schema used
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Add request_schema column to existing tables if it doesn't exist
            try:
                conn.execute("ALTER TABLE llm_calls ADD COLUMN request_schema TEXT")
                logger.info("Added request_schema column to existing llm_calls table")
            except sqlite3.OperationalError:
                # Column already exists, which is fine
                pass

            # Create index for faster queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_llm_calls_timestamp
                ON llm_calls(timestamp)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_llm_calls_model
                ON llm_calls(model)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_llm_calls_provider
                ON llm_calls(provider)
            """
            )

    def log_call(self, record: LLMCallRecord) -> int:
        """
        Log an LLM call to the database.

        Args:
            record: LLMCallRecord to log

        Returns:
            The ID of the inserted record
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO llm_calls (
                        timestamp, model, provider, prompt, response,
                        token_usage, error, duration_ms, search_type, request_schema
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        record.timestamp.isoformat(),
                        record.model,
                        record.provider,
                        record.prompt,
                        record.response,
                        json.dumps(record.token_usage) if record.token_usage else None,
                        record.error,
                        record.duration_ms,
                        record.search_type,
                        record.request_schema,
                    ),
                )

                record_id = cursor.lastrowid
                logger.debug(f"Logged LLM call with ID: {record_id}")
                return record_id

        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")
            raise

    def get_calls(
        self,
        limit: int = 100,
        offset: int = 0,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        search_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve LLM calls from the database.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            model: Filter by model name
            provider: Filter by provider
            search_type: Filter by search type
            start_date: Filter calls after this date
            end_date: Filter calls before this date

        Returns:
            List of LLM call records as dictionaries
        """
        try:
            query = """
                SELECT id, timestamp, model, provider, prompt, response,
                       token_usage, error, duration_ms, search_type, request_schema, created_at
                FROM llm_calls
                WHERE 1=1
            """
            params = []

            if model:
                query += " AND model = ?"
                params.append(model)

            if provider:
                query += " AND provider = ?"
                params.append(provider)

            if search_type:
                query += " AND search_type = ?"
                params.append(search_type)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                records = []

                for row in cursor.fetchall():
                    record = dict(row)
                    # Parse JSON fields
                    if record["token_usage"]:
                        record["token_usage"] = json.loads(record["token_usage"])

                    # Convert timestamp string back to datetime object
                    if record["timestamp"]:
                        try:
                            record["timestamp"] = datetime.fromisoformat(record["timestamp"])
                        except ValueError:
                            # Fallback for older timestamp formats
                            record["timestamp"] = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")

                    # Convert created_at string to datetime if present
                    if record.get("created_at"):
                        try:
                            record["created_at"] = datetime.fromisoformat(record["created_at"])
                        except ValueError:
                            # Fallback for older timestamp formats
                            record["created_at"] = datetime.strptime(record["created_at"], "%Y-%m-%d %H:%M:%S")

                    # Parse tokens_used from token_usage if available
                    if record.get("token_usage") and isinstance(record["token_usage"], dict):
                        record["tokens_used"] = record["token_usage"].get(
                            "total_tokens", record["token_usage"].get("total", 0)
                        )
                    else:
                        record["tokens_used"] = None

                    records.append(record)

                return records

        except Exception as e:
            logger.error(f"Failed to retrieve LLM calls: {e}")
            raise

    def get_call_by_id(self, call_id: int) -> Optional[LLMCallRecord]:
        """
        Get a specific LLM call by ID.

        Args:
            call_id: The ID of the call to retrieve

        Returns:
            LLMCallRecord if found, None otherwise
        """
        try:
            query = """
                SELECT id, timestamp, model, provider, prompt, response,
                       token_usage, error, duration_ms, search_type, request_schema, created_at
                FROM llm_calls
                WHERE id = ?
            """

            with self._get_connection() as conn:
                cursor = conn.execute(query, (call_id,))
                row = cursor.fetchone()

                if not row:
                    return None

                record = dict(row)

                # Parse JSON fields
                if record["token_usage"]:
                    record["token_usage"] = json.loads(record["token_usage"])

                # Convert timestamp string back to datetime object
                if record["timestamp"]:
                    try:
                        record["timestamp"] = datetime.fromisoformat(record["timestamp"])
                    except ValueError:
                        # Fallback for older timestamp formats
                        record["timestamp"] = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")

                # Create LLMCallRecord object
                return LLMCallRecord(
                    id=record["id"],
                    timestamp=record["timestamp"],
                    model=record["model"],
                    provider=record["provider"],
                    prompt=record["prompt"],
                    response=record["response"],
                    token_usage=record["token_usage"],
                    error=record["error"],
                    duration_ms=record["duration_ms"],
                    search_type=record["search_type"],
                    request_schema=record.get("request_schema"),
                )

        except Exception as e:
            logger.error(f"Failed to retrieve LLM call by ID {call_id}: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about LLM calls.

        Returns:
            Dictionary with statistics
        """
        try:
            with self._get_connection() as conn:
                # Total calls
                total_calls = conn.execute("SELECT COUNT(*) FROM llm_calls").fetchone()[0]

                # Calls by provider
                provider_stats = {}
                for row in conn.execute("SELECT provider, COUNT(*) FROM llm_calls GROUP BY provider"):
                    provider_stats[row[0]] = row[1]

                # Calls by model
                model_stats = {}
                for row in conn.execute("SELECT model, COUNT(*) FROM llm_calls GROUP BY model"):
                    model_stats[row[0]] = row[1]

                # Recent activity (last 24 hours)
                yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                recent_calls = conn.execute(
                    "SELECT COUNT(*) FROM llm_calls WHERE timestamp >= ?", (yesterday.isoformat(),)
                ).fetchone()[0]

                # Error rate
                error_count = conn.execute("SELECT COUNT(*) FROM llm_calls WHERE error IS NOT NULL").fetchone()[0]
                error_rate = (error_count / total_calls * 100) if total_calls > 0 else 0

                return {
                    "total_calls": total_calls,
                    "recent_calls_24h": recent_calls,
                    "error_rate_percent": round(error_rate, 2),
                    "provider_stats": provider_stats,
                    "model_stats": model_stats,
                }

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "total_calls": 0,
                "recent_calls_24h": 0,
                "error_rate_percent": 0,
                "provider_stats": {},
                "model_stats": {},
            }

    def get_total_calls_count(
        self, model: Optional[str] = None, provider: Optional[str] = None, search_type: Optional[str] = None
    ) -> int:
        """
        Get total count of calls matching filters.

        Args:
            model: Filter by model name
            provider: Filter by provider
            search_type: Filter by search type

        Returns:
            Total count of matching records
        """
        try:
            query = "SELECT COUNT(*) FROM llm_calls WHERE 1=1"
            params = []

            if model:
                query += " AND model = ?"
                params.append(model)

            if provider:
                query += " AND provider = ?"
                params.append(provider)

            if search_type:
                query += " AND search_type = ?"
                params.append(search_type)

            with self._get_connection() as conn:
                return conn.execute(query, params).fetchone()[0]

        except Exception as e:
            logger.error(f"Failed to get total calls count: {e}")
            return 0

    def get_available_providers(self) -> List[str]:
        """
        Get list of providers that have been used.

        Returns:
            List of provider names
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT DISTINCT provider FROM llm_calls ORDER BY provider")
                return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get available providers: {e}")
            return []

    def get_provider_stats(self) -> Dict[str, int]:
        """
        Get statistics by provider.

        Returns:
            Dictionary mapping provider names to call counts
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT provider, COUNT(*) FROM llm_calls GROUP BY provider ORDER BY COUNT(*) DESC"
                )
                return {row[0]: row[1] for row in cursor.fetchall()}

        except Exception as e:
            logger.error(f"Failed to get provider stats: {e}")
            return {}

    def get_top_models(self, limit: int = 5) -> List[tuple]:
        """
        Get top models by usage.

        Args:
            limit: Maximum number of models to return

        Returns:
            List of tuples (model_name, count)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT model, COUNT(*) FROM llm_calls GROUP BY model ORDER BY COUNT(*) DESC LIMIT ?", (limit,)
                )
                return [(row[0], row[1]) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get top models: {e}")
            return []

    def get_search_requests_count(self) -> int:
        """
        Get count of requests that used search.

        Returns:
            Number of requests with search enabled
        """
        try:
            with self._get_connection() as conn:
                return conn.execute("SELECT COUNT(*) FROM llm_calls WHERE search_type IS NOT NULL").fetchone()[0]

        except Exception as e:
            logger.error(f"Failed to get search requests count: {e}")
            return 0

    def delete_old_records(self, days_to_keep: int = 30) -> int:
        """
        Delete old records to keep database size manageable.

        Args:
            days_to_keep: Number of days of records to keep

        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)

            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM llm_calls WHERE timestamp < ?", (cutoff_date.isoformat(),))

                deleted_count = cursor.rowcount
                logger.info(f"Deleted {deleted_count} old LLM call records")
                return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete old records: {e}")
            return 0
