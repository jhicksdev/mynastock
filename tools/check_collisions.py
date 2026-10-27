#!/usr/bin/env python3
"""Reject locals that shadow a module-level name in the assembled namespace.

myna 0.4.2 emits `x = ...` (no `let`) for a local assignment when `x` also names a
module-level binding. In Python that assignment is function-local; in JS it overwrites
the outer binding. Because tools/assemble.py merges modules into one scope, a local in
one module can clobber a function in another. Rename the local.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECLARATION = re.compile(r"^(\+?@\w+|\+?\$\$?\w+|[A-Z][A-Z0-9_]*)\s*[={(<:-]")
ASSIGNMENT = re.compile(r"^\s+([a-z_][A-Za-z0-9_]*)\s*=")
LOOP = re.compile(r"^\s*%\s*([a-z_][A-Za-z0-9_,\s]*?)\s*<-")


def read_manifest(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", help="additional manifest to scan")
    args = parser.parse_args()

    listed = read_manifest(ROOT / "tools/portable.txt")
    if args.extra:
        listed += read_manifest(ROOT / args.extra)

    declared: dict[str, str] = {}
    for rel in listed:
        for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
            match = DECLARATION.match(line)
            if match:
                name = match.group(1).lstrip("+$@")
                declared.setdefault(name, rel)

    status = 0
    for rel in listed:
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

    return status


if __name__ == "__main__":
    raise SystemExit(main())
