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


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.parts.append(value)

    @property
    def text(self) -> str:
        return " ".join(self.parts)


class TableCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_table = False
        self.table_class = ""
        self.current_cell: list[str] | None = None
        self.current_row: list[str] | None = None
        self.tables: list[tuple[str, list[list[str]]]] = []
        self._active_rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        if tag == "table":
            self.in_table = True
            self.table_class = attrs_dict.get("class", "")
            self._active_rows = []
        elif self.in_table and tag == "tr":
            self.current_row = []
        elif self.in_table and tag in {"td", "th"}:
            self.current_cell = []

    def handle_endtag(self, tag: str) -> None:
        if self.in_table and tag in {"td", "th"} and self.current_cell is not None and self.current_row is not None:
            self.current_row.append(" ".join(" ".join(self.current_cell).split()))
            self.current_cell = None
        elif self.in_table and tag == "tr" and self.current_row is not None:
            self._active_rows.append(self.current_row)
            self.current_row = None
        elif tag == "table" and self.in_table:
            self.tables.append((self.table_class, self._active_rows))
            self.in_table = False
            self.table_class = ""
            self._active_rows = []

    def handle_data(self, data: str) -> None:
        if self.current_cell is not None:
            self.current_cell.append(data)


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


def page_text(path: Path) -> str:
    collector = TextCollector()
    collector.feed(path.read_text(encoding="utf-8", errors="replace"))
    return collector.text


def require_page(errors: list[str], root: Path, relative: str) -> Path | None:
    path = root / relative
    if not path.exists():
        errors.append(f"required documentation page is missing: {relative}")
        return None
    content = path.read_text(encoding="utf-8", errors="replace")
    if len(content) < 3000:
        errors.append(f"{relative} is too small to be a complete customer-facing page")
    lower_text = page_text(path).lower()
    for placeholder in ["lorem ipsum", "todo", "tbd", "placeholder", "coming soon"]:
        if placeholder in lower_text:
            errors.append(f"{relative} contains placeholder text: {placeholder}")
    return path


def validate_platform_tracks(root: Path) -> list[str]:
    errors: list[str] = []
    tracks = {
        "openshift": ("OpenShift", "reference-openshift-operator.html"),
        "helm": ("Helm", "reference-helm-kubernetes.html"),
        "linux": ("Linux", "reference-linux-host.html"),
        "windows": ("Windows", "reference-windows-host.html"),
    }
    stages = ("prerequisites", "installation", "upgrade", "uninstall")
    for track, (label, reference_page) in tracks.items():
        require_page(errors, root, f"install-{track}.html")
        for stage in stages:
            path = require_page(errors, root, f"install-{track}-{stage}.html")
            if path is None:
                continue
            text = page_text(path)
            lower_text = text.lower()
            if label.lower() not in lower_text:
                errors.append(f"{path.relative_to(root)} does not identify the {label} installation track")
            if stage == "prerequisites":
                if "online prerequisites" not in lower_text:
                    errors.append(f"{path.relative_to(root)} must describe online prerequisites")
                if "air-gapped prerequisites" not in lower_text:
                    errors.append(f"{path.relative_to(root)} must describe air-gapped prerequisites")
            else:
                content = path.read_text(encoding="utf-8", errors="replace")
                if "<pre><code" not in content:
                    errors.append(f"{path.relative_to(root)} must include copy-paste command blocks")
                expected_word = {"installation": "install", "upgrade": "upgrade", "uninstall": "uninstall"}[stage]
                if expected_word not in lower_text:
                    errors.append(f"{path.relative_to(root)} does not describe {stage} actions")
        require_page(errors, root, reference_page)
    if not (root / "troubleshooting.html").exists():
        errors.append("troubleshooting.html is required for every public docs build")
    return errors


def collect_capability_reference_links(index_html: str) -> set[str]:
    collector = TableCollector()
    collector.feed(index_html)
    links = set(re.findall(r'href="(reference-[^"#?]+\.html)"[^>]*>\s*How to\s*</a>', index_html))
    # Keep this intentionally tied to capability tables: every row should expose a real reference link.
    for table_class, rows in collector.tables:
        if "capability-table" not in table_class:
            continue
        for row in rows[1:]:
            if len(row) < 3:
                continue
            if "How to" not in row[-1]:
                errors = getattr(collect_capability_reference_links, "_errors", [])
                errors.append(f"capability row missing How to link: {' | '.join(row)}")
                setattr(collect_capability_reference_links, "_errors", errors)
    return links


def validate_reference_pages(root: Path) -> list[str]:
    errors: list[str] = []
    index = root / "index.html"
    if not index.exists():
        return ["index.html is required for capability reference validation"]
    if hasattr(collect_capability_reference_links, "_errors"):
        delattr(collect_capability_reference_links, "_errors")
    links = collect_capability_reference_links(index.read_text(encoding="utf-8", errors="replace"))
    errors.extend(getattr(collect_capability_reference_links, "_errors", []))
    if len(links) < 30:
        errors.append(f"expected at least 30 capability reference links, found {len(links)}")
    for link in sorted(links):
        path = require_page(errors, root, link)
        if path is None:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        text = page_text(path).lower()
        if "class=\"docs-diagram\"" not in content:
            errors.append(f"{link} must include an engineering docs diagram")
        if "how to" not in text and "verify" not in text and "<pre><code" not in content and "<table" not in content:
            errors.append(f"{link} must include usable how-to, verification, or decision-table content")
    return errors


def validate_screenshots(root: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "openshift-installed-operator.png": "install-openshift-installation.html",
        "s3-console-bucket-browser.png": "install-openshift-installation.html",
        "s3-console-prefix-browser.png": "reference-platform-openshift-bucket-browser.html",
        "windows-installed-apps-uninstall.png": "install-windows-uninstall.html",
        "windows-services-installed.png": "install-windows-installation.html",
    }
    for name, page in required.items():
        image = root / "assets/screenshots" / name
        if not image.exists():
            errors.append(f"required screenshot is missing: assets/screenshots/{name}")
            continue
        if image.stat().st_size < 10_000:
            errors.append(f"screenshot appears empty or truncated: assets/screenshots/{name}")
        page_path = root / page
        if page_path.exists() and f"assets/screenshots/{name}" not in page_path.read_text(encoding="utf-8", errors="replace"):
            errors.append(f"{page} must reference assets/screenshots/{name}")
        raw = image.read_bytes()
        for pattern in FORBIDDEN_PATTERNS:
            try:
                decoded = raw.decode("latin1", errors="ignore")
            except Exception:
                decoded = ""
            if decoded and pattern.search(decoded):
                errors.append(f"assets/screenshots/{name} contains forbidden environment or secret pattern: {pattern.pattern}")
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
    errors.extend(validate_platform_tracks(root))
    errors.extend(validate_reference_pages(root))
    errors.extend(validate_screenshots(root))
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
