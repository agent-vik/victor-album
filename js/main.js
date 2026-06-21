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

// Image load shimmer fade-in
document.querySelectorAll('.img-wrap img').forEach(function(img) {
  var wrap = img.parentElement;
  function reveal() {
    img.classList.add('is-loaded');
    wrap.classList.add('is-loaded');
  }
  if (img.complete) {
    reveal();
  } else {
    img.addEventListener('load', reveal);
    img.addEventListener('error', reveal);
  }
});

// Pinterest-style masonry layout (PC only, mobile uses single column)
(function() {
  function layoutMasonry(grid) {
    var items = Array.from(grid.querySelectorAll(".photo-item"));
    if (!items.length) return;

    if (grid.querySelector(".photo-col")) return;

    var numCols = 4;
    var cols = [];
    for (var c = 0; c < numCols; c++) {
      var col = document.createElement("div");
      col.className = "photo-col";
      cols.push(col);
      grid.appendChild(col);
    }

    // Temporarily make grid block-flow so items have natural height
    grid.style.display = "block";
    var colHeights = [];
    for (var c = 0; c < numCols; c++) { colHeights.push(0); }
    var gapSize = 12;

    items.forEach(function(item) {
      var h = item.offsetHeight;
      var shortest = 0;
      var minH = colHeights[0];
      for (var c = 1; c < numCols; c++) {
        if (colHeights[c] < minH) {
          minH = colHeights[c];
          shortest = c;
        }
      }
      cols[shortest].appendChild(item);
      colHeights[shortest] += h + (colHeights[shortest] > 0 ? gapSize : 0);
    });

    grid.style.display = "";
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

// Lightbox
(function() {
  var lb = document.createElement("div");
  lb.className = "lightbox";
  lb.innerHTML = '<button class="lightbox-close">×</button>' +
    '<button class="lightbox-nav lightbox-prev"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg></button>' +
    '<button class="lightbox-nav lightbox-next"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg></button>' +
    '<img src="" alt="" />' +
    '<div class="lightbox-caption"></div>';
  document.body.appendChild(lb);

  var lbImg = lb.querySelector("img");
  var lbCaption = lb.querySelector(".lightbox-caption");
  var lbClose = lb.querySelector(".lightbox-close");
  var lbPrev = lb.querySelector(".lightbox-prev");
  var lbNext = lb.querySelector(".lightbox-next");

  var allItems = [];
  var currentIndex = 0;

  function collectItems() {
    allItems = [];
    var items = document.querySelectorAll(".photo-item");
    items.forEach(function(fig, i) {
      var img = fig.querySelector("img");
      var cap = fig.querySelector("figcaption");
      if (img) {
        allItems.push({ src: img.src, alt: img.alt, caption: cap ? cap.textContent : "" });
        fig.addEventListener("click", function() { open(i); });
      }
    });
  }

  function open(index) {
    currentIndex = index;
    show(currentIndex);
    lb.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function show(index) {
    var item = allItems[index];
    if (!item) return;
    lbImg.src = item.src;
    lbImg.alt = item.alt;
    lbCaption.textContent = item.caption;
    lbPrev.style.display = allItems.length > 1 ? "" : "none";
    lbNext.style.display = allItems.length > 1 ? "" : "none";
  }

  function close() {
    lb.classList.remove("is-open");
    lbImg.src = "";
    document.body.style.overflow = "";
  }

  function prev() {
    currentIndex = (currentIndex - 1 + allItems.length) % allItems.length;
    show(currentIndex);
  }

  function next() {
    currentIndex = (currentIndex + 1) % allItems.length;
    show(currentIndex);
  }

  lbClose.addEventListener("click", function(e) { e.stopPropagation(); close(); });
  lbPrev.addEventListener("click", function(e) { e.stopPropagation(); prev(); });
  lbNext.addEventListener("click", function(e) { e.stopPropagation(); next(); });
  lb.addEventListener("click", function(e) { if (e.target === lb || e.target === lbImg) close(); });

  document.addEventListener("keydown", function(e) {
    if (!lb.classList.contains("is-open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") prev();
    if (e.key === "ArrowRight") next();
  });

  var touchStartX = 0;
  lb.addEventListener("touchstart", function(e) { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
  lb.addEventListener("touchend", function(e) {
    var dx = e.changedTouches[0].screenX - touchStartX;
    if (dx > 50) prev();
    else if (dx < -50) next();
  }, { passive: true });

  var observer = new MutationObserver(function() {
    if (document.querySelector(".photo-col")) {
      observer.disconnect();
      collectItems();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
  setTimeout(collectItems, 3500);
})();
