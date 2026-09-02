document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("darkModeToggle");
  const toggleIcon = toggleBtn ? toggleBtn.querySelector("i") : null;
  const storedTheme = localStorage.getItem("darkTheme");

  // Function to apply or remove dark mode
  const applyTheme = (isDark) => {
    document.body.classList.toggle("dark-mode", isDark);
    document.documentElement.setAttribute("data-bs-theme", isDark ? "dark" : "light");

    if (toggleIcon) {
      if (isDark) {
        toggleIcon.className = "bi bi-sun-fill text-warning";
      } else {
        toggleIcon.className = "bi bi-moon-stars";
      }
    }
  };

  // 1. Initialize theme state on load
  if (storedTheme === "on") {
    applyTheme(true);
  } else if (storedTheme === null && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    // Default to OS setting if user has no saved preference
    applyTheme(true);
  }

  // 2. Toggle button click event
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const isCurrentlyDark = document.body.classList.contains("dark-mode");
      const nextState = !isCurrentlyDark;

      applyTheme(nextState);
      localStorage.setItem("darkTheme", nextState ? "on" : "off");
    });
  }
});