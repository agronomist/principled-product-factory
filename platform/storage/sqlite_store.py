"""ACID SQLite WAL Persistence Engine (`platform/storage/sqlite_store.py`).

Implements Joel Spolsky's systems durability mandate: *"If it isn't persisted in an ACID
transaction on disk, it didn't happen."*

Features:
1. **Write-Ahead Logging (`PRAGMA journal_mode=WAL`) & `PRAGMA synchronous=NORMAL`**:
   Allows concurrent readers and serialized ACID writers across independent worker processes
   without `SQLITE_BUSY` deadlocks (`busy_timeout = 5000ms`).
2. **Four Durable Factory Tables**:
   - `learning_signals`: Content-addressed (`PRIMARY KEY (idempotency_key)`) storage for
     `IdempotentLearningLogger` so deduplication survives process crashes and restarts.
   - `handoff_artifacts`: Immutable pass-by-ID blob table (`PRIMARY KEY (artifact_key)`)
     for `HandoffArtifactStore` (`INSERT OR FAIL` prevents silent overwrites).
   - `factory_brain_notes`: Append-only durable repository memory keyed by `brain_key`
     (`SHA256(FACTORY_REPO)`).
   - `demand_signals`: Deduplicated per `(topic_slug, customer_account_id)` storage for
     `DemandSignalAccumulator` so $N=1 \to N=3 \to N=10$ customer demand graduation persists
     across quarters and server restarts.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StoredLearningSignalRow(BaseModel):
    """Immutable row model for a persisted learning signal in SQLite."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    idempotency_key: str = Field(..., min_length=64, max_length=64)
    recorded_at_utc: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    workflow_run_id: str = Field(..., min_length=1)
    payload_json: str = Field(..., min_length=2)


class StoredArtifactRow(BaseModel):
    """Immutable row model for a persisted pass-by-ID handoff artifact in SQLite."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    artifact_key: str = Field(..., min_length=1)
    created_at_utc: str = Field(..., min_length=1)
    content: str = Field(...)


class StoredBrainNoteRow(BaseModel):
    """Immutable row model for a persisted Factory Brain note in SQLite."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    note_id: int = Field(..., ge=1)
    brain_key: str = Field(..., min_length=1)
    created_at_utc: str = Field(..., min_length=1)
    note_text: str = Field(..., min_length=1)


class StoredDemandSignalRow(BaseModel):
    """Immutable row model for a persisted customer pain signal in SQLite."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    topic_slug: str = Field(..., min_length=3)
    customer_account_id: str = Field(..., min_length=1)
    commitment_rank: int = Field(..., ge=0, le=4)
    payload_json: str = Field(..., min_length=2)


class SQLiteWALStore:
    """Thread-safe and multi-process-safe ACID SQLite persistence engine using WAL mode."""

    def __init__(self, db_path: Path | str) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=5.0, isolation_level="DEFERRED")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS learning_signals (
                    idempotency_key TEXT PRIMARY KEY,
                    recorded_at_utc TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    workflow_run_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS handoff_artifacts (
                    artifact_key TEXT PRIMARY KEY,
                    created_at_utc TEXT NOT NULL,
                    content TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS factory_brain_notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brain_key TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    note_text TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS demand_signals (
                    topic_slug TEXT NOT NULL,
                    customer_account_id TEXT NOT NULL,
                    commitment_rank INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY (topic_slug, customer_account_id)
                );
                """
            )

    def journal_mode(self) -> str:
        """Return active SQLite journal mode (verifies `wal` is active on disk)."""
        with self._lock, self._connect() as conn:
            row = conn.execute("PRAGMA journal_mode;").fetchone()
            return str(row[0]).lower() if row else "unknown"

    # -----------------------------------------------------------------------
    # 1. Durable Learning Signals (`IdempotentLearningLogger`)
    # -----------------------------------------------------------------------

    def insert_or_get_learning_signal(
        self,
        *,
        idempotency_key: str,
        recorded_at_utc: str,
        product_id: str,
        workflow_run_id: str,
        payload_dict: dict[str, Any],
    ) -> tuple[StoredLearningSignalRow, bool]:
        """Atomically insert a learning signal or return the existing row with `is_replay=True`."""
        serialized = json.dumps(payload_dict, sort_keys=True)
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO learning_signals
                (idempotency_key, recorded_at_utc, product_id, workflow_run_id, payload_json)
                VALUES (?, ?, ?, ?, ?);
                """,
                (idempotency_key, recorded_at_utc, product_id, workflow_run_id, serialized),
            )
            inserted = cur.rowcount == 1
            row = conn.execute(
                """
                SELECT idempotency_key, recorded_at_utc, product_id, workflow_run_id, payload_json
                FROM learning_signals
                WHERE idempotency_key = ?;
                """,
                (idempotency_key,),
            ).fetchone()
            if row is None:
                raise RuntimeError("SQLite consistency error on learning_signals lookup.")
            return (
                StoredLearningSignalRow(
                    idempotency_key=row[0],
                    recorded_at_utc=row[1],
                    product_id=row[2],
                    workflow_run_id=row[3],
                    payload_json=row[4],
                ),
                not inserted,
            )

    def list_learning_signals(self) -> tuple[StoredLearningSignalRow, ...]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT idempotency_key, recorded_at_utc, product_id, workflow_run_id, payload_json
                FROM learning_signals
                ORDER BY rowid ASC;
                """
            ).fetchall()
            return tuple(
                StoredLearningSignalRow(
                    idempotency_key=r[0],
                    recorded_at_utc=r[1],
                    product_id=r[2],
                    workflow_run_id=r[3],
                    payload_json=r[4],
                )
                for r in rows
            )

    # -----------------------------------------------------------------------
    # 2. Durable Handoff Artifacts (`HandoffArtifactStore`)
    # -----------------------------------------------------------------------

    def save_artifact_row(self, artifact_key: str, content: str) -> StoredArtifactRow:
        """Persist an immutable handoff artifact (`INSERT` fails on key collision)."""
        ts = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO handoff_artifacts (artifact_key, created_at_utc, content)
                VALUES (?, ?, ?);
                """,
                (artifact_key, ts, content),
            )
            return StoredArtifactRow(
                artifact_key=artifact_key,
                created_at_utc=ts,
                content=content,
            )

    def read_artifact_row(self, artifact_key: str) -> str | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT content FROM handoff_artifacts WHERE artifact_key = ?;",
                (artifact_key,),
            ).fetchone()
            return str(row[0]) if row is not None else None

    # -----------------------------------------------------------------------
    # 3. Durable Factory Brain (`FactoryBrain`)
    # -----------------------------------------------------------------------

    def append_brain_note(self, brain_key: str, note_text: str) -> StoredBrainNoteRow:
        ts = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO factory_brain_notes (brain_key, created_at_utc, note_text)
                VALUES (?, ?, ?);
                """,
                (brain_key, ts, note_text),
            )
            note_id = int(cur.lastrowid or 1)
            return StoredBrainNoteRow(
                note_id=note_id,
                brain_key=brain_key,
                created_at_utc=ts,
                note_text=note_text,
            )

    def read_brain_notes(self, brain_key: str) -> tuple[str, ...]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT note_text FROM factory_brain_notes
                WHERE brain_key = ?
                ORDER BY note_id ASC;
                """,
                (brain_key,),
            ).fetchall()
            return tuple(str(r[0]) for r in rows)

    # -----------------------------------------------------------------------
    # 4. Durable Demand Signals (`DemandSignalAccumulator`)
    # -----------------------------------------------------------------------

    def upsert_demand_signal(
        self,
        *,
        topic_slug: str,
        customer_account_id: str,
        commitment_rank: int,
        payload_dict: dict[str, Any],
    ) -> None:
        """Upsert a customer pain signal, keeping the higher commitment_rank if the account already exists."""
        serialized = json.dumps(payload_dict, sort_keys=True)
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO demand_signals (topic_slug, customer_account_id, commitment_rank, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(topic_slug, customer_account_id) DO UPDATE SET
                    commitment_rank = excluded.commitment_rank,
                    payload_json = excluded.payload_json
                WHERE excluded.commitment_rank >= demand_signals.commitment_rank;
                """,
                (topic_slug, customer_account_id, commitment_rank, serialized),
            )

    def list_demand_signals_for_topic(
        self,
        topic_slug: str,
    ) -> tuple[StoredDemandSignalRow, ...]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT topic_slug, customer_account_id, commitment_rank, payload_json
                FROM demand_signals
                WHERE topic_slug = ?
                ORDER BY rowid ASC;
                """,
                (topic_slug,),
            ).fetchall()
            return tuple(
                StoredDemandSignalRow(
                    topic_slug=r[0],
                    customer_account_id=r[1],
                    commitment_rank=int(r[2]),
                    payload_json=r[3],
                )
                for r in rows
            )
