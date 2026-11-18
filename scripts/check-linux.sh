#!/usr/bin/env bash
# Baseline smoke test for Shoto Fighter on Linux.
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v godot >/dev/null 2>&1; then
  GODOT=godot
elif command -v godot4 >/dev/null 2>&1; then
  GODOT=godot4
else
  echo "ERROR: Godot 4.4+ not found (expected 'godot' or 'godot4' in PATH)." >&2
  exit 127
fi

echo "Using: $("$GODOT" --version)"
echo "Importing project assets and parsing scenes..."
"$GODOT" --headless --path . --editor --import --quit
echo "Running gdUnit4 tests..."
"$GODOT" --headless --path . -s addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://test
echo "Linux baseline OK."
