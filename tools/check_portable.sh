#!/usr/bin/env bash
# Portable modules may not rely on exception or constructor syntax that does not
# survive the JS target, except for explicitly audited host boundaries.
# Imports are checked separately by tools/check_imports.py.
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if grep -qxF "$f" tools/exceptional.txt; then
    patterns='\bnew[[:space:]]'
  else
    patterns='!\^|!!|!\{|!&|!\?|\bnew[[:space:]]'
  fi
  while IFS= read -r hit; do
    echo "portable: $f:$hit"
    status=1
  done < <(grep -nE "$patterns" "$f" || true)
done < tools/portable.txt

exit "$status"
