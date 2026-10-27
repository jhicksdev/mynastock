#!/usr/bin/env bash
# Every module listed as portable must declare both targets and actually generate for JS.
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if ! grep -qx '@target(py, js)' "$f"; then
    echo "targets: $f must declare @target(py, js)"
    status=1
    continue
  fi
  report="$(myna targets "$f")"
  if ! grep -Eq '^Declared *: *js, *py$' <<<"$report"; then
    echo "targets: $f is not declared for both targets"
    echo "$report"
    status=1
  fi
  if ! grep -Eq '^js *: *supported' <<<"$report"; then
    echo "targets: $f does not generate for js"
    status=1
  fi
done < tools/portable.txt

exit "$status"
