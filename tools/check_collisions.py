#!/usr/bin/env python3
"""Reject locals that shadow a module-level name in the assembled portable namespace.

myna 0.4.2 emits `x = ...` (no `let`) for a local assignment when `x` also names a
module-level binding. In Python that assignment is function-local; in JS it overwrites
the outer binding. Because tools/assemble.py merges modules into one scope, a local in
one module can clobber a function in another. Rename the local.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTED = [
    line.strip()
    for line in (ROOT / "tools/portable.txt").read_text(encoding="utf-8").splitlines()
    if line.strip()
]

DECLARATION = re.compile(r"^(\+?@\w+|\+?\$\$?\w+|[A-Z][A-Z0-9_]*)\s*[={(<:-]")
ASSIGNMENT = re.compile(r"^\s+([a-z_][A-Za-z0-9_]*)\s*=")
LOOP = re.compile(r"^\s*%\s*([a-z_][A-Za-z0-9_,\s]*?)\s*<-")

declared: dict[str, str] = {}
for rel in LISTED:
    for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
        match = DECLARATION.match(line)
        if match:
            name = match.group(1).lstrip("+$@")
            declared.setdefault(name, rel)

status = 0
for rel in LISTED:
    for lineno, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
        names = []
        assignment = ASSIGNMENT.match(line)
        if assignment:
            names.append(assignment.group(1))
        loop = LOOP.match(line)
        if loop:
            names.extend(part.strip() for part in loop.group(1).split(","))
        for name in names:
            if name in declared:
                print(f"{rel}:{lineno}: local {name!r} shadows module-level {declared[name]}")
                status = 1

sys.exit(status)
