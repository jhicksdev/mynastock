#!/usr/bin/env python3
"""Portable modules may only import other portable modules, and only relatively."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTED = [
    line.strip()
    for line in (ROOT / "tools/portable.txt").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
PORTABLE = {(ROOT / rel).resolve() for rel in LISTED}

IMPORT = re.compile(r"^\s*(\.*)([A-Za-z_][\w.]*)")
status = 0

for rel in LISTED:
    path = (ROOT / rel).resolve()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.lstrip().startswith("<"):
            continue
        match = IMPORT.match(line.strip()[1:])
        if not match:
            print(f"{rel}:{lineno}: cannot parse import: {line.strip()}")
            status = 1
            continue
        dots, module = match.group(1), match.group(2)
        if not dots:
            print(f"{rel}:{lineno}: absolute import is not allowed in portable code")
            status = 1
            continue
        base = path.parent
        for _ in range(len(dots) - 1):
            base = base.parent
        target = (base / (module.replace(".", "/") + ".myna")).resolve()
        if not target.is_file():
            print(f"{rel}:{lineno}: cannot resolve {line.strip()} -> {target}")
            status = 1
        elif target not in PORTABLE:
            print(f"{rel}:{lineno}: imports non-portable module {target}")
            status = 1

sys.exit(status)
