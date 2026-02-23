"""Candidate management for the recruitment tool."""

from datetime import datetime, timezone

from src.database import get_db


def add_candidate(
    name: str,
    email: str,
    phone: str = "",
    resume_text: str = "",
) -> int:
    """Add a new candidate. Returns the new candidate id."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO candidates (name, email, phone, resume_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, phone, resume_text, now),
        )
        return cursor.lastrowid


def get_candidate(candidate_id: int) -> dict | None:
    """Return a candidate by id, or None if not found."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        return dict(row) if row else None


def list_candidates() -> list[dict]:
    """Return all candidates ordered by most recently added."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM candidates ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
