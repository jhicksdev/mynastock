#!/usr/bin/env python3
"""Assemble the static site: landing page, browser demo, and source viewer.

Run after `make demo`: the demo bundle (site/demo/app.js) is produced there.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
MYNA = os.environ.get("MYNA", "myna")

COPIES = [
    ("web/landing.html", "index.html"),
    ("web/landing.css", "assets/landing.css"),
    ("web/source.css", "assets/source.css"),
    ("web/404.html", "404.html"),
    ("web/index.html", "demo/index.html"),
    ("web/styles.css", "demo/styles.css"),
]

CURATED = [
    "src/mynastock/core.myna",
    "src/mynastock/app/service.myna",
    "src/mynastock/http/router.myna",
    "src/mynastock/http/handlers.myna",
    "src/mynastock/adapters/sqlite.myna",
    "src/mynastock/db/seed.myna",
]


def run(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def compile_target(src: Path, out: Path, target: str | None):
    cmd = [MYNA, "compile"]
    if target:
        cmd += ["-t", target]
    cmd += [str(src), "-o", str(out)]
    result = run(cmd)
    if result.returncode != 0:
        return None
    return out.read_text(encoding="utf-8")


def token_stats(src: Path):
    result = run([MYNA, "stats", str(src)])
    if result.returncode != 0:
        return None
    python = re.search(r"Python tokens\s*:\s*(\d+)", result.stdout)
    myna = re.search(r"Myna tokens\s*:\s*(\d+)", result.stdout)
    if not python or not myna:
        return None
    py_tokens = int(python.group(1))
    myna_tokens = int(myna.group(1))
    reduction = round((py_tokens - myna_tokens) * 100 / py_tokens, 1) if py_tokens else 0
    return {"python_tokens": py_tokens, "myna_tokens": myna_tokens, "reduction_pct": reduction}


def render_source(entries) -> str:
    blocks = []
    for index, entry in enumerate(entries):
        stats = entry.get("stats") or {}
        chips = ""
        if stats:
            chips = (
                f'<span class="chip">{stats["myna_tokens"]} myna tok</span>'
                f'<span class="chip">{stats["python_tokens"]} python tok</span>'
                f'<span class="chip">{stats["reduction_pct"]}% smaller</span>'
            )
        js = entry.get("js")
        if js is None:
            js_block = (
                '<p class="missing">Not a stand-alone JS module: this file uses relative '
                "imports, which myna 0.4.2 rejects for the JavaScript target. The browser "
                "bundle assembles it into one module.</p>"
            )
        else:
            js_block = f"<pre><code>{html.escape(js)}</code></pre>"
        opened = " open" if index == 0 else ""
        blocks.append(
            f"""<section class="file">
  <h2>{html.escape(entry['path'].split('/')[-1])}</h2>
  <p class="path">{html.escape(entry['path'])}</p>
  <div class="chips">{chips}</div>
  <details{opened}><summary>Myna source</summary><pre><code>{html.escape(entry['myna'])}</code></pre></details>
  <details><summary>Python target</summary><pre><code>{html.escape(entry['py'])}</code></pre></details>
  <details><summary>JavaScript target</summary>{js_block}</details>
</section>"""
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Source viewer - MynaStock</title>
  <meta name="description" content="Myna source and transpiled Python and JavaScript for MynaStock.">
  <link rel="stylesheet" href="./assets/source.css">
</head>
<body>
  <header>
    <a class="brand" href="./">Myna<span>Stock</span></a>
    <nav><a href="./demo/">Live demo</a><a href="./">Home</a><a href="https://github.com/jhicksdev/mynastock">GitHub</a></nav>
  </header>
  <main>
    <h1>Source viewer</h1>
    <p class="lede">Real files from the repository with their generated Python and JavaScript. The browser demo uses the same source; relative imports are assembled into one module for the JS target.</p>
    {''.join(blocks)}
  </main>
  <footer><p>Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by <code>tools/build_site.py</code>. MIT licensed.</p></footer>
</body>
</html>
"""


def main() -> int:
    if not (SITE / "demo" / "app.js").exists():
        print("site: run `make demo` first (missing site/demo/app.js)", file=sys.stderr)
        return 1

    for source, destination in COPIES:
        target = SITE / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / source).read_bytes())

    entries = []
    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        for rel in CURATED:
            src = ROOT / rel
            stem = src.stem
            py = compile_target(src, temp / f"{stem}.py", None)
            js = compile_target(src, temp / f"{stem}.mjs", "js")
            if py is None:
                print(f"site: failed to compile {rel} to Python", file=sys.stderr)
                return 1
            entries.append(
                {
                    "path": rel,
                    "target": "py,js" if js is not None else "py",
                    "myna": src.read_text(encoding="utf-8"),
                    "py": py,
                    "js": js,
                    "stats": token_stats(src),
                }
            )

    data_dir = SITE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": entries,
    }
    (data_dir / "source.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (SITE / "source.html").write_text(render_source(entries), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"site: {len(entries)} source files, {sum(len(e['myna']) for e in entries)} bytes of Myna")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
