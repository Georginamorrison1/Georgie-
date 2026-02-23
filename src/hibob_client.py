import base64
from datetime import datetime, timedelta

import httpx


class HiBobClient:
    """Client for the HiBob HR platform REST API."""

    BASE_URL = "https://api.hibob.com/v1"

    def __init__(self, service_user_id: str, service_user_token: str):
        credentials = base64.b64encode(
            f"{service_user_id}:{service_user_token}".encode()
        ).decode()
        self._headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{self.BASE_URL}{path}",
                headers=self._headers,
                params=params or {},
            )
            response.raise_for_status()
            return response.json()

    def get_employees(self) -> list[dict]:
        """Fetch all active employees from HiBob."""
        data = self._get("/people")
        return data.get("employees", [])

    def get_timeoff_outtoday(self) -> list[dict]:
        """Fetch employees who are out of office today."""
        data = self._get("/timeoff/outtoday")
        return data.get("outs", [])

    def get_timeoff_requests(self, from_date: str, to_date: str) -> list[dict]:
        """Fetch time-off requests within a date range (ISO 8601 dates)."""
        data = self._get(
            "/timeoff/requests/changes",
            params={"since": from_date, "to": to_date},
        )
        return data.get("changes", [])

    def aggregate_employees(self, employees: list[dict]) -> dict:
        """Summarise raw employee records into counts and lists for reporting."""
        cutoff = (datetime.now().date() - timedelta(days=90)).isoformat()
        by_department: dict[str, int] = {}
        by_site: dict[str, int] = {}
        by_employment_type: dict[str, int] = {}
        recent_hires: list[dict] = []

        for emp in employees:
            work = emp.get("work") or {}
            dept = work.get("department") or "Unknown"
            site = work.get("site") or "Unknown"
            emp_type = work.get("employmentType") or "Unknown"
            start_date = work.get("startDate") or ""

            by_department[dept] = by_department.get(dept, 0) + 1
            by_site[site] = by_site.get(site, 0) + 1
            by_employment_type[emp_type] = by_employment_type.get(emp_type, 0) + 1

            if start_date >= cutoff:
                recent_hires.append(
                    {
                        "name": f"{emp.get('firstName', '')} {emp.get('surname', '')}".strip(),
                        "department": dept,
                        "title": work.get("title") or "",
                        "site": site,
                        "start_date": start_date,
                    }
                )

        return {
            "total": len(employees),
            "by_department": dict(
                sorted(by_department.items(), key=lambda x: x[1], reverse=True)
            ),
            "by_site": dict(
                sorted(by_site.items(), key=lambda x: x[1], reverse=True)
            ),
            "by_employment_type": by_employment_type,
            "recent_hires_last_90_days": sorted(
                recent_hires, key=lambda x: x["start_date"], reverse=True
            ),
        }

    def aggregate_timeoff(
        self, requests: list[dict], outtoday: list[dict]
    ) -> dict:
        """Summarise time-off data for reporting."""
        by_type: dict[str, int] = {}
        by_department: dict[str, int] = {}

        for req in requests:
            policy = req.get("type", {})
            if isinstance(policy, dict):
                ptype = policy.get("name") or "Unknown"
            else:
                ptype = str(policy) if policy else "Unknown"
            by_type[ptype] = by_type.get(ptype, 0) + 1

            dept = req.get("employeeDisplayName", "")
            # department not always present in change events; track by name counts
            _ = dept

        out_names = [
            f"{o.get('firstName', '')} {o.get('surname', '')}".strip()
            for o in outtoday
        ]

        return {
            "out_today_count": len(outtoday),
            "out_today": out_names,
            "requests_total": len(requests),
            "by_type": by_type,
        }
