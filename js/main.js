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

// Pinterest-style masonry layout (PC only, mobile uses single column)
(function() {
  function layoutMasonry(grid) {
    var items = Array.from(grid.querySelectorAll(".photo-item"));
    if (!items.length) return;

    if (grid.querySelector(".photo-col")) return;

    var numCols = 2;
    var cols = [];
    for (var c = 0; c < numCols; c++) {
      var col = document.createElement("div");
      col.className = "photo-col";
      cols.push(col);
      grid.appendChild(col);
    }

    items.forEach(function(item) {
      var shortest = 0;
      for (var c = 1; c < cols.length; c++) {
        if (cols[c].scrollHeight < cols[shortest].scrollHeight) {
          shortest = c;
        }
      }
      cols[shortest].appendChild(item);
    });
  }

  var grids = document.querySelectorAll(".photo-grid");
  if (!grids.length) return;

  var isMobile = window.innerWidth <= 768;

  // Mobile: show immediately, no masonry needed
  if (isMobile) {
    grids.forEach(function(g) { g.classList.add("is-ready"); });
    return;
  }

  // PC: show a loading spinner while images load
  grids.forEach(function(grid) {
    var spinner = document.createElement("div");
    spinner.className = "photo-grid-loader";
    spinner.innerHTML = '<svg viewBox="0 0 24 24" width="32" height="32"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4 31.4" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></circle></svg>';
    grid.parentNode.insertBefore(spinner, grid.nextSibling);
  });

  var images = document.querySelectorAll(".photo-item img");
  var loaded = 0;
  var total = images.length;

  function onReady() {
    grids.forEach(layoutMasonry);
    grids.forEach(function(g) { g.classList.add("is-ready"); });
    var spinners = document.querySelectorAll(".photo-grid-loader");
    spinners.forEach(function(s) { s.remove(); });
  }

  if (total === 0) {
    onReady();
    return;
  }

  images.forEach(function(img) {
    if (img.complete) {
      loaded++;
      if (loaded === total) onReady();
    } else {
      img.addEventListener("load", function() {
        loaded++;
        if (loaded === total) onReady();
      });
      img.addEventListener("error", function() {
        loaded++;
        if (loaded === total) onReady();
      });
    }
  });

  setTimeout(onReady, 3000);
})();
