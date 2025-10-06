#!/usr/bin/env bash
set -euo pipefail

# 1) Pick a solid interpreter (Homebrew 3.11):
PY="/opt/homebrew/opt/python@3.11/bin/python3.11"

# 2) Recreate a thick venv with NO ensurepip:
rm -rf .venv
"$PY" -m venv --copies --without-pip .venv

# 3) Copy libpython into place so the loader path resolves:
LIBDIR="$("$PY" -c 'import sysconfig;print(sysconfig.get_config_var("LIBDIR"))')"
LDV="$("$PY" -c 'import sysconfig;print(sysconfig.get_config_var("LDVERSION") or sysconfig.get_config_var("VERSION"))')"
mkdir -p .venv/lib
cp -f "$LIBDIR/libpython${LDV}.dylib" ".venv/lib/libpython${LDV}.dylib"

# 4) Sanity check that the venv’s python runs:
otool -L .venv/bin/python3 | sed 's/^/  /'
.venv/bin/python3 -V

# 5) Use uv in full copy mode to install from your pyproject/uv.lock:
UV_LINK_MODE=copy uv sync --python .venv/bin/python3.11

# 6) Prove there are no links in the venv:
find .venv -type l -print