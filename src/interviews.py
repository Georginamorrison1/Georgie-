"""Interview scheduling for the recruitment tool."""

from datetime import datetime, timezone

from src.database import get_db


def schedule_interview(
    application_id: int,
    interviewer: str,
    scheduled_at: str,
    stage_name: str = "",
) -> int:
    """Schedule an interview for an application. Returns the new interview id.

    scheduled_at should be an ISO 8601 datetime string, e.g. '2026-03-10T14:00'.
    """
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO interviews (application_id, interviewer, scheduled_at, stage_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (application_id, interviewer, scheduled_at, stage_name, now),
        )
        return cursor.lastrowid


def add_interview_notes(interview_id: int, notes: str) -> bool:
    """Record notes on a completed interview. Returns True if the interview existed."""
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE interviews SET notes = ? WHERE id = ?",
            (notes, interview_id),
        )
        return cursor.rowcount > 0


def list_interviews(application_id: int) -> list[dict]:
    """Return all interviews for a given application, ordered by scheduled time."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM interviews WHERE application_id = ? ORDER BY scheduled_at",
            (application_id,),
        ).fetchall()
        return [dict(r) for r in rows]
