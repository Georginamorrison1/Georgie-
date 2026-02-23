#!/usr/bin/env python3
"""HiBob + Claude integration: HR data analysis and reporting."""

import argparse
import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable is not set.", file=sys.stderr)
        print("Copy .env.example to .env and fill in your credentials.", file=sys.stderr)
        sys.exit(1)
    return value


def _build_hibob_client():
    from src.hibob_client import HiBobClient

    return HiBobClient(
        service_user_id=_require_env("HIBOB_SERVICE_USER_ID"),
        service_user_token=_require_env("HIBOB_SERVICE_USER_TOKEN"),
    )


def _check_anthropic_key():
    _require_env("ANTHROPIC_API_KEY")


# ------------------------------------------------------------------
# Command handlers
# ------------------------------------------------------------------


def cmd_headcount(args):
    """Generate a headcount report by department and location."""
    _check_anthropic_key()
    bob = _build_hibob_client()

    from src.reporter import HRReporter

    print("Fetching employees from HiBob...", flush=True)
    try:
        employees = bob.get_employees()
    except Exception as exc:
        print(f"Error fetching employees: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(employees)} employees. Generating report...\n", flush=True)
    summary = bob.aggregate_employees(employees)
    HRReporter().generate_headcount_report(summary)


def cmd_timeoff(args):
    """Generate a time-off summary for the last 30 days."""
    _check_anthropic_key()
    bob = _build_hibob_client()

    from src.reporter import HRReporter

    today = datetime.now().date()
    from_date = (today - timedelta(days=30)).isoformat()
    to_date = today.isoformat()

    print("Fetching time-off data from HiBob...", flush=True)
    try:
        outtoday = bob.get_timeoff_outtoday()
        requests = bob.get_timeoff_requests(from_date, to_date)
    except Exception as exc:
        print(f"Error fetching time-off data: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Fetched {len(outtoday)} out today, {len(requests)} requests in last 30 days."
        " Generating report...\n",
        flush=True,
    )
    summary = bob.aggregate_timeoff(requests, outtoday)
    HRReporter().generate_timeoff_report(summary)


def cmd_query(args):
    """Answer a custom workforce question using Claude."""
    _check_anthropic_key()
    bob = _build_hibob_client()

    from src.reporter import HRReporter

    print("Fetching employees from HiBob...", flush=True)
    try:
        employees = bob.get_employees()
    except Exception as exc:
        print(f"Error fetching employees: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(employees)} employees. Answering query...\n", flush=True)
    summary = bob.aggregate_employees(employees)
    HRReporter().answer_query(args.question, summary)


# ------------------------------------------------------------------
# CLI definition
# ------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="hibob-claude",
        description="HiBob + Claude: AI-powered HR data analysis and reporting",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # headcount
    headcount = subparsers.add_parser(
        "headcount",
        help="Generate a headcount report by department and location",
    )
    headcount.set_defaults(func=cmd_headcount)

    # timeoff
    timeoff = subparsers.add_parser(
        "timeoff",
        help="Generate a time-off summary for the last 30 days",
    )
    timeoff.set_defaults(func=cmd_timeoff)

    # query
    query = subparsers.add_parser(
        "query",
        help="Ask a custom question about your workforce",
    )
    query.add_argument("question", help='e.g. "Which department grew the most this quarter?"')
    query.set_defaults(func=cmd_query)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
