#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path


REPOSITORY = "https://github.com/digital-iq/ocp-developers-s3_storage_li9_docsrepo.git"
SOURCE_REPOSITORIES = {
    "operator": "https://github.com/digital-iq/ocp-developers-s3_storage_li9_operators.git",
    "runtime": "https://github.com/digital-iq/ocp-developers-s3_storage-code.git",
    "helmchart": "https://github.com/digital-iq/ocp-developers-s3_storage_li9_helmchart.git",
    "linux-installer": "https://github.com/digital-iq/ocp-developers-s3_storage_linux_installer.git",
    "windows-installer": "https://github.com/digital-iq/ocp-developers-s3_storage_windows_installer.git",
}


def run(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=True,
    )


def write_askpass(directory: Path) -> Path:
    askpass = directory / "git-askpass.sh"
    askpass.write_text(
        """#!/usr/bin/env sh
case "$1" in
  *Username*) echo "x-access-token" ;;
  *Password*) echo "${DOCS_SOURCE_TOKEN}" ;;
  *) echo "" ;;
esac
""",
        encoding="utf-8",
    )
    askpass.chmod(askpass.stat().st_mode | stat.S_IXUSR)
    return askpass


def auth_env(askpass: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_ASKPASS"] = str(askpass)
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def clone_sources(root: Path, ref: str, env: dict[str, str]) -> None:
    sources = root / "_sources"
    if sources.exists():
        shutil.rmtree(sources)
    sources.mkdir(parents=True)
    for name, url in SOURCE_REPOSITORIES.items():
        destination = sources / name
        run(["git", "clone", "--depth", "1", "--branch", ref, url, str(destination)], cwd=root, env=env)


def copy_tree_contents(source: Path, destination: Path) -> None:
    for item in destination.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def branch_exists(repo_url: str, branch: str, env: dict[str, str]) -> bool:
    result = run(["git", "ls-remote", "--heads", repo_url, branch], env=env, capture=True)
    return bool(result.stdout.strip())


def publish_branch(root: Path, repo_url: str, branch: str, env: dict[str, str]) -> None:
    output = root / "_site"
    if not output.exists():
        raise SystemExit(f"site output missing: {output}")
    with tempfile.TemporaryDirectory(prefix="li9-s3-docs-pages-") as tmp:
        publish_dir = Path(tmp) / "pages"
        run(["git", "init", str(publish_dir)])
        run(["git", "remote", "add", "origin", repo_url], cwd=publish_dir)
        if branch_exists(repo_url, branch, env):
            run(["git", "fetch", "--depth", "1", "origin", branch], cwd=publish_dir, env=env)
            run(["git", "checkout", "-B", branch, "FETCH_HEAD"], cwd=publish_dir)
        else:
            run(["git", "checkout", "--orphan", branch], cwd=publish_dir)
        copy_tree_contents(output, publish_dir)
        run(["git", "config", "user.name", "li9-s3-docs-ci"], cwd=publish_dir)
        run(["git", "config", "user.email", "docs@li9.com"], cwd=publish_dir)
        run(["git", "add", "-A"], cwd=publish_dir)
        changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=publish_dir)
        if changed.returncode == 0:
            print("public documentation site is already up to date")
            return
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        run(["git", "commit", "-m", f"Publish Li9 S3 documentation {timestamp}"], cwd=publish_dir)
        run(["git", "push", "origin", branch], cwd=publish_dir, env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-ref", default="main")
    parser.add_argument("--output-branch", default="gh-pages")
    parser.add_argument("--repo-url", default=os.environ.get("DOCS_PUBLIC_REPOSITORY_URL", REPOSITORY))
    parser.add_argument("--public-base-path", default=os.environ.get("DOCS_PUBLIC_BASE_PATH", ""))
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("DOCS_SOURCE_TOKEN") or os.environ.get("DOCS_PUBLISH_TOKEN") or os.environ.get("DOCS_REPO_DISPATCH_TOKEN")
    if not token:
        raise SystemExit("DOCS_SOURCE_TOKEN, DOCS_PUBLISH_TOKEN, or DOCS_REPO_DISPATCH_TOKEN must be configured")
    os.environ["DOCS_SOURCE_TOKEN"] = token

    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="li9-s3-docs-auth-") as tmp:
        askpass = write_askpass(Path(tmp))
        env = auth_env(askpass)
        clone_sources(root, args.source_ref, env)
        build_args = ["python3", "scripts/build_site.py", "--sources-root", ".", "--output", "_site"]
        if args.public_base_path:
            build_args.extend(["--public-base-path", args.public_base_path])
        run(build_args, cwd=root, env=env)
        if args.publish:
            publish_branch(root, args.repo_url, args.output_branch, env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
