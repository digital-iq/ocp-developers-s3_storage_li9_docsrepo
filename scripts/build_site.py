#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import shutil
import subprocess
from pathlib import Path


SOURCES = [
    {
        "name": "operator",
        "label": "Operator and OpenShift platform docs",
        "path": "_sources/operator/docs/site",
        "destination": ".",
        "required": True,
    },
    {
        "name": "runtime",
        "label": "Runtime and S3 service docs",
        "path": "_sources/runtime/docs/site",
        "destination": "runtime",
        "required": True,
    },
    {
        "name": "helm",
        "label": "Helm installation docs",
        "path": "_sources/helmchart/docs/site",
        "destination": ".",
        "required": False,
    },
    {
        "name": "linux",
        "label": "Linux native installation docs",
        "path": "_sources/linux-installer/docs/site",
        "destination": ".",
        "required": False,
    },
    {
        "name": "windows",
        "label": "Windows native installation docs",
        "path": "_sources/windows-installer/docs/site",
        "destination": ".",
        "required": False,
    },
]


def repo_revision(path: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def copy_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def write_source_report(output: Path, records: list[dict[str, str]]) -> None:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(record['label'])}</td>"
        f"<td><code>{html.escape(record['name'])}</code></td>"
        f"<td><code>{html.escape(record['revision'])}</code></td>"
        f"<td>{html.escape(record['status'])}</td>"
        "</tr>"
        for record in records
    )
    page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Li9 S3 Documentation Sources</title>
    <link rel="stylesheet" href="assets/styles.css">
  </head>
  <body>
    <main class="content">
      <nav class="breadcrumbs"><a href="index.html">Li9 S3 Storage</a> / Documentation Sources</nav>
      <section class="hero">
        <p class="eyebrow">Publication Metadata</p>
        <h1>Documentation source revisions.</h1>
        <p class="lede">This page records the component repositories used to publish the public documentation site.</p>
      </section>
      <table>
        <thead><tr><th>Source</th><th>Key</th><th>Revision</th><th>Status</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </main>
  </body>
</html>
"""
    (output / "docs-sources.html").write_text(page, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources-root", default=".")
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()

    root = Path(args.sources_root).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    records: list[dict[str, str]] = []
    for source in SOURCES:
        source_path = root / source["path"]
        repo_path = source_path.parent.parent
        destination = output / source["destination"]
        if not source_path.exists():
            if source["required"]:
                raise SystemExit(f"required documentation source missing: {source_path}")
            records.append(
                {
                    "name": source["name"],
                    "label": source["label"],
                    "revision": repo_revision(repo_path),
                    "status": "not present",
                }
            )
            continue
        copy_contents(source_path, destination)
        records.append(
            {
                "name": source["name"],
                "label": source["label"],
                "revision": repo_revision(repo_path),
                "status": f"published to /{source['destination'].strip('.')}",
            }
        )

    (output / ".nojekyll").write_text("", encoding="utf-8")
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    metadata = {
        "publishedAt": dt.datetime.now(dt.UTC).isoformat(),
        "component": "public-docs",
        "sources": records,
    }
    (assets / "docs-public-build.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_source_report(output, records)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
