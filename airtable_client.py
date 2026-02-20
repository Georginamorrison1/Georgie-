"""
Airtable client — read and write records using pyairtable.

Usage:
    Copy .env.example to .env and fill in your credentials, then:

    from airtable_client import AirtableClient

    client = AirtableClient()

    # List all records
    records = client.get_all()

    # Get a single record by ID
    record = client.get("recXXXXXXXXXXXXXX")

    # Create a record
    new_record = client.create({"Name": "Alice", "Status": "Active"})

    # Update a record
    updated = client.update("recXXXXXXXXXXXXXX", {"Status": "Inactive"})

    # Delete a record
    client.delete("recXXXXXXXXXXXXXX")
"""

import os
from typing import Any

from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()


class AirtableClient:
    """Thin wrapper around pyairtable for a single table."""

    def __init__(
        self,
        api_token: str | None = None,
        base_id: str | None = None,
        table_name: str | None = None,
    ) -> None:
        token = api_token or os.environ["AIRTABLE_API_TOKEN"]
        base = base_id or os.environ["AIRTABLE_BASE_ID"]
        table = table_name or os.environ["AIRTABLE_TABLE_NAME"]

        api = Api(token)
        self._table = api.table(base, table)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_all(self, **kwargs: Any) -> list[dict]:
        """Return all records in the table.

        Accepts any keyword arguments supported by pyairtable's `all()`,
        e.g. fields, formula, sort, view.
        """
        return self._table.all(**kwargs)

    def get(self, record_id: str) -> dict:
        """Return a single record by its Airtable record ID."""
        return self._table.get(record_id)

    def first(self, **kwargs: Any) -> dict | None:
        """Return the first matching record, or None if no records match."""
        return self._table.first(**kwargs)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, fields: dict) -> dict:
        """Create a new record and return it."""
        return self._table.create(fields)

    def update(self, record_id: str, fields: dict) -> dict:
        """Update an existing record by ID and return the updated record."""
        return self._table.update(record_id, fields)

    def upsert(self, records: list[dict], key_fields: list[str]) -> dict:
        """Create or update records based on key fields.

        Args:
            records:    List of field dicts to upsert.
            key_fields: Field names used to match existing records.

        Returns:
            A dict with 'createdRecords' and 'updatedRecords' lists.
        """
        return self._table.batch_upsert(records, key_fields)

    def delete(self, record_id: str) -> dict:
        """Delete a record by ID and return the deletion confirmation."""
        return self._table.delete(record_id)
