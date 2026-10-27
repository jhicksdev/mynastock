#!/usr/bin/env python3
"""Fail on missing local assets and oversized artifacts in site/."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REQUIRED = [
    "index.html",
    "404.html",
    "source.html",
    "demo/index.html",
    "demo/app.js",
    "demo/styles.css",
    "data/source.json",
    "assets/landing.css",
    "assets/source.css",
    ".nojekyll",
]
REFERENCE = re.compile(r'(?:src|href)="([^"]+)"')
EXTERNAL = ("http://", "https://", "mailto:", "data:", "javascript:")

status = 0
for rel in REQUIRED:
    if not (SITE / rel).is_file():
        print(f"audit: missing {rel}")
        status = 1

pages = 0
for page in sorted(SITE.rglob("*.html")):
    pages += 1
    for reference in REFERENCE.findall(page.read_text(encoding="utf-8")):
        ref = reference.split("#")[0].split("?")[0]
        if not ref or ref.startswith(EXTERNAL) or ref.startswith("#"):
            continue
        target = (page.parent / ref).resolve()
        if ref.endswith("/"):
            target = target / "index.html"
        if not target.exists() and not (target.is_dir() and (target / "index.html").exists()):
            print(f"audit: {page.relative_to(SITE)} -> missing {reference}")
            status = 1

app = SITE / "demo" / "app.js"
if app.is_file() and app.stat().st_size > 200_000:
    print(f"audit: demo/app.js is {app.stat().st_size} bytes (budget 200000)")
    status = 1

total = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
if total > 8_000_000:
    print(f"audit: site is {total} bytes (budget 8000000)")
    status = 1

if status == 0:
    print(f"audit: ok ({pages} pages, {total // 1024} KB)")
raise SystemExit(status)
