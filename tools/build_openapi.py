#!/usr/bin/env python3
"""Write docs/openapi.json from the route table, or verify it is current."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build" / "py"))

from mynastock.http.openapi import document  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()

text = json.dumps(document(), indent=2) + "\n"
target = ROOT / "docs" / "api" / "openapi.json"

if args.check:
    if not target.is_file() or target.read_text(encoding="utf-8") != text:
        print("openapi: docs/openapi.json is stale; run `make openapi`", file=sys.stderr)
        raise SystemExit(1)
    print("openapi: current")
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"openapi: wrote {target.relative_to(ROOT)} ({len(text)} bytes)")
