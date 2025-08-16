#!/usr/bin/env bash
# Usage: scripts/compress_file.sh  runs/20250711_164550/transcript.txt  [HOST]

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${2:-http://localhost:8000}"
FILE="$ROOT/$1"

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2; exit 1
fi

curl -s -X POST "$HOST/compress_txt" \
     -H "Content-Type: text/plain" \
     --data-binary "@$FILE"