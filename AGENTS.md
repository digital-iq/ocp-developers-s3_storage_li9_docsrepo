# Repository Instructions

## Li9 S3 Repository Boundaries

Keep repository ownership strict. Do not move code, build logic, or release
artifacts across these boundaries unless the user explicitly asks for a
repository split or migration.

| Repository | Owns source code for | Owns output artifacts | Must not own |
| --- | --- | --- | --- |
| `ocp-developers-s3_storage-code` | Go runtime services, shared runtime libraries, S3 API behavior, runtime contracts, runtime tests, runtime documentation source. | Runtime service images, runtime docs image, digest-pinned runtime release manifest. | Operator manager code, OLM bundle/catalog publication, Helm chart, native installers, public docs site publication. |
| `ocp-developers-s3_storage_li9_operators` | Go operator source, CRDs, controllers, RBAC, samples, OpenShift Console plugin integration, operator documentation source. | Operator manager image, operator docs image, generated bundle artifact for validation, source-side certification/readiness checks. | Customer-facing OLM bundle image, catalog image, multi-operator catalog inventory, runtime service code. |
| `ocp-developers-dockerfile-bundle-li9_operators` | Multi-operator bundle/catalog inventory, per-operator version metadata, catalog rendering scripts, OLM install verification scripts. | Customer-facing OLM bundle images, shared multi-operator catalog images, OperatorHub/Software Catalog verification results. | Runtime service code, operator controller implementation, Helm chart implementation. |
| `ocp-developers-s3_storage_li9_helmchart` | Helm chart templates, values, Helm installation docs/tests. | Helm chart package and OCI chart artifact. | Operator CRDs/controllers, OLM bundle/catalog, runtime service code. |
| `ocp-developers-s3_storage_li9_helmrepo` | Public GitHub Pages Helm repository index and packaged chart copies. | Public `index.yaml`, chart `.tgz` files, GitHub Pages content. | Source chart templates or product logic. |
| `ocp-developers-s3_storage_li9_docsrepo` | Public documentation site aggregation and publication tooling. | Static GitHub Pages documentation site. | Product behavior, operator logic, runtime logic, generated HTML hand edits from component docs. |
| `ocp-developers-s3_storage_linux_installer` | Linux RPM/DEB packaging, Linux native service configuration, Linux VM E2E. | RPM/DEB packages, Linux installer release artifacts, Linux E2E evidence. | Runtime source implementation, operator/bundle/catalog code. |
| `ocp-developers-s3_storage_windows_installer` | Windows MSI/ZIP packaging, Windows service configuration, Windows VM E2E. | MSI/ZIP packages, Windows installer release artifacts, Windows E2E evidence. | Runtime source implementation, operator/bundle/catalog code. |

Shared registry namespace:

- `quay.io/li9/li9-operators` is the shared image/artifact namespace.
- Runtime images are published by `ocp-developers-s3_storage-code`.
- Operator manager/docs images are published by
  `ocp-developers-s3_storage_li9_operators`.
- Bundle/catalog images are published by
  `ocp-developers-dockerfile-bundle-li9_operators`.

Pipeline boundary rules:

- Runtime repo CI may build runtime images and release manifests only.
- Operator source CI may validate generated bundles, but final bundle/catalog
  publication belongs to the bundle repo.
- Bundle repo CI is the only place that publishes customer-facing OLM bundle and
  catalog images.
- Helm install and operator install are separate product delivery paths. Do not
  mix Helm resources into OLM bundle logic or operator-owned resources into the
  Helm chart unless the product contract explicitly requires it.
- Documentation changes must be made in the component source repository first;
  the public docs repo aggregates and publishes, it is not the source of truth
  for product behavior.

When a feature spans repositories, update each owning repository separately:

1. Runtime behavior in the runtime repo.
2. CRD/controller behavior in the operator repo.
3. OLM version/catalog metadata in the bundle repo.
4. Helm/native installer packaging in the relevant installer repo.
5. Public documentation through the source docs and docs publication pipeline.

This repository publishes the public Li9 S3 Storage documentation site.

- Treat component repositories as the source of truth. Do not hand-edit copied
  generated HTML in this repository.
- Keep publication logic in `.github/workflows/publish.yml`,
  `scripts/build_site.py`, and `scripts/publish_site.py`.
- The GitHub Pages workflow runs on the OpenShift ARC `mgm01-prd-ovh-gitops-runner`, the
  same runner family used by the component repositories.
- The publication flow must not require public read access to private source
  repositories; use `DOCS_SOURCE_TOKEN`.
- Keep GitHub Pages output static and self-contained under `_site`.
- Never commit credentials, registry tokens, cluster URLs from test
  environments, or screenshots containing environment-specific hostnames.
