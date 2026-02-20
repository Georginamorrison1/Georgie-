"""HiBob REST API client."""

import requests

HIBOB_API_BASE = "https://api.hibob.com/v1"


class HiBobClient:
    def __init__(self, service_user_id: str, service_user_token: str):
        self._auth = (service_user_id, service_user_token)
        self._headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{HIBOB_API_BASE}/{endpoint}"
        response = requests.get(url, auth=self._auth, headers=self._headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_employees(self) -> dict:
        """Fetch all employees from the people directory."""
        return self._get("people")

    def get_employee(self, employee_id: str) -> dict:
        """Fetch a single employee by ID."""
        return self._get(f"people/{employee_id}")

    def get_timeoff_requests(self, from_date: str | None = None, to_date: str | None = None) -> dict:
        """Fetch time-off requests, optionally filtered by date range (YYYY-MM-DD)."""
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        return self._get("timeoff/requests/changes", params=params or None)

    def get_payroll(self) -> dict:
        """Fetch payroll history."""
        return self._get("payroll/history")
