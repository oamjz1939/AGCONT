#!/usr/bin/env bash
set -e

# Find Blender executable
BLENDER_BIN=""
if [ -x "/Applications/Blender.app/Contents/MacOS/Blender" ]; then
    BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
elif command -v blender &> /dev/null; then
    BLENDER_BIN="blender"
else
    echo "Error: Blender executable not found." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/convert_pmx_to_blend.py"

"$BLENDER_BIN" -b -P "$PYTHON_SCRIPT" -- "$@"
