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

// Pinterest-style masonry layout
(function() {
  function layoutMasonry(grid) {
    var items = Array.from(grid.querySelectorAll(".photo-item"));
    if (!items.length) return;

    // Check if already laid out
    if (grid.querySelector(".photo-col")) return;

    var isMobile = window.innerWidth <= 768;
    var numCols = isMobile ? 1 : 2;
    var cols = [];
    for (var c = 0; c < numCols; c++) {
      var col = document.createElement("div");
      col.className = "photo-col";
      cols.push(col);
    }

    items.forEach(function(item) {
      if (numCols === 1) {
        cols[0].appendChild(item);
        return;
      }
      var shortest = 0;
      for (var c = 1; c < cols.length; c++) {
        if (cols[c].offsetHeight < cols[shortest].offsetHeight) {
          shortest = c;
        }
      }
      cols[shortest].appendChild(item);
    });

    grid.innerHTML = "";
    cols.forEach(function(col) { grid.appendChild(col); });
  }

  var grids = document.querySelectorAll(".photo-grid");
  if (!grids.length) return;

  // Wait for images to load before layout
  var images = document.querySelectorAll(".photo-item img");
  var loaded = 0;
  var total = images.length;

  if (total === 0) {
    grids.forEach(layoutMasonry);
    return;
  }

  function onReady() {
    grids.forEach(layoutMasonry);
    grids.forEach(function(g) { g.classList.add("is-ready"); });
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

  // Fallback: layout after 3s even if some images fail
  setTimeout(onReady, 3000);
})();
