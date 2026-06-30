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

The `Publish Li9 S3 Documentation` workflow checks out those private source
repositories, assembles a static site into `_site`, and publishes it through
GitHub Pages.

Public site:

```text
https://digital-iq.github.io/ocp-developers-s3_storage_li9_docsrepo/
```

## Pipeline

The workflow runs on:

- `workflow_dispatch` for manual publication.
- `repository_dispatch` from component repositories after documentation or
  release artifacts change.
- `push` to this repository.

Required repository secret:

- `DOCS_SOURCE_TOKEN`: token with read access to the private component source
  repositories.

The published site also includes:

- `/runtime/` for runtime documentation.
- `/assets/docs-public-build.json` for source repository revisions used in the
  publication.
- `/docs-sources.html` for a human-readable source revision report.

Do not edit generated site output by hand. Change the owning component
repository and let the workflow publish a new site.
