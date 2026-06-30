(function () {
  const platformConfigs = {
    openshift: {
      slug: "openshift",
      title: "OpenShift Operator",
      installPath: "/install-openshift.html",
      referencePath: "/reference-openshift-operator.html",
      description: "This documentation view is scoped to OLM and operator-managed OpenShift installations."
    },
    helm: {
      slug: "helm",
      title: "Helm / Kubernetes",
      installPath: "/install-helm.html",
      referencePath: "/reference-helm-kubernetes.html",
      description: "This documentation view is scoped to Helm-managed Kubernetes installations."
    },
    linux: {
      slug: "linux",
      title: "Linux Packages",
      installPath: "/install-linux.html",
      referencePath: "/reference-linux-host.html",
      description: "This documentation view is scoped to RPM/DEB installations managed by systemd."
    },
    windows: {
      slug: "windows",
      title: "Windows Packages",
      installPath: "/install-windows.html",
      referencePath: "/reference-windows-host.html",
      description: "This documentation view is scoped to MSI/ZIP installations managed by Windows services."
    }
  };
  const installTypes = [
    { slug: "openshift", title: "OpenShift Operator" },
    { slug: "helm", title: "Helm Chart" },
    { slug: "linux", title: "Linux Packages" },
    { slug: "windows", title: "Windows Packages" },
    { slug: "airgap", title: "Private Registry And Airgap" }
  ];
  const installPhases = [
    { slug: "prerequisites", title: "Prerequisites" },
    { slug: "installation", title: "Installation" },
    { slug: "upgrade", title: "Upgrade" },
    { slug: "uninstall", title: "Uninstall" }
  ];
  const installPages = installTypes.flatMap((type) => [
    { path: `/install-${type.slug}.html`, title: type.title, section: "Installation" },
    ...installPhases.map((phase) => ({
      path: `/install-${type.slug}-${phase.slug}.html`,
      title: phase.title,
      section: `Installation / ${type.title}`
    }))
  ]);
  const s3ReferenceLinks = [
    { path: "/reference-s3-api.html", title: "S3 API reference" },
    { path: "/reference-s3-core-bucket-object-api.html", title: "Core bucket/object API" },
    { path: "/reference-s3-multipart-upload.html", title: "Multipart upload" },
    { path: "/reference-s3-versioning-delete-markers.html", title: "Versioning" },
    { path: "/reference-s3-policies-authorization.html", title: "Policies" },
    { path: "/reference-s3-object-metadata-tagging.html", title: "Metadata and tagging" },
    { path: "/reference-s3-checksums-payload-integrity.html", title: "Checksums" },
    { path: "/reference-s3-encryption-kms-compatible-wrapping.html", title: "Encryption" },
    { path: "/reference-s3-object-lock-retention.html", title: "Object Lock" },
    { path: "/reference-s3-lifecycle-multi-tier-archive-restore.html", title: "Lifecycle policy and restore" },
    { path: "/reference-s3-replication.html", title: "Replication" },
    { path: "/reference-s3-bucket-subresources.html", title: "Bucket subresources" },
    { path: "/reference-s3-inventory-metadata-tables.html", title: "Inventory and tables" },
    { path: "/reference-s3-select.html", title: "S3 Select" },
    { path: "/reference-s3-range-conditional-reads.html", title: "Range and conditional reads" },
    { path: "/reference-s3-storage-classes.html", title: "S3 storage class and PVC placement" }
  ];
  const runtimeReferenceLinks = [
    { path: "/reference-platform-storage-topology.html", title: "Storage topology" },
    { path: "/reference-platform-data-protection-engines.html", title: "Data protection" },
    { path: "/reference-platform-metadata-durability.html", title: "Metadata durability" },
    { path: "/reference-platform-identity-credentials.html", title: "Identity and credentials" },
    { path: "/reference-platform-internal-security.html", title: "Internal security" },
    { path: "/reference-platform-observability.html", title: "Observability" },
    { path: "/reference-platform-audit-durable-delivery.html", title: "Audit delivery" },
    { path: "/reference-platform-healing-maintenance.html", title: "Healing" },
    { path: "/reference-platform-high-availability-behavior.html", title: "High availability" }
  ];
  const platformReferenceLinks = {
    openshift: [
      { path: "/reference-openshift-operator.html", title: "OpenShift Operator" },
      { path: "/reference-platform-openshift-consumption-apis.html", title: "OpenShift consumption APIs" },
      { path: "/reference-platform-openshift-bucket-browser.html", title: "OpenShift bucket browser" },
      { path: "/reference-platform-node-placement.html", title: "Node placement" },
      { path: "/reference-platform-pvc-capacity-operations.html", title: "PVC capacity" },
      { path: "/reference-platform-documentation-delivery.html", title: "Documentation delivery" },
      { path: "/cr-examples.html", title: "CR examples" }
    ],
    helm: [
      { path: "/reference-helm-kubernetes.html", title: "Helm / Kubernetes" },
      { path: "/reference-platform-node-placement.html", title: "Kubernetes placement" },
      { path: "/reference-platform-pvc-capacity-operations.html", title: "PVC capacity" }
    ],
    linux: [
      { path: "/reference-linux-host.html", title: "Linux host packages" }
    ],
    windows: [
      { path: "/reference-windows-host.html", title: "Windows host packages" }
    ]
  };
  const releaseReferenceLinks = [
    { path: "/reference-platform-installation-modes.html", title: "Installation modes" },
    { path: "/reference-platform-packaging-release-automation.html", title: "Packaging and release automation" }
  ];
  const pages = [
    { path: "/index.html", title: "Home", section: "Overview" },
    { path: "/install.html", title: "Installation Overview", section: "Installation" },
    ...installPages,
    { path: "/administration.html", title: "Administration", section: "Administration" },
    { path: "/operations.html", title: "Operations", section: "Operations" },
    { path: "/upgrade.html", title: "Upgrade", section: "Upgrade" },
    { path: "/reference.html", title: "Reference", section: "Reference" },
    ...s3ReferenceLinks.map((item) => ({ ...item, section: "Reference / S3 API" })),
    ...runtimeReferenceLinks.map((item) => ({ ...item, section: "Reference / Runtime" })),
    { path: "/reference-platform.html", title: "Platform reference", section: "Reference" },
    ...Object.values(platformReferenceLinks).flat().map((item) => ({ ...item, section: "Reference / Platform" })),
    ...releaseReferenceLinks.map((item) => ({ ...item, section: "Reference / Release" })),
    { path: "/cr-examples.html", title: "CR Examples", section: "Reference" },
    { path: "/troubleshooting.html", title: "Troubleshooting", section: "Operations" },
    { path: "/runtime/index.html", title: "Runtime Overview", section: "Runtime" },
    { path: "/runtime/usage.html", title: "Runtime Usage", section: "Runtime" },
    { path: "/runtime/services.html", title: "Runtime Services", section: "Runtime" },
    { path: "/runtime/architecture.html", title: "Runtime Architecture", section: "Runtime" }
  ];

  function currentPath() {
    const path = window.location.pathname;
    if (path === "/") return "/index.html";
    if (path === "/runtime/") return "/runtime/index.html";
    return path;
  }

  function configuredPlatform() {
    const fromWindow = window.LI9_DOCS_PLATFORM;
    const fromMeta = document.querySelector('meta[name="li9-docs-platform"]')?.getAttribute("content");
    const slug = (fromWindow || fromMeta || "").trim().toLowerCase();
    return platformConfigs[slug] || null;
  }

  function createSidebarLink(item, className) {
    const link = document.createElement("a");
    link.href = item.path;
    link.textContent = item.title;
    if (className) link.className = className;
    return link;
  }

  function appendSidebarLabel(section, text) {
    const label = document.createElement("div");
    label.className = "sidebar-label";
    label.textContent = text;
    section.appendChild(label);
  }

  function normalizeInstallationNav() {
    const sidebar = document.querySelector(".docs-sidebar");
    if (!sidebar) return;
    const platform = configuredPlatform();
    const section = Array.from(sidebar.querySelectorAll(".sidebar-section")).find((item) => {
      return (item.querySelector("h3")?.textContent || "").trim().toLowerCase() === "installation";
    });
    if (!section) return;
    const heading = section.querySelector("h3");
    section.innerHTML = "";
    section.appendChild(heading);
    const overview = document.createElement("a");
    overview.href = "/install.html";
    overview.textContent = "Overview";
    section.appendChild(overview);
    const path = currentPath();
    const visibleTypes = platform
      ? installTypes.filter((type) => type.slug === platform.slug || type.slug === "airgap")
      : installTypes;
    visibleTypes.forEach((type) => {
      const group = document.createElement("div");
      group.className = "install-group";
      const typePath = `/install-${type.slug}.html`;
      const isCurrentGroup = path === typePath || path.startsWith(`/install-${type.slug}-`) || platform?.slug === type.slug;
      if (isCurrentGroup) group.classList.add("open");
      const linksId = `install-group-${type.slug}`;
      const title = document.createElement("button");
      title.className = "install-group-toggle";
      if (isCurrentGroup) title.classList.add("active");
      title.type = "button";
      title.textContent = type.title;
      title.setAttribute("aria-expanded", isCurrentGroup ? "true" : "false");
      title.setAttribute("aria-controls", linksId);
      title.addEventListener("click", () => {
        const isOpen = group.classList.toggle("open");
        title.setAttribute("aria-expanded", String(isOpen));
      });
      group.appendChild(title);
      const links = document.createElement("div");
      links.className = "install-group-links";
      links.id = linksId;
      installPhases.forEach((phase) => {
        const link = document.createElement("a");
        link.className = "sub";
        link.href = `/install-${type.slug}-${phase.slug}.html`;
        link.textContent = phase.title;
        links.appendChild(link);
      });
      group.appendChild(links);
      section.appendChild(group);
    });
  }

  function normalizeReferenceNav() {
    const sidebar = document.querySelector(".docs-sidebar");
    if (!sidebar) return;
    const platform = configuredPlatform();
    const section = Array.from(sidebar.querySelectorAll(".sidebar-section")).find((item) => {
      return (item.querySelector("h3")?.textContent || "").trim().toLowerCase() === "reference";
    });
    if (!section) return;
    const heading = section.querySelector("h3");
    section.innerHTML = "";
    section.appendChild(heading);

    section.appendChild(createSidebarLink({ path: "/reference.html", title: "Reference index" }));
    appendSidebarLabel(section, "S3 API");
    s3ReferenceLinks.forEach((item, index) => section.appendChild(createSidebarLink(item, index === 0 ? "" : "sub")));
    appendSidebarLabel(section, "Runtime");
    runtimeReferenceLinks.forEach((item) => section.appendChild(createSidebarLink(item, "sub")));
    appendSidebarLabel(section, "Platform");
    if (platform) {
      section.appendChild(createSidebarLink({ path: platform.referencePath, title: `${platform.title} reference` }));
    } else {
      section.appendChild(createSidebarLink({ path: "/reference-platform.html", title: "Platform reference" }));
    }
    const platformLinks = platform
      ? (platformReferenceLinks[platform.slug] || []).filter((item) => item.path !== platform.referencePath)
      : Object.values(platformReferenceLinks).flat();
    platformLinks.forEach((item) => section.appendChild(createSidebarLink(item, "sub")));
    appendSidebarLabel(section, "Release");
    releaseReferenceLinks.forEach((item) => section.appendChild(createSidebarLink(item, "sub")));
    section.appendChild(createSidebarLink({ path: "/runtime/usage.html", title: "AWS CLI usage" }, "sub"));
    section.appendChild(createSidebarLink({ path: "/runtime/services.html", title: "Runtime services" }, "sub"));
    section.appendChild(createSidebarLink({ path: "/runtime/architecture.html", title: "Architecture" }, "sub"));
  }

  function insertPlatformBanner() {
    const platform = configuredPlatform();
    if (!platform) return;
    const content = document.querySelector(".docs-content") || document.querySelector("main");
    if (!content || content.querySelector(".platform-scope-banner")) return;
    const hero = content.querySelector(".hero-doc");
    const banner = document.createElement("section");
    banner.className = "platform-scope-banner";
    banner.innerHTML = `
      <div>
        <strong>${platform.title} documentation view</strong>
        <span>${platform.description}</span>
      </div>
      <div class="platform-scope-links">
        <a href="${platform.installPath}">Installation guide</a>
        <a href="${platform.referencePath}">Platform reference</a>
      </div>
    `;
    if (hero) {
      hero.insertAdjacentElement("afterend", banner);
    } else {
      content.prepend(banner);
    }
  }

  function markActiveLink() {
    const sidebar = document.querySelector(".docs-sidebar");
    if (!sidebar) return;
    const path = currentPath();
    sidebar.querySelectorAll("a").forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (!href || href.startsWith("#")) return;
      const normalized = href.startsWith("/") ? href.split("#")[0] : "/" + href.split("#")[0];
      if (normalized === path || (path === "/index.html" && normalized === "/")) {
        link.classList.add("active");
      }
    });
  }

  function insertBreadcrumbs() {
    const content = document.querySelector(".docs-content") || document.querySelector("main");
    if (!content || content.querySelector(".breadcrumbs")) return;
    const page = pages.find((item) => item.path === currentPath());
    if (!page) return;
    const crumbs = document.createElement("nav");
    crumbs.className = "breadcrumbs";
    crumbs.setAttribute("aria-label", "Breadcrumbs");
    crumbs.innerHTML = `<a href="/">Li9 S3 Storage</a><span>${page.section}</span><span>${page.title}</span>`;
    content.prepend(crumbs);
  }

  function insertPageNav() {
    const content = document.querySelector(".docs-content") || document.querySelector("main");
    if (!content || content.querySelector(".page-nav")) return;
    const index = pages.findIndex((item) => item.path === currentPath());
    if (index < 0) return;
    const previous = pages[index - 1];
    const next = pages[index + 1];
    if (!previous && !next) return;
    const nav = document.createElement("nav");
    nav.className = "page-nav";
    nav.setAttribute("aria-label", "Page navigation");
    nav.innerHTML = `
      ${previous ? `<a class="previous" href="${previous.path}"><span>Previous</span>${previous.title}</a>` : "<div></div>"}
      ${next ? `<a class="next" href="${next.path}"><span>Next</span>${next.title}</a>` : "<div></div>"}
    `;
    content.append(nav);
  }

  function normalizeInstallationProcedure() {
    const path = currentPath();
    if (!/^\/install-[a-z0-9-]+-installation\.html$/.test(path)) return;
    const content = document.querySelector(".docs-content");
    const procedure = content?.querySelector(".procedure");
    if (!content || !procedure || procedure.dataset.merged === "true") return;
    const items = Array.from(procedure.querySelectorAll(".procedure-item > div"));
    if (!items.length) return;

    const details = [];
    let cursor = procedure.nextElementSibling;
    while (cursor && cursor.tagName !== "H2" && !cursor.classList?.contains("page-nav")) {
      if (cursor.tagName === "H3" && /^\d+\.\s+/.test(cursor.textContent.trim())) {
        const heading = cursor;
        const nodes = [];
        cursor = cursor.nextElementSibling;
        while (cursor && !(cursor.tagName === "H3" && /^\d+\.\s+/.test(cursor.textContent.trim())) && cursor.tagName !== "H2" && !cursor.classList?.contains("page-nav")) {
          const next = cursor.nextElementSibling;
          nodes.push(cursor);
          cursor = next;
        }
        details.push({ heading, nodes });
        continue;
      }
      cursor = cursor.nextElementSibling;
    }

    details.slice(0, items.length).forEach((detail, index) => {
      const target = items[index];
      const actionHeading = document.createElement("h4");
      actionHeading.className = "procedure-action-title";
      actionHeading.textContent = detail.heading.textContent.replace(/^\d+\.\s+/, "");
      target.appendChild(actionHeading);
      detail.nodes.forEach((node) => target.appendChild(node));
      detail.heading.remove();
    });
    procedure.dataset.merged = "true";
  }

  function enhanceCodeBlocks() {
    document.querySelectorAll("pre").forEach((pre) => {
      if (pre.parentElement && pre.parentElement.classList.contains("code-block")) return;
      const wrapper = document.createElement("div");
      wrapper.className = "code-block";
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);
      const button = document.createElement("button");
      button.className = "copy-code";
      button.type = "button";
      button.textContent = "Copy";
      button.addEventListener("click", async () => {
        const text = pre.textContent;
        try {
          await navigator.clipboard.writeText(text);
          button.textContent = "Copied";
          setTimeout(() => { button.textContent = "Copy"; }, 1200);
        } catch (_) {
          button.textContent = "Select";
          setTimeout(() => { button.textContent = "Copy"; }, 1200);
        }
      });
      wrapper.appendChild(button);
    });
  }

  function insertBuildInfo() {
    const target = document.querySelector("footer") || document.querySelector(".docs-sidebar");
    if (!target || target.querySelector(".docs-build")) return;
    const badge = document.createElement("span");
    badge.className = "docs-build";
    badge.textContent = "Version loading";
    target.appendChild(badge);

    fetch("/assets/build.json", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("build metadata unavailable")))
      .then((metadata) => {
        const operatorVersion = String(metadata.operatorVersion || metadata.version || "unknown").trim();
        const buildTag = String(metadata.buildTag || metadata.version || "unknown").trim();
        const revision = String(metadata.sourceRevision || "").trim();
        const revisionText = revision && revision !== "unknown" && revision !== "local" ? ` · ${revision}` : "";
        badge.textContent = `Operator ${operatorVersion} · Docs ${buildTag}${revisionText}`;
        badge.dataset.operatorVersion = operatorVersion;
        badge.dataset.buildTag = buildTag;
      })
      .catch(() => {
        badge.textContent = "Version unavailable";
      });
  }

  document.addEventListener("DOMContentLoaded", () => {
    normalizeInstallationNav();
    normalizeReferenceNav();
    insertPlatformBanner();
    markActiveLink();
    insertBreadcrumbs();
    normalizeInstallationProcedure();
    insertPageNav();
    enhanceCodeBlocks();
    insertBuildInfo();
  });
})();
