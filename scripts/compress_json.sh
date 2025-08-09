#!/usr/bin/env bash
# Compress a structured chat stored as JSON.
# Usage:
#   scripts/compress_json.sh  runs/20250711_164550/chat.json  [HOST]

# ── repo-root and args ──────────────────────────────────────────────────────
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="$ROOT/$1"                                  # first arg → relative path
HOST="${2:-http://localhost:8000}"               # second arg → host/port

if [[ -z "$1" || ! -f "$FILE" ]]; then
  echo "Usage: $0 runs/<timestamp>/chat.json [HOST]" >&2
  exit 1
fi

# ── send it ─────────────────────────────────────────────────────────────────
curl -s -X POST "$HOST/compress" \
     -H "Content-Type: application/json" \
     --data "@$FILE"
