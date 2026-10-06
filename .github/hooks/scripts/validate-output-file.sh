#!/bin/bash

# Copilot provides the completed tool event as JSON on standard input.
INPUT=$(cat)

echo "postToolUse event received." >&2

if [ -z "$INPUT" ]; then
  echo "Output validation hook executed: no payload received." >&2
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "WARNING: Python is unavailable; output validation was skipped." >&2
  exit 0
fi

PATHS=$(printf '%s' "$INPUT" | "$PYTHON" -c '
import json
import re
import sys

try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

def strings(value):
    if isinstance(value, dict):
        for nested_value in value.values():
            yield from strings(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from strings(nested_value)
    elif isinstance(value, str):
        yield value

seen = set()
for value in strings(payload):
    normalized = value.replace("\\\\", "/")
    match = re.search(r"(?:^|/)((?:docs|output)/.+)$", normalized)
    if match:
        path = match.group(1)
        if path not in seen:
            seen.add(path)
            print(path)
')

if [ -z "$PATHS" ]; then
  echo "Output validation hook executed: no docs/ or output/ file was affected." >&2
  exit 0
fi

while IFS= read -r path; do
  if [ ! -e "$path" ]; then
    echo "WARNING: $path was referenced but does not exist." >&2
  elif [ ! -f "$path" ]; then
    echo "WARNING: $path is not a file." >&2
  elif [ -s "$path" ]; then
    echo "OK: $path contains content" >&2
  else
    echo "WARNING: $path was written but is empty." >&2
  fi
done <<EOF
$PATHS
EOF

echo "Output validation hook executed." >&2