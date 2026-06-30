# Repository Instructions

This repository publishes the public Li9 S3 Storage documentation site.

- Treat component repositories as the source of truth. Do not hand-edit copied
  generated HTML in this repository.
- Keep publication logic in `.github/workflows/publish.yml`,
  `scripts/build_site.py`, and `scripts/publish_site.py`.
- The GitHub Pages workflow is allowed to use `ubuntu-latest` because this
  public repository does not currently have access to the OpenShift ARC runner
  group. Component repositories must continue to use their OpenShift runners.
- The publication flow must not require public read access to private source
  repositories; use `DOCS_SOURCE_TOKEN`.
- Keep GitHub Pages output static and self-contained under `_site`.
- Never commit credentials, registry tokens, cluster URLs from test
  environments, or screenshots containing environment-specific hostnames.
