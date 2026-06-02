#!/usr/bin/env bash
set -euo pipefail

# CodeDocs Desktop — PyInstaller build script
# Bundles python/wrapper.py into a single executable for distribution

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_DIR="$(dirname "$SCRIPT_DIR")"
CODEDOCS_ROOT="$(dirname "$DESKTOP_DIR")"

echo "=== CodeDocs Python Build ==="
echo "Desktop dir: $DESKTOP_DIR"
echo "CodeDocs root: $CODEDOCS_ROOT"

# Check that wrapper.py exists
if [ ! -f "$DESKTOP_DIR/python/wrapper.py" ]; then
  echo "ERROR: python/wrapper.py not found in $DESKTOP_DIR"
  exit 1
fi

# Install pyinstaller if not present
if ! command -v pyinstaller &> /dev/null; then
  echo "Installing PyInstaller..."
  pip install pyinstaller
fi

echo "Building codedocs-wrapper binary..."

# Build single-file executable
pyinstaller \
  --onefile \
  --name codedocs-wrapper \
  --distpath "$DESKTOP_DIR/python/dist" \
  --workpath "$DESKTOP_DIR/python/build" \
  --specpath "$DESKTOP_DIR/python" \
  --paths "$CODEDOCS_ROOT" \
  --add-data "$CODEDOCS_ROOT/codedocs/i18n:codedocs/i18n" \
  --clean \
  --noconfirm \
  "$DESKTOP_DIR/python/wrapper.py"

# Report result
BINARY="$DESKTOP_DIR/python/dist/codedocs-wrapper"
if [ -f "$BINARY" ]; then
  SIZE=$(du -h "$BINARY" | cut -f1)
  echo ""
  echo "=== Build successful ==="
  echo "Binary: $BINARY"
  echo "Size: $SIZE"
else
  echo "ERROR: Build failed — binary not found at $BINARY"
  exit 1
fi
