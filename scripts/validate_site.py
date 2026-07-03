#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen


FORBIDDEN_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"console-openshift-console\.apps\.",
        r"oauth-openshift\.apps\.",
        r"api\.mgm01\.prd-ovh\.dc\.li9\.com",
        r"apps\.mgm01\.prd-ovh\.dc\.li9\.com",
        r"avishnya-[a-z0-9-]+\.ephemeral-ovh\.dev\.li9\.com",
        r"127\.0\.0\.1:8099",
        r"localhost:8099",
        r"github_pat_",
        r"quay\.io/.+:[A-Za-z0-9]{20,}",
    ]
]

LI9_QUAY_IMAGE_PATTERN = re.compile(r"\bquay\.io/li9/li9-operators:([A-Za-z0-9._-]+)")
MANIFEST_ACCEPT = (
    "application/vnd.oci.image.index.v1+json, "
    "application/vnd.oci.image.manifest.v1+json, "
    "application/vnd.docker.distribution.manifest.list.v2+json, "
    "application/vnd.docker.distribution.manifest.v2+json"
)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_names = {"a": "href", "link": "href", "script": "src", "img": "src"}
        attr_name = attr_names.get(tag)
        if not attr_name:
            return
        for name, value in attrs:
            if name == attr_name and value:
                self.links.append((tag, value))


def is_external(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.scheme not in {"file"})


def target_path(root: Path, page: Path, value: str) -> Path | None:
    if value.startswith("#") or value.startswith("mailto:") or value.startswith("tel:"):
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    if path.startswith("/ocp-developers-s3_storage_li9_docsrepo/"):
        path = path.removeprefix("/ocp-developers-s3_storage_li9_docsrepo/")
    elif path.startswith("/"):
        path = path.lstrip("/")
    base = root if path.startswith((".", "/")) or value.startswith("/") else page.parent
    candidate = (base / path).resolve()
    if candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".html", ".css", ".js", ".json", ".md"}:
            content = path.read_text(encoding="utf-8", errors="replace")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(content):
                    errors.append(f"{path.relative_to(root)} contains forbidden environment or secret pattern: {pattern.pattern}")
        if path.suffix.lower() != ".html":
            continue
        collector = LinkCollector()
        collector.feed(path.read_text(encoding="utf-8", errors="replace"))
        for tag, value in collector.links:
            if is_external(value):
                continue
            candidate = target_path(root, path, value)
            if candidate is None:
                continue
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{path.relative_to(root)} links outside site root: {value}")
                continue
            if not candidate.exists():
                errors.append(f"{path.relative_to(root)} has broken {tag} link: {value}")
    return errors


def quay_pull_token(repository: str) -> str:
    query = urlencode({"service": "quay.io", "scope": f"repository:{repository}:pull"})
    request = Request(f"https://quay.io/v2/auth?{query}")
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    token = payload.get("token") or payload.get("access_token")
    if not token:
        raise RuntimeError(f"Quay did not return an anonymous pull token for {repository}")
    return token


def documented_li9_images(root: Path) -> set[str]:
    images: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".css", ".js", ".json", ".md"}:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for match in LI9_QUAY_IMAGE_PATTERN.finditer(content):
            images.add(f"quay.io/li9/li9-operators:{match.group(1)}")
    return images


def validate_public_li9_images(root: Path) -> list[str]:
    errors: list[str] = []
    images = sorted(documented_li9_images(root))
    if not images:
        return errors
    token = quay_pull_token("li9/li9-operators")
    for image in images:
        tag = image.rsplit(":", 1)[1]
        manifest_url = f"https://quay.io/v2/li9/li9-operators/manifests/{quote(tag, safe='')}"
        request = Request(manifest_url, headers={"Accept": MANIFEST_ACCEPT, "Authorization": f"Bearer {token}"})
        try:
            with urlopen(request, timeout=30) as response:
                if response.status < 200 or response.status >= 300:
                    errors.append(f"documented image is not publicly pullable: {image} returned HTTP {response.status}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"documented image is not publicly pullable: {image}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", default="_site")
    parser.add_argument("--skip-public-image-check", action="store_true")
    args = parser.parse_args()
    root = Path(args.site_root).resolve()
    if not root.exists():
        raise SystemExit(f"site root does not exist: {root}")
    errors = validate(root)
    if not args.skip_public_image_check:
        errors.extend(validate_public_li9_images(root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"validated {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
