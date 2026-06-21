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

    // Skip on mobile: single column, natural flow
    if (window.innerWidth <= 768) {
      grid.classList.add("is-ready");
      return;
    }

    // Skip if already laid out
    if (grid.querySelector(".photo-col")) return;

    var numCols = 2;
    var cols = [];
    for (var c = 0; c < numCols; c++) {
      var col = document.createElement("div");
      col.className = "photo-col";
      cols.push(col);
      grid.appendChild(col);
    }

    // Assign each photo to the shortest column (by scrollHeight, not offsetHeight)
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

  // Wait for images to load before layout (so heights are correct)
  var images = document.querySelectorAll(".photo-item img");
  var loaded = 0;
  var total = images.length;

  function onReady() {
    grids.forEach(layoutMasonry);
    grids.forEach(function(g) { g.classList.add("is-ready"); });
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

  // Fallback: show after 3s even if some images fail to load
  setTimeout(onReady, 3000);
})();
