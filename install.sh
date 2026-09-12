#!/usr/bin/env bash
# Install this skill folder into Claude Code's personal skills directory
# (~/.claude/skills/website-growth-engine by default) so it shows up as an
# available skill without you having to find or open the folder yourself.
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="website-growth-engine"
SKILLS_ROOT="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
TARGET_DIR="$SKILLS_ROOT/$SKILL_NAME"

mkdir -p "$SKILLS_ROOT"

if [ -e "$TARGET_DIR" ]; then
  BACKUP_DIR="${TARGET_DIR}.backup.$(date +%Y%m%d-%H%M%S)"
  echo "Existing install found at $TARGET_DIR — backing it up to $BACKUP_DIR"
  mv "$TARGET_DIR" "$BACKUP_DIR"
fi

mkdir -p "$TARGET_DIR"
cp -R "$SOURCE_DIR/." "$TARGET_DIR/"
find "$TARGET_DIR/scripts" -name '*.py' -exec chmod +x {} \; 2>/dev/null || true

echo ""
echo "Installed website-growth-engine to: $TARGET_DIR"
echo "Open (or restart) Claude Code — it will now appear as an available skill."
