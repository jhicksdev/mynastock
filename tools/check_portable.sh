#!/usr/bin/env bash
# Portable modules may not import anything or rely on exception/constructor syntax
# that does not survive the JS target (see docs/adr/0001-portable-core.md).
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  while IFS= read -r hit; do
    echo "portable: $f:$hit"
    status=1
  done < <(grep -nE '^[[:space:]]*<|!\^|!!|!\{|!&|!\?|\bnew[[:space:]]' "$f" || true)
done < tools/portable.txt

exit "$status"
