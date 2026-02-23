"""Job posting management for the recruitment tool."""

from datetime import datetime, timezone

from src.database import get_db

VALID_STATUSES = {"open", "closed", "draft"}


def create_job(
    title: str,
    department: str = "",
    location: str = "",
    description: str = "",
    requirements: str = "",
) -> int:
    """Create a new job posting. Returns the new job id."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO jobs (title, department, location, description, requirements, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'open', ?)
            """,
            (title, department, location, description, requirements, now),
        )
        return cursor.lastrowid


def list_jobs(status: str | None = None) -> list[dict]:
    """Return all jobs, optionally filtered by status."""
    with get_db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def get_job(job_id: int) -> dict | None:
    """Return a single job by id, or None if not found."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


def close_job(job_id: int) -> bool:
    """Mark a job as closed. Returns True if the job existed."""
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE jobs SET status = 'closed' WHERE id = ?", (job_id,)
        )
        return cursor.rowcount > 0
