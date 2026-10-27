#!/usr/bin/env python3
"""Portable (and web) modules may only import allowlisted modules, and only relatively."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMPORT = re.compile(r"^\s*(\.*)([A-Za-z_][\w.]*)")


def read_manifest(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", help="additional manifest to check")
    args = parser.parse_args()

    portable = read_manifest(ROOT / "tools/portable.txt")
    listed = list(portable)
    if args.extra:
        listed += read_manifest(ROOT / args.extra)

    allowed = {(ROOT / rel).resolve() for rel in listed}
    status = 0

    for rel in listed:
        path = (ROOT / rel).resolve()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("<"):
                continue
            match = IMPORT.match(line.strip()[1:])
            if not match:
                print(f"{rel}:{lineno}: cannot parse import: {line.strip()}")
                status = 1
                continue
            dots, module = match.group(1), match.group(2)
            if not dots:
                print(f"{rel}:{lineno}: absolute import is not allowed here")
                status = 1
                continue
            base = path.parent
            for _ in range(len(dots) - 1):
                base = base.parent
            target = (base / (module.replace(".", "/") + ".myna")).resolve()
            if not target.is_file():
                print(f"{rel}:{lineno}: cannot resolve {line.strip()} -> {target}")
                status = 1
            elif target not in allowed:
                print(f"{rel}:{lineno}: imports non-portable module {target}")
                status = 1

    return status


if __name__ == "__main__":
    raise SystemExit(main())
