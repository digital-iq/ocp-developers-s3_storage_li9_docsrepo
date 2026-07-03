#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
from urllib.parse import quote
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


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def first_match(patterns: list[tuple[Path, str]], default: str = "unknown") -> str:
    for path, pattern in patterns:
        content = read_text_if_exists(path)
        if not content:
            continue
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
    return default


def release_metadata(root: Path, records: list[dict[str, str]], published_at: str) -> dict[str, str]:
    operator_revision = next((record["revision"] for record in records if record["name"] == "operator"), "unknown")
    operator_version = os.environ.get("LI9_OPERATOR_VERSION") or first_match(
        [
            (root / "_sources/operator/docs/site/install-openshift-installation.html", r"LI9_OPERATOR_VERSION=([A-Za-z0-9._-]+)"),
            (root / "_sources/operator/docs/site/install-airgap-installation.html", r"LI9_OPERATOR_VERSION=([A-Za-z0-9._-]+)"),
        ]
    )
    runtime_version = os.environ.get("LI9_RUNTIME_VERSION") or first_match(
        [
            (root / "_sources/operator/docs/site/install-airgap-installation.html", r"LI9_RUNTIME_VERSION=([A-Za-z0-9._-]+)"),
            (root / "_sources/runtime/VERSION", r"^(.+)$"),
        ],
        default=operator_version,
    )
    helm_version = os.environ.get("LI9_CHART_VERSION") or first_match(
        [
            (root / "_sources/helmchart/charts/li9-s3-storage/Chart.yaml", r"^version:\s*([A-Za-z0-9._-]+)\s*$"),
            (root / "_sources/operator/docs/site/install-helm-installation.html", r"LI9_CHART_VERSION=([A-Za-z0-9._-]+)"),
        ],
        default=runtime_version,
    )
    linux_version = os.environ.get("LI9_LINUX_VERSION") or first_match(
        [(root / "_sources/linux-installer/VERSION", r"^(.+)$")],
        default=runtime_version,
    )
    windows_version = os.environ.get("LI9_WINDOWS_VERSION") or first_match(
        [(root / "_sources/windows-installer/VERSION", r"^(.+)$")],
        default=runtime_version,
    )
    source_revision = os.environ.get("GITHUB_SHA", operator_revision)
    return {
        "buildTag": os.environ.get("DOCS_BUILD_TAG", operator_version),
        "component": "public-docs",
        "helmChartVersion": helm_version,
        "linuxInstallerVersion": linux_version,
        "operatorVersion": operator_version,
        "publishedAt": published_at,
        "runtimeVersion": runtime_version,
        "sourceRevision": source_revision,
        "version": operator_version,
        "windowsInstallerVersion": windows_version,
    }


def normalize_public_base_path(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not value.startswith("/"):
        value = "/" + value
    return value.rstrip("/")


def rewrite_root_relative_links(output: Path, public_base_path: str) -> None:
    public_base_path = normalize_public_base_path(public_base_path)
    if not public_base_path:
        return
    pattern = re.compile(r'\b(href|src)="(/(?!/)[^"]*)"')

    def replace(match: re.Match[str]) -> str:
        attr = match.group(1)
        value = match.group(2)
        return f'{attr}="{public_base_path}{value}"'

    for page in output.rglob("*.html"):
        content = page.read_text(encoding="utf-8")
        updated = pattern.sub(replace, content)
        if updated != content:
            page.write_text(updated, encoding="utf-8")


def version_static_assets(output: Path, version: str) -> None:
    version = quote(version, safe="")
    pattern = re.compile(r'\b(href|src)="([^"#?]+?\.(?:css|js))"')

    def replace(match: re.Match[str]) -> str:
        attr = match.group(1)
        value = match.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", value, re.IGNORECASE) or value.startswith("//"):
            return match.group(0)
        return f'{attr}="{value}?v={version}"'

    for page in output.rglob("*.html"):
        content = page.read_text(encoding="utf-8")
        updated = pattern.sub(replace, content)
        if updated != content:
            page.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources-root", default=".")
    parser.add_argument("--output", default="_site")
    parser.add_argument("--public-base-path", default="")
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
    build_metadata = release_metadata(root, records, metadata["publishedAt"])
    metadata["release"] = build_metadata
    (assets / "docs-public-build.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (assets / "build.json").write_text(
        json.dumps(build_metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_source_report(output, records)
    rewrite_root_relative_links(output, args.public_base_path)
    version_static_assets(output, metadata["publishedAt"])
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
