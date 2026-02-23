"""Application pipeline management for the recruitment tool."""

from datetime import datetime, timezone

from src.database import get_db

STAGES = ["applied", "screening", "interview", "offer", "hired", "rejected"]


def apply(job_id: int, candidate_id: int) -> int:
    """Create an application linking a candidate to a job. Returns the application id."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications (job_id, candidate_id, stage, created_at, updated_at)
            VALUES (?, ?, 'applied', ?, ?)
            """,
            (job_id, candidate_id, now, now),
        )
        return cursor.lastrowid


def advance_stage(application_id: int, stage: str) -> bool:
    """Move an application to a new stage. Returns True if the application existed."""
    if stage not in STAGES:
        raise ValueError(f"Invalid stage '{stage}'. Choose from: {', '.join(STAGES)}")
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE applications SET stage = ?, updated_at = ? WHERE id = ?",
            (stage, now, application_id),
        )
        return cursor.rowcount > 0


def add_notes(application_id: int, notes: str) -> bool:
    """Append notes to an application. Returns True if the application existed."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE applications SET notes = ?, updated_at = ? WHERE id = ?",
            (notes, now, application_id),
        )
        return cursor.rowcount > 0


def get_application(application_id: int) -> dict | None:
    """Return a single application with joined job and candidate details."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT
                a.*,
                j.title       AS job_title,
                j.department  AS job_department,
                c.name        AS candidate_name,
                c.email       AS candidate_email
            FROM applications a
            JOIN jobs       j ON j.id = a.job_id
            JOIN candidates c ON c.id = a.candidate_id
            WHERE a.id = ?
            """,
            (application_id,),
        ).fetchone()
        return dict(row) if row else None


def list_applications(job_id: int | None = None, stage: str | None = None) -> list[dict]:
    """Return applications, optionally filtered by job and/or stage."""
    query = """
        SELECT
            a.*,
            j.title       AS job_title,
            j.department  AS job_department,
            c.name        AS candidate_name,
            c.email       AS candidate_email
        FROM applications a
        JOIN jobs       j ON j.id = a.job_id
        JOIN candidates c ON c.id = a.candidate_id
    """
    filters, params = [], []
    if job_id is not None:
        filters.append("a.job_id = ?")
        params.append(job_id)
    if stage is not None:
        filters.append("a.stage = ?")
        params.append(stage)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY a.updated_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
