// Theme toggle
(function() {
  const toggle = document.getElementById("themeToggle");
  if (!toggle) return;
  
  // Check saved preference or system preference
  const saved = localStorage.getItem("album-theme");
  if (saved) {
    document.documentElement.dataset.scheme = saved;
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.dataset.scheme = "dark";
  }
  
  toggle.addEventListener("click", function() {
    const current = document.documentElement.dataset.scheme;
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.dataset.scheme = next;
    localStorage.setItem("album-theme", next);
  });
  
  // Listen for system preference changes
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
    if (!localStorage.getItem("album-theme")) {
      document.documentElement.dataset.scheme = e.matches ? "dark" : "light";
    }
  });
})();
