"""HiBob + Claude integration.

Fetches HR data from HiBob and uses Claude to analyze or summarize it.

Usage:
    python main.py employees "How many employees are in each department?"
    python main.py timeoff "Who has pending time-off requests?"
    python main.py employees  # defaults to a general summary
"""

import json
import os
import sys

import anthropic
from dotenv import load_dotenv

from hibob_client import HiBobClient

load_dotenv()

# Maximum characters of HiBob JSON to pass to Claude.
# Roughly 80K chars ≈ 20K tokens, well within the 200K context window.
MAX_DATA_CHARS = 80_000

DATA_SOURCES = {
    "employees": "Employee directory and profiles",
    "timeoff": "Time-off requests",
}


def fetch_data(client: HiBobClient, source: str) -> dict:
    if source == "employees":
        return client.get_employees()
    if source == "timeoff":
        return client.get_timeoff_requests()
    raise ValueError(f"Unknown data source '{source}'. Choose from: {', '.join(DATA_SOURCES)}")


def analyze(data: dict, query: str, source: str) -> None:
    """Send HiBob data to Claude and stream the analysis."""
    data_str = json.dumps(data, indent=2)

    if len(data_str) > MAX_DATA_CHARS:
        print(
            f"[Warning: data is {len(data_str):,} chars; truncating to {MAX_DATA_CHARS:,} chars "
            "to stay within context limits.]\n",
            flush=True,
        )
        data_str = data_str[:MAX_DATA_CHARS] + "\n... [truncated]"

    claude = anthropic.Anthropic()

    print("Analyzing with Claude...\n" + "-" * 60, flush=True)

    with claude.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=(
            "You are an HR data analyst. You have been given data exported from HiBob, "
            "an HR platform. Analyze the data and answer the user's question clearly and "
            "accurately. Use markdown formatting where it improves readability. "
            "Point out interesting patterns, trends, or anomalies when relevant."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Data source: {source}\n\n"
                    f"HiBob data:\n```json\n{data_str}\n```\n\n"
                    f"Question: {query}"
                ),
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n" + "-" * 60)


def main() -> None:
    # Validate required env vars up front
    missing = [v for v in ("HIBOB_SERVICE_USER_ID", "HIBOB_SERVICE_USER_TOKEN", "ANTHROPIC_API_KEY")
               if not os.environ.get(v)]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Copy .env.example to .env and fill in your credentials.", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        print("Available data sources:")
        for src, desc in DATA_SOURCES.items():
            print(f"  {src:<12} {desc}")
        return

    source = args[0] if args[0] in DATA_SOURCES else "employees"
    query_words = args[1:] if args[0] in DATA_SOURCES else args
    query = " ".join(query_words) if query_words else f"Give me a summary of the {source} data."

    hibob = HiBobClient(
        service_user_id=os.environ["HIBOB_SERVICE_USER_ID"],
        service_user_token=os.environ["HIBOB_SERVICE_USER_TOKEN"],
    )

    print(f"Fetching {source} data from HiBob...", flush=True)
    try:
        data = fetch_data(hibob, source)
    except Exception as exc:
        print(f"Error fetching HiBob data: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Done.\n", flush=True)
    analyze(data, query, source)


if __name__ == "__main__":
    main()
