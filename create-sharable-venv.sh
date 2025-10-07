#!/usr/bin/env bash
set -euo pipefail

THIS_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
VENV="$THIS_DIR/.venv"
PY="/opt/homebrew/opt/python@3.11/bin/python3.11"

echo "==> Using base Python: $PY"
"$PY" -V

# Make sure virtualenv exists for THIS Python
if ! "$PY" -m virtualenv --version >/dev/null 2>&1; then
  echo "==> Installing virtualenv for $PY"
  "$PY" -m pip install --upgrade virtualenv
fi

echo "==> Removing old venv (if any)"
rm -rf "$VENV"

echo "==> Creating venv (default behavior; we'll de-symlink afterwards)"
"$PY" -m virtualenv -p "$PY" "$VENV"

# --- De-symlink the interpreter binaries ---
echo "==> Replacing bin/python* symlinks with real binaries"
REAL_PY="$("$PY" -c 'import os,sys; print(os.path.realpath(sys.executable))')"
for NAME in python3.11 python3 python; do
  TGT="$VENV/bin/$NAME"
  if [ -e "$TGT" ]; then
    if [ -L "$TGT" ]; then
      rm -f "$TGT"
      cp -Lp "$REAL_PY" "$TGT"
      chmod +x "$TGT"
      echo "    converted $TGT -> real copy"
    else
      echo "    $TGT already a real file"
    fi
  fi
done

# --- Vendor libpython for macOS loader path stability ---
echo "==> Vendoring libpython into venv/lib"
LIBDIR="$("$PY" -c 'import sysconfig;print(sysconfig.get_config_var("LIBDIR"))')"
LDV="$("$PY" -c 'import sysconfig;print(sysconfig.get_config_var("LDVERSION") or sysconfig.get_config_var("VERSION"))')"
mkdir -p "$VENV/lib"
cp -f "$LIBDIR/libpython${LDV}.dylib" "$VENV/lib/libpython${LDV}.dylib" || true

# --- Sanity checks ---
echo "==> Sanity check: python runs and links resolve"
"$VENV/bin/python3.11" -V
otool -L "$VENV/bin/python3.11" | sed 's/^/  /'

# --- Ensure pip tooling (PyCharm likes this) ---
echo "==> Ensuring pip/setuptools/wheel are available"
"$VENV/bin/python" -m ensurepip --upgrade || true
"$VENV/bin/python" -m pip install --upgrade pip setuptools wheel

# --- Install deps with uv without symlinks ---
echo "==> Installing project deps with uv (copy mode)"
UV_LINK_MODE=copy uv sync --python "$VENV/bin/python3.11"

# --- Verify no symlinks remain ---
echo "==> Verifying no symlinks remain in venv"
if find "$VENV" -type l -print | grep -q .; then
  echo "WARNING: some symlinks remain above (inspect as needed)."
else
  echo "OK: no symlinks found in $VENV"
fi

echo "==> Done. Select interpreter: $VENV/bin/python3.11 in PyCharm."