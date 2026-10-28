// Theme toggle
(function() {
  const toggle = document.getElementById("themeToggle");
  if (!toggle) return;
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
  if (img.complete) { reveal(); }
  else {
    img.addEventListener('load', reveal);
    img.addEventListener('error', reveal);
  }
});

// Pinterest-style masonry layout
(function() {
  function getNumCols() {
    var w = window.innerWidth;
    if (w <= 768) return 1;
    if (w <= 1024) return 3;
    return 4;
  }

  function layoutMasonry(grid) {
    var items = Array.from(grid.querySelectorAll(".photo-item"));
    if (!items.length) return;
    grid.querySelectorAll(".photo-col").forEach(function(c) { c.remove(); });
    var numCols = getNumCols();
    var gapSize = 12;
    var colW = (grid.clientWidth - gapSize * (numCols - 1)) / numCols;

    // Measure heights off-flow at exact column width. Items must stay in the
    // DOM while measured (detached elements report offsetHeight 0, which
    // would collapse everything into col 0), and must NOT sit inside the
    // pre-ready grid (height 0 + flex would shrink them to 0 as well).
    var measurer = document.createElement("div");
    measurer.style.cssText = "position:absolute;visibility:hidden;top:0;left:0;width:" + colW + "px;";
    grid.appendChild(measurer);
    var heights = items.map(function(item) {
      measurer.appendChild(item);
      return item.offsetHeight;
    });
    measurer.remove();

    var cols = [];
    var colHeights = [];
    for (var c = 0; c < numCols; c++) {
      var col = document.createElement("div");
      col.className = "photo-col";
      cols.push(col);
      colHeights.push(0);
      grid.appendChild(col);
    }
    items.forEach(function(item, i) {
      var shortest = 0;
      var minH = colHeights[0];
      for (var c = 1; c < numCols; c++) {
        if (colHeights[c] < minH) { minH = colHeights[c]; shortest = c; }
      }
      cols[shortest].appendChild(item);
      colHeights[shortest] += heights[i] + (colHeights[shortest] > 0 ? gapSize : 0);
    });
  }

  var grids = document.querySelectorAll(".photo-grid");
  if (!grids.length) return;
  var isMobile = window.innerWidth <= 768;
  if (isMobile) {
    grids.forEach(function(g) { g.classList.add("is-ready"); });
    return;
  }

  grids.forEach(function(grid) {
    var spinner = document.createElement("div");
    spinner.className = "photo-grid-loader";
    spinner.innerHTML = '<svg viewBox="0 0 24 24" width="32" height="32"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4 31.4" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite"/></circle></svg>';
    grid.parentNode.insertBefore(spinner, grid);
  });

  var images = document.querySelectorAll(".photo-item img");
  var loaded = 0;
  var total = images.length;
  var onReadyCalled = false;
  function onReady() {
    if (onReadyCalled) return;
    onReadyCalled = true;
    grids.forEach(layoutMasonry);
    grids.forEach(function(g) { g.classList.add("is-ready"); });
    document.querySelectorAll(".photo-grid-loader").forEach(function(s) { s.remove(); });
  }
  if (total === 0) { onReady(); return; }
  images.forEach(function(img) {
    if (img.complete) { loaded++; if (loaded === total) onReady(); }
    else {
      img.addEventListener("load", function() { loaded++; if (loaded === total) onReady(); });
      img.addEventListener("error", function() { loaded++; if (loaded === total) onReady(); });
    }
  });
  setTimeout(onReady, 3000);

  var resizeTimer;
  window.addEventListener("resize", function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      if (window.innerWidth <= 768) return;
      grids.forEach(function(g) {
        if (g.classList.contains("is-ready")) layoutMasonry(g);
      });
    }, 200);
  });
})();

// Lightbox
(function() {
  var lb = document.createElement("div");
  lb.className = "lightbox";
  lb.innerHTML = '<button class="lightbox-close">\u00d7</button>' +
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
  var collected = false;

  function collectItems() {
    if (collected) return;
    collected = true;
    allItems = [];
    document.querySelectorAll(".photo-item").forEach(function(fig, i) {
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
