# Repository Instructions

This repository publishes the public Li9 S3 Storage documentation site.

- Treat component repositories as the source of truth. Do not hand-edit copied
  generated HTML in this repository.
- Keep publication logic in `scripts/build_site.py` and
  `scripts/publish_site.py`.
- Component repository pipelines publish the generated `_site` output to the
  `gh-pages` branch. This public repository does not require its own runner.
- The publication flow must not require public read access to private source
  repositories; use `DOCS_SOURCE_TOKEN` or the component repository publication
  token in CI.
- Keep GitHub Pages output static and self-contained under `_site` before it is
  copied to `gh-pages`.
- Never commit credentials, registry tokens, cluster URLs from test
  environments, or screenshots containing environment-specific hostnames.
