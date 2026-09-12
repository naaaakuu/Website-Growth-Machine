#!/usr/bin/env bash
# Double-click this file in Finder to install the skill — no need to open a
# folder or use Terminal yourself. If macOS blocks it as an unidentified
# developer, right-click (or Control-click) it and choose Open instead.
cd "$(dirname "$0")"
./install.sh
echo ""
read -n 1 -s -r -p "Done. Press any key to close this window..."
echo ""
