document.addEventListener("DOMContentLoaded", () => {
  /* ================= DARK MODE ================= */
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("toggleBtn");
  const overlay = document.getElementById("overlay");
  const main = document.getElementById("mainContent");
  const topbar = document.getElementById("topbar");

  /* ================= DATE & TIME ================= */
  const days = [
    "អាទិត្យ",
    "ចន្ទ",
    "អង្គារ",
    "ពុធ",
    "ព្រហស្បតិ៍",
    "សុក្រ",
    "សៅរ៍",
  ];
  const months = [
    "មករា",
    "កុម្ភៈ",
    "មីនា",
    "មេសា",
    "ឧសភា",
    "មិថុនា",
    "កក្កដា",
    "សីហា",
    "កញ្ញា",
    "តុលា",
    "វិច្ឆិកា",
    "ធ្នូ",
  ];

  function updateTime() {
    const d = new Date();
    const dateEl = document.getElementById("khmer-date");
    const timeEl = document.getElementById("current-time");

    if (dateEl) {
      dateEl.innerText = `${days[d.getDay()]}, ${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
    }
    if (timeEl) {
      timeEl.innerText = d.toLocaleTimeString();
    }
  }

  updateTime();
  setInterval(updateTime, 1000);

//   /* ================= GREETING ================= */
//   const greetingEl = document.getElementById("greeting-text");
//   if (greetingEl) {
//     const hour = new Date().getHours();
//     const currentText = greetingEl.innerText.trim();

//     // Fallback if Jinja tags aren't rendered inline
//     if (!currentText || currentText.includes("{{")) {
//       greetingEl.innerText =
//         hour < 12
//           ? "🌅 {{ lang.dashboard.good_morning }}"
//           : hour < 17
//             ? "☀️ {{ lang.dashboard.good_afternoon }}"
//             : "🌙 {{ lang.dashboard.good_evening }}";
//     }
//   }

  /* ================= PAGE TRANSITION ================= */
  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    document.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", function (e) {
        const href = this.getAttribute("href");

        // Bypass transitions for external, hash, javascript anchors, or modal triggers
        if (
          this.target === "_blank" ||
          !href ||
          href.startsWith("#") ||
          href.startsWith("javascript:") ||
          this.hasAttribute("data-bs-toggle") ||
          this.hasAttribute("data-bs-dismiss")
        ) {
          return;
        }

        e.preventDefault();
        pageContent.classList.add("fade-out");
        setTimeout(() => (window.location.href = href), 200);
      });
    });
  }

  /* ================= SIDEBAR & OVERLAY TOGGLE ================= */
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      if (window.innerWidth < 992) {
        if (sidebar) sidebar.classList.toggle("show");
        if (overlay) overlay.classList.toggle("show");
      } else {
        if (sidebar) sidebar.classList.toggle("collapsed");
        if (main) main.classList.toggle("full");
        if (topbar) topbar.classList.toggle("full");
      }
    });
  }

  if (overlay) {
    overlay.addEventListener("click", () => {
      if (sidebar) sidebar.classList.remove("show");
      overlay.classList.remove("show");
    });
  }
});

/* ================= GLOBAL HELPER FUNCTIONS ================= */
function confirmLogout(event) {
  event.preventDefault();
  if (confirm("Are you sure you want to logout?")) {
    window.location.href = event.currentTarget.href;
  }
  return false;
}

function toggleRiceMenu(event) {
  event.preventDefault();

  const menu = document.getElementById("riceManagementMenu");
  const toggle = event.currentTarget;

  if (!menu) return;

  menu.classList.toggle("show");
  toggle.classList.toggle("open");

  const isOpen = menu.classList.contains("show");
  toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
}