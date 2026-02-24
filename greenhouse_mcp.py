"""
Greenhouse MCP Server

Exposes Greenhouse Harvest API as MCP tools for Claude Code.

Configuration:
    Set GREENHOUSE_API_KEY environment variable to your Greenhouse Harvest API key.
    Optionally set GREENHOUSE_ON_BEHALF_OF to a Greenhouse user ID for audit logging.

Usage:
    python greenhouse_mcp.py
"""

import os
import json
from typing import Optional
import requests
from mcp.server.fastmcp import FastMCP

GREENHOUSE_API_KEY = os.environ.get("GREENHOUSE_API_KEY", "")
ON_BEHALF_OF = os.environ.get("GREENHOUSE_ON_BEHALF_OF", "")
BASE_URL = "https://harvest.greenhouse.io/v1"

mcp = FastMCP("Greenhouse")


def _get(path: str, params: Optional[dict] = None) -> dict | list:
    """Make an authenticated GET request to the Greenhouse Harvest API."""
    if not GREENHOUSE_API_KEY:
        raise ValueError("GREENHOUSE_API_KEY environment variable is not set")
    headers = {}
    if ON_BEHALF_OF:
        headers["On-Behalf-Of"] = ON_BEHALF_OF
    resp = requests.get(
        f"{BASE_URL}{path}",
        auth=(GREENHOUSE_API_KEY, ""),
        headers=headers,
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _post(path: str, body: dict) -> dict:
    """Make an authenticated POST request to the Greenhouse Harvest API."""
    if not GREENHOUSE_API_KEY:
        raise ValueError("GREENHOUSE_API_KEY environment variable is not set")
    headers = {"Content-Type": "application/json"}
    if ON_BEHALF_OF:
        headers["On-Behalf-Of"] = ON_BEHALF_OF
    resp = requests.post(
        f"{BASE_URL}{path}",
        auth=(GREENHOUSE_API_KEY, ""),
        headers=headers,
        json=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _patch(path: str, body: dict) -> dict:
    """Make an authenticated PATCH request to the Greenhouse Harvest API."""
    if not GREENHOUSE_API_KEY:
        raise ValueError("GREENHOUSE_API_KEY environment variable is not set")
    headers = {"Content-Type": "application/json"}
    if ON_BEHALF_OF:
        headers["On-Behalf-Of"] = ON_BEHALF_OF
    resp = requests.patch(
        f"{BASE_URL}{path}",
        auth=(GREENHOUSE_API_KEY, ""),
        headers=headers,
        json=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@mcp.tool()
def list_jobs(status: str = "open", department_id: Optional[int] = None, office_id: Optional[int] = None) -> str:
    """List jobs in Greenhouse.

    Args:
        status: Filter by status. One of 'open', 'closed', or 'draft'. Defaults to 'open'.
        department_id: Optional department ID to filter by.
        office_id: Optional office ID to filter by.
    """
    params: dict = {"status": status, "per_page": 100}
    if department_id:
        params["department_id"] = department_id
    if office_id:
        params["office_id"] = office_id
    data = _get("/jobs", params=params)
    jobs = [
        {
            "id": j["id"],
            "name": j["name"],
            "status": j["status"],
            "departments": [d["name"] for d in j.get("departments", [])],
            "offices": [o["name"] for o in j.get("offices", [])],
            "opened_at": j.get("opened_at"),
        }
        for j in data
    ]
    return json.dumps(jobs, indent=2)


@mcp.tool()
def get_job(job_id: int) -> str:
    """Get details for a specific Greenhouse job.

    Args:
        job_id: The Greenhouse job ID.
    """
    data = _get(f"/jobs/{job_id}")
    result = {
        "id": data["id"],
        "name": data["name"],
        "status": data["status"],
        "departments": [d["name"] for d in data.get("departments", [])],
        "offices": [o["name"] for o in data.get("offices", [])],
        "hiring_team": data.get("hiring_team", {}),
        "opened_at": data.get("opened_at"),
        "custom_fields": data.get("custom_fields", {}),
        "job_post_id": data.get("job_post_id"),
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def list_job_stages(job_id: int) -> str:
    """List the interview stages for a specific job.

    Args:
        job_id: The Greenhouse job ID.
    """
    data = _get(f"/jobs/{job_id}/stages")
    stages = [{"id": s["id"], "name": s["name"]} for s in data]
    return json.dumps(stages, indent=2)


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------

@mcp.tool()
def list_candidates(
    job_id: Optional[int] = None,
    email: Optional[str] = None,
    per_page: int = 25,
) -> str:
    """List candidates in Greenhouse.

    Args:
        job_id: Optional job ID to filter candidates by.
        email: Optional email address to search for a specific candidate.
        per_page: Number of results per page (max 500). Defaults to 25.
    """
    params: dict = {"per_page": min(per_page, 500)}
    if job_id:
        params["job_id"] = job_id
    if email:
        params["email"] = email
    data = _get("/candidates", params=params)
    candidates = [
        {
            "id": c["id"],
            "first_name": c.get("first_name"),
            "last_name": c.get("last_name"),
            "email_addresses": [e["value"] for e in c.get("email_addresses", [])],
            "applications": [
                {"id": a["id"], "job_id": a.get("job", {}).get("id"), "status": a.get("status")}
                for a in c.get("applications", [])
            ],
            "created_at": c.get("created_at"),
        }
        for c in data
    ]
    return json.dumps(candidates, indent=2)


@mcp.tool()
def get_candidate(candidate_id: int) -> str:
    """Get full details for a specific Greenhouse candidate.

    Args:
        candidate_id: The Greenhouse candidate ID.
    """
    data = _get(f"/candidates/{candidate_id}")
    result = {
        "id": data["id"],
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email_addresses": data.get("email_addresses", []),
        "phone_numbers": data.get("phone_numbers", []),
        "addresses": data.get("addresses", []),
        "website_addresses": data.get("website_addresses", []),
        "social_media_addresses": data.get("social_media_addresses", []),
        "tags": data.get("tags", []),
        "applications": data.get("applications", []),
        "educations": data.get("educations", []),
        "employments": data.get("employments", []),
        "custom_fields": data.get("custom_fields", {}),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def add_note_to_candidate(candidate_id: int, note: str, visibility: str = "private") -> str:
    """Add a note to a candidate in Greenhouse.

    Args:
        candidate_id: The Greenhouse candidate ID.
        note: The note text to add.
        visibility: Note visibility. One of 'private' or 'public'. Defaults to 'private'.
    """
    if not ON_BEHALF_OF:
        return json.dumps({"error": "GREENHOUSE_ON_BEHALF_OF must be set to add notes. Set it to a Greenhouse user ID."})
    body = {"body": note, "visibility": visibility, "user_id": int(ON_BEHALF_OF)}
    data = _post(f"/candidates/{candidate_id}/notes", body=body)
    return json.dumps({"id": data.get("id"), "body": data.get("body"), "created_at": data.get("created_at")}, indent=2)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@mcp.tool()
def list_applications(
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    per_page: int = 25,
) -> str:
    """List applications in Greenhouse.

    Args:
        job_id: Optional job ID to filter applications by.
        status: Optional status filter. One of 'active', 'rejected', 'hired'.
        per_page: Number of results per page (max 500). Defaults to 25.
    """
    params: dict = {"per_page": min(per_page, 500)}
    if job_id:
        params["job_id"] = job_id
    if status:
        params["status"] = status
    data = _get("/applications", params=params)
    applications = [
        {
            "id": a["id"],
            "candidate_id": a.get("candidate_id"),
            "status": a.get("status"),
            "stage": a.get("current_stage", {}).get("name") if a.get("current_stage") else None,
            "job": a.get("jobs", [{}])[0].get("name") if a.get("jobs") else None,
            "job_id": a.get("jobs", [{}])[0].get("id") if a.get("jobs") else None,
            "applied_at": a.get("applied_at"),
            "rejected_at": a.get("rejected_at"),
        }
        for a in data
    ]
    return json.dumps(applications, indent=2)


@mcp.tool()
def get_application(application_id: int) -> str:
    """Get full details for a specific Greenhouse application.

    Args:
        application_id: The Greenhouse application ID.
    """
    data = _get(f"/applications/{application_id}")
    result = {
        "id": data["id"],
        "candidate_id": data.get("candidate_id"),
        "status": data.get("status"),
        "current_stage": data.get("current_stage"),
        "jobs": data.get("jobs", []),
        "job_post_id": data.get("job_post_id"),
        "source": data.get("source"),
        "credited_to": data.get("credited_to"),
        "rejection_reason": data.get("rejection_reason"),
        "rejection_details": data.get("rejection_details"),
        "applied_at": data.get("applied_at"),
        "rejected_at": data.get("rejected_at"),
        "custom_fields": data.get("custom_fields", {}),
        "scheduled_interviews": data.get("scheduled_interviews", []),
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def move_application(application_id: int, stage_id: int) -> str:
    """Move a Greenhouse application to a specific interview stage.

    Args:
        application_id: The Greenhouse application ID.
        stage_id: The target stage ID (use list_job_stages to find stage IDs).
    """
    body = {"stage_id": stage_id}
    data = _patch(f"/applications/{application_id}/move", body=body)
    return json.dumps({"id": data.get("id"), "current_stage": data.get("current_stage"), "status": data.get("status")}, indent=2)


# ---------------------------------------------------------------------------
# Departments & Offices
# ---------------------------------------------------------------------------

@mcp.tool()
def list_departments() -> str:
    """List all departments in Greenhouse."""
    data = _get("/departments")
    departments = [{"id": d["id"], "name": d["name"], "parent_id": d.get("parent_id")} for d in data]
    return json.dumps(departments, indent=2)


@mcp.tool()
def list_offices() -> str:
    """List all offices in Greenhouse."""
    data = _get("/offices")
    offices = [{"id": o["id"], "name": o["name"], "location": o.get("location", {}).get("name")} for o in data]
    return json.dumps(offices, indent=2)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@mcp.tool()
def list_users(email: Optional[str] = None) -> str:
    """List users in Greenhouse.

    Args:
        email: Optional email to search for a specific user.
    """
    params: dict = {"per_page": 100}
    if email:
        params["email"] = email
    data = _get("/users", params=params)
    users = [
        {
            "id": u["id"],
            "name": u.get("name"),
            "first_name": u.get("first_name"),
            "last_name": u.get("last_name"),
            "primary_email_address": u.get("primary_email_address"),
            "employee_id": u.get("employee_id"),
            "is_site_admin": u.get("site_admin"),
            "disabled": u.get("disabled"),
        }
        for u in data
    ]
    return json.dumps(users, indent=2)


if __name__ == "__main__":
    mcp.run()
