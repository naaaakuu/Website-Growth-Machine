#!/usr/bin/env bash
# Build a single distributable archive of this skill (for AirDrop/email/cloud
# transfer to a machine where you can't easily open/navigate this folder).
# tar.gz keeps installer scripts' executable permission intact — a zip built
# with some tools (notably on Windows) silently drops it.
# Run from macOS, Linux, or Git Bash on Windows: bash package_release.sh
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="website-growth-engine"
OUT="$SOURCE_DIR/../${NAME}.tar.gz"

cd "$SOURCE_DIR/.."
rm -f "$OUT"
tar --owner=0 --group=0 --mode='a+rX,u+w' \
  --exclude="$(basename "$SOURCE_DIR")/.git" \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  -czf "$OUT" "$(basename "$SOURCE_DIR")"

echo "Wrote $OUT"
