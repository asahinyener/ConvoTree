#!/usr/bin/env bash
# Usage: scripts/resume.sh  runs/<stamp>/bundle.json  "next user msg"  [HOST]

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE_REL="$1"                     # e.g. runs/20250711_051647/bundle.json
NEXT="$2"
HOST="${3:-http://localhost:8000}"

if [[ -z "$BUNDLE_REL" || -z "$NEXT" ]]; then
  echo "Usage: $0 runs/<stamp>/bundle.json \"next message\" [HOST]" >&2
  exit 1
fi

curl -s -X POST "$HOST/resume" \
     -H "Content-Type: application/json" \
     -d "{\"bundle_path\":\"${BUNDLE_REL}\",\"next_user\":\"${NEXT}\"}"
