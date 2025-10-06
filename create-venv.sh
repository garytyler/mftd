#!/usr/bin/env bash
set -euo pipefail

# Config — change if needed
PY=python3.11

echo "Recreating .venv (no pip, no symlinks)…"
rm -rf .venv
if ! $PY -m venv --copies --without-pip .venv 2>/dev/null; then
  echo "venv --copies failed; trying virtualenv --copies…"
  $PY -m pip install -U virtualenv
  $PY -m virtualenv --copies .venv
fi

# On macOS, a copied venv may need libpython inside .venv/lib for the loader path
echo "Ensuring libpython is available inside .venv/lib…"
LIBDIR="$($PY -c 'import sysconfig;print(sysconfig.get_config_var("LIBDIR") or "")')"
LDV="$($PY -c 'import sysconfig;print(sysconfig.get_config_var("LDVERSION") or sysconfig.get_config_var("VERSION"))')"

if [[ -z "$LIBDIR" || -z "$LDV" ]]; then
  echo "Could not determine LIBDIR/LDVERSION from $PY" >&2
  exit 1
fi

SRC_LIB="$LIBDIR/libpython${LDV}.dylib"
DEST_DIR=".venv/lib"
DEST_LIB="$DEST_DIR/libpython${LDV}.dylib"

mkdir -p "$DEST_DIR"
if [[ ! -f "$SRC_LIB" ]]; then
  echo "Expected lib not found: $SRC_LIB" >&2
  echo "Tip: On Homebrew this is often at /opt/homebrew/Frameworks/Python.framework/Versions/${LDV%*m}/lib/libpython${LDV}.dylib" >&2
  exit 1
fi

cp -f "$SRC_LIB" "$DEST_LIB"

# Quick loader sanity check
echo "Checking loader paths…"
otool -L .venv/bin/python3 | sed 's/^/  /'
if ! .venv/bin/python3 -V >/dev/null 2>&1; then
  echo "ERROR: .venv/bin/python3 still not runnable after lib copy." >&2
  exit 1
fi

# Install/update packages via uv with full copy mode (no links/hardlinks)
echo "Syncing deps with uv (copy mode)…"
# Make copy mode the default for this command:
UV_LINK_MODE=copy uv sync --python .venv/bin/python

# Optional: verify there are truly no symlinks anywhere under .venv
echo "Verifying no symlinks exist under .venv…"
if find .venv -type l -print -quit | grep -q .; then
  echo "ERROR: Found symlink(s) inside .venv:" >&2
  find .venv -type l >&2
  exit 1
fi

echo "Success: thick .venv + uv-installed packages with NO symlinks."