"""SQLite database initialisation and connection helper for the recruitment tool."""

import os
import sqlite3
from contextlib import contextmanager


def _db_path() -> str:
    return os.environ.get("DATABASE_PATH", "recruitment.db")


def init_db() -> None:
    """Create all recruitment tables if they do not already exist."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                department  TEXT,
                location    TEXT,
                description TEXT,
                requirements TEXT,
                status      TEXT NOT NULL DEFAULT 'open',
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS candidates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                email       TEXT NOT NULL UNIQUE,
                phone       TEXT,
                resume_text TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id        INTEGER NOT NULL REFERENCES jobs(id),
                candidate_id  INTEGER NOT NULL REFERENCES candidates(id),
                stage         TEXT NOT NULL DEFAULT 'applied',
                notes         TEXT,
                created_at    TEXT NOT NULL,
                updated_at    TEXT NOT NULL,
                UNIQUE(job_id, candidate_id)
            );

            CREATE TABLE IF NOT EXISTS interviews (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id  INTEGER NOT NULL REFERENCES applications(id),
                interviewer     TEXT NOT NULL,
                scheduled_at    TEXT NOT NULL,
                stage_name      TEXT,
                notes           TEXT,
                created_at      TEXT NOT NULL
            );
        """)


@contextmanager
def _connect():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db():
    """Return a context manager that yields a connected, committed SQLite connection."""
    return _connect()
