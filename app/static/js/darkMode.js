(function () {
  const STORAGE_KEY = "darkMode";

  // Migrate preferences saved by the older role-specific implementations.
  const migrateStoredTheme = () => {
    const current = localStorage.getItem(STORAGE_KEY);
    if (current === "enabled" || current === "disabled") return;

    const legacy =
      localStorage.getItem("darkTheme") === "on" ||
      localStorage.getItem("darkMode") === "enabled" ||
      localStorage.getItem("expert-theme") === "dark" ||
      localStorage.getItem("dark") === "on";

    if (legacy) localStorage.setItem(STORAGE_KEY, "enabled");
    else if (localStorage.getItem("darkTheme") !== null ||
             localStorage.getItem("darkMode") !== null ||
             localStorage.getItem("expert-theme") !== null ||
             localStorage.getItem("dark") !== null) {
      localStorage.setItem(STORAGE_KEY, "disabled");
    }
  };

  migrateStoredTheme();

  const applyTheme = (isDark) => {
    document.body.classList.toggle("dark-mode", isDark);
    document.body.classList.toggle("theme-dark", isDark);
    document.body.classList.toggle("theme-light", !isDark);
    document.documentElement.setAttribute("data-bs-theme", isDark ? "dark" : "light");

    document
      .querySelectorAll("#darkModeToggle, #themeToggle")
      .forEach((toggle) => {
        if (toggle.matches('input[type="checkbox"]')) {
          toggle.checked = isDark;
        } else {
          toggle.setAttribute("aria-pressed", isDark ? "true" : "false");
        }

        const icon = toggle.querySelector("i");
        if (icon) icon.className = isDark ? "bi bi-sun-fill text-warning" : "bi bi-moon-stars";
      });
  };

  const savedTheme = localStorage.getItem(STORAGE_KEY);
  const useDarkTheme =
    savedTheme === "enabled" ||
    (savedTheme === null && window.matchMedia("(prefers-color-scheme: dark)").matches);

  applyTheme(useDarkTheme);

  document.addEventListener("DOMContentLoaded", () => {
    const syncThemeControls = () => {
      applyTheme(document.body.classList.contains("dark-mode"));
    };

    syncThemeControls();
    document.querySelectorAll("#darkModeToggle, #themeToggle").forEach((toggle) => {
      const eventName = toggle.matches('input[type="checkbox"]') ? "change" : "click";

      toggle.addEventListener(eventName, () => {
        const nextState = toggle.matches('input[type="checkbox"]')
          ? toggle.checked
          : !document.body.classList.contains("dark-mode");
        applyTheme(nextState);
        localStorage.setItem(STORAGE_KEY, nextState ? "enabled" : "disabled");
      });
    });
  });
})();