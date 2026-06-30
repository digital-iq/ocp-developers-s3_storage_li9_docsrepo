(function () {
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
  const pages = [
    { path: "/index.html", title: "Home", section: "Overview" },
    { path: "/install.html", title: "Installation Overview", section: "Installation" },
    ...installPages,
    { path: "/administration.html", title: "Administration", section: "Administration" },
    { path: "/operations.html", title: "Operations", section: "Operations" },
    { path: "/upgrade.html", title: "Upgrade", section: "Upgrade" },
    { path: "/reference.html", title: "Reference", section: "Reference" },
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
    if (path === "/runtime/" || path.endsWith("/runtime/")) return "/runtime/index.html";
    if (!path.startsWith("/runtime/") && ["index.html", "usage.html", "services.html", "architecture.html"].some((name) => path.endsWith("/" + name))) {
      const name = path.split("/").pop();
      return "/runtime/" + name;
    }
    return path;
  }

  function normalizeInstallationNav() {
    const sidebar = document.querySelector(".docs-sidebar");
    if (!sidebar) return;
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
    installTypes.forEach((type) => {
      const group = document.createElement("div");
      group.className = "install-group";
      const typePath = `/install-${type.slug}.html`;
      const isCurrentGroup = path === typePath || path.startsWith(`/install-${type.slug}-`);
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

  function markActiveLink() {
    const sidebar = document.querySelector(".docs-sidebar");
    if (!sidebar) return;
    const path = currentPath();
    sidebar.querySelectorAll("a").forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (!href || href.startsWith("#")) return;
      const normalized = href.startsWith("/") ? href.split("#")[0] : "/runtime/" + href.split("#")[0];
      if (normalized === path || (path === "/runtime/index.html" && normalized === "/runtime/")) {
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

  document.addEventListener("DOMContentLoaded", () => {
    normalizeInstallationNav();
    markActiveLink();
    insertBreadcrumbs();
    insertPageNav();
    enhanceCodeBlocks();
  });
})();
