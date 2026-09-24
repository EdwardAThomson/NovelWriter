#!/bin/bash
# Prepares a Claude Code on the web session to run NovelWriter's test suite.
#
# The images these sessions start from default to an older python3 than
# NovelWriter needs (see .python-version), and start with none of the project's
# dependencies installed. This builds a virtualenv on a new enough interpreter,
# installs the requirements into it, and puts it on PATH for the session.
set -euo pipefail

# Local checkouts manage their own environments; this is only for the web.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR"

VENV="$PROJECT_DIR/.venv"
REQUIRED_MINOR=12  # keep in step with .python-version and main.py

# Pick an interpreter that is new enough. The named binaries come first because
# the bare `python3` on these images is usually older than we need.
find_python() {
  local candidate
  for candidate in python3.12 python3.13 python3.14 python3; do
    if command -v "$candidate" >/dev/null 2>&1 \
       && "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, $REQUIRED_MINOR) else 1)" 2>/dev/null; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

if ! PYTHON="$(find_python)"; then
  echo "session-start: no Python 3.$REQUIRED_MINOR+ found; skipping dependency install." >&2
  exit 0
fi

# Rebuild the venv if it is missing or was built on too old an interpreter, so
# a cached container from before a version bump does not silently keep the old one.
if [ -x "$VENV/bin/python" ] \
   && ! "$VENV/bin/python" -c "import sys; sys.exit(0 if sys.version_info >= (3, $REQUIRED_MINOR) else 1)" 2>/dev/null; then
  echo "session-start: existing .venv is too old, rebuilding."
  rm -rf "$VENV"
fi

if [ ! -x "$VENV/bin/python" ]; then
  echo "session-start: creating .venv with $PYTHON ($("$PYTHON" --version))"
  "$PYTHON" -m venv "$VENV"
fi

echo "session-start: installing dependencies (this takes a couple of minutes on a cold container)"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -r requirements.txt
# pytest is not in requirements.txt - it is only needed to run the test suite.
"$VENV/bin/python" -m pip install --quiet pytest

# Make the venv the default interpreter for the rest of the session, so
# `python`, `pip` and `pytest` are the right ones without being told.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export VIRTUAL_ENV=\"$VENV\""
    echo "export PATH=\"$VENV/bin:\$PATH\""
  } >> "$CLAUDE_ENV_FILE"
fi

echo "session-start: ready - $("$VENV/bin/python" --version), run the tests with: pytest tests/"
