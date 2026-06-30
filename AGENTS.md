# Repository Instructions

This repository publishes the public Li9 S3 Storage documentation site.

- Treat component repositories as the source of truth. Do not hand-edit copied
  generated HTML in this repository.
- Keep publication logic in `.github/workflows/publish.yml` and
  `scripts/build_site.py`.
- The workflow must not require public read access to private source
  repositories; use `DOCS_SOURCE_TOKEN`.
- Keep GitHub Pages output static and self-contained under `_site`.
- Never commit credentials, registry tokens, cluster URLs from test
  environments, or screenshots containing environment-specific hostnames.
