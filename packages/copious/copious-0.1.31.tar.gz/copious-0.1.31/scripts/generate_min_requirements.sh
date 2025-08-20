#!/usr/bin/env bash
set -euo pipefail

# Generate minimal compatible pinned requirements for this project.
# Prefers `uv pip compile --resolution lowest-direct` if available; otherwise falls back to pip-tools.
# Output files:
#   constraints/requirements-min.txt (pinned minimal set for default Python)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
REQ_IN="$ROOT_DIR/requirements.runtime.in"
OUT_DIR="$ROOT_DIR/constraints"
PYTAG="py$(python -c 'import sys;print(str(sys.version_info.major)+str(sys.version_info.minor))')"
OUT_FILE_VERSIONED="$OUT_DIR/requirements-min-${PYTAG}.txt"
OUT_FILE_GENERIC="$OUT_DIR/requirements-min.txt"
FLOORS_FILE="$OUT_DIR/floors-${PYTAG}.txt"

mkdir -p "$OUT_DIR"

if command -v uv >/dev/null 2>&1; then
  echo "Using uv to resolve lowest compatible versions..."
  if [[ -f "$FLOORS_FILE" ]]; then EXTRA_CONSTRAINTS=( -c "$FLOORS_FILE" ); else EXTRA_CONSTRAINTS=(); fi
  uv pip compile "$REQ_IN" "${EXTRA_CONSTRAINTS[@]}" \
    --resolution lowest-direct \
    --quiet \
    --no-header \
    --output-file "$OUT_FILE_VERSIONED"
  cp "$OUT_FILE_VERSIONED" "$OUT_FILE_GENERIC"
  echo "Wrote $OUT_FILE_VERSIONED and $OUT_FILE_GENERIC"
  exit 0
fi

echo "uv not found. Falling back to pip-tools (pip-compile). This may not be strictly minimal."
if ! command -v pip-compile >/dev/null 2>&1; then
  echo "pip-tools not installed. Installing locally..." >&2
  python -m pip install --upgrade pip-tools >/dev/null
fi

if [[ -f "$FLOORS_FILE" ]]; then
  pip-compile "$REQ_IN" -c "$FLOORS_FILE" --no-header --output-file "$OUT_FILE_VERSIONED"
else
  pip-compile "$REQ_IN" --no-header --output-file "$OUT_FILE_VERSIONED"
fi

# Validate headerless format exists
if [[ ! -s "$OUT_FILE_VERSIONED" ]]; then
  echo "Failed to generate $OUT_FILE_VERSIONED" >&2
  exit 2
fi

cp "$OUT_FILE_VERSIONED" "$OUT_FILE_GENERIC"
echo "Wrote $OUT_FILE_VERSIONED and $OUT_FILE_GENERIC"
echo "Note: For strict minimums, install 'uv' and rerun this script."
