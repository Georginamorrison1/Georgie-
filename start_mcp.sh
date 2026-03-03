#!/usr/bin/env bash
# Loads credentials from .env (if present) then starts the Greenhouse MCP server.
# Claude Code calls this script as the MCP server command.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if it exists
ENV_FILE="$SCRIPT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

# Validate required variable
if [[ -z "${GREENHOUSE_API_KEY:-}" ]]; then
  echo "ERROR: GREENHOUSE_API_KEY is not set." >&2
  echo "Copy .env.example to .env and fill in your Greenhouse Harvest API key." >&2
  exit 1
fi

exec python "$SCRIPT_DIR/greenhouse_mcp.py"
