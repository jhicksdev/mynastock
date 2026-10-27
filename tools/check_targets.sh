#!/usr/bin/env bash
# Portable modules must declare both targets. Since myna 0.4.1 and later rejects relative
# imports per file for the JS target, the executable check runs on the assembled
# single-file artifact (the thing that actually ships to the browser).
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if ! grep -qx '@target(py, js)' "$f"; then
    echo "targets: $f must declare @target(py, js)"
    status=1
  fi
done < tools/portable.txt

python3 tools/assemble.py build/js/portable.myna >/dev/null
report="$(myna targets build/js/portable.myna)"
if ! grep -Eq '^Declared *:.*(^|[^a-z])js([^a-z]|$)' <<<"$report"; then
  echo "targets: assembled portable module is not declared for js"
  echo "$report"
  status=1
fi
if ! grep -Eq '^js *: *supported' <<<"$report"; then
  echo "targets: assembled portable module does not generate for js"
  echo "$report"
  status=1
fi

python3 tools/assemble.py --extra tools/web.txt build/demo.myna >/dev/null
web_report="$(myna targets build/demo.myna)"
if ! grep -Eq '^js *: *supported' <<<"$web_report"; then
  echo "targets: assembled demo module does not generate for js"
  echo "$web_report"
  status=1
fi

exit "$status"
