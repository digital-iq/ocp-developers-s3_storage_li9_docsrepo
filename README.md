# Li9 S3 Storage Documentation

Public GitHub Pages documentation site for Li9 S3 Storage.

This repository is a generated publication target. Product documentation remains
owned by the component repositories:

- `ocp-developers-s3_storage_li9_operators` for OpenShift operator, CRDs,
  platform references, and the base documentation shell.
- `ocp-developers-s3_storage-code` for runtime, S3 API, service, and data-plane
  documentation.
- `ocp-developers-s3_storage_li9_helmchart` for Helm installation procedures.
- `ocp-developers-s3_storage_linux_installer` for native Linux installation
  procedures.
- `ocp-developers-s3_storage_windows_installer` for native Windows installation
  procedures.

Component CI pipelines check out this repository, assemble a static site into
`_site`, and publish the generated output to the `gh-pages` branch served by
GitHub Pages.

Public site:

```text
https://digital-iq.github.io/ocp-developers-s3_storage_li9_docsrepo/
```

## Publication

The public site is published by private component repositories after their own
validation gates:

- Operator source CI after the operator documentation image is built.
- Runtime source CI after the runtime documentation image is built.
- Helm chart CI after chart publication or docs-only changes.
- Linux installer CI after public package release or docs-only changes.
- Windows installer CI after public package release or docs-only changes.

Required component repository secret:

- `DOCS_REPO_DISPATCH_TOKEN`: token with read access to the private component
  repositories and write access to this public documentation repository.

Publication command used by component pipelines:

```bash
DOCS_SOURCE_TOKEN="${DOCS_REPO_DISPATCH_TOKEN}" \
  python3 scripts/publish_site.py --publish
```

The published site also includes:

- `/runtime/` for runtime documentation.
- `/assets/docs-public-build.json` for source repository revisions used in the
  publication.
- `/docs-sources.html` for a human-readable source revision report.

Do not edit generated site output by hand. Change the owning component
repository and let that component pipeline publish a new `gh-pages` revision.
