/* Click-to-enlarge for figures.
 *
 * Figures render at a modest reading width so they do not shove the prose
 * apart; the detail is one click away instead of always on screen. Written
 * against no library on purpose - the site's requirements are pinned and CI
 * installs exactly that list, so a plugin here would be a deploy risk for a
 * feature this small.
 */
(function () {
  "use strict";

  var FIGURES = ".md-typeset p > img";
  var overlay = null;
  var frame = null;
  var caption = null;
  var closeBtn = null;
  var lastFocus = null;

  function build() {
    overlay = document.createElement("div");
    overlay.className = "el-lightbox";
    overlay.hidden = true;
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Enlarged image");

    closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "el-lightbox__close";
    closeBtn.setAttribute("aria-label", "Close enlarged image");
    closeBtn.innerHTML = "&#215;";

    frame = document.createElement("img");
    frame.className = "el-lightbox__img";
    frame.alt = "";

    caption = document.createElement("p");
    caption.className = "el-lightbox__cap";

    overlay.appendChild(closeBtn);
    overlay.appendChild(frame);
    overlay.appendChild(caption);
    document.body.appendChild(overlay);

    // Clicking the backdrop closes; clicking the image itself does not.
    overlay.addEventListener("click", close);
    closeBtn.addEventListener("click", close);
    frame.addEventListener("click", function (e) { e.stopPropagation(); });

    document.addEventListener("keydown", function (e) {
      if (overlay.hidden) return;
      if (e.key === "Escape") { close(); return; }
      // A modal that can be tabbed out of is a modal in name only.
      if (e.key === "Tab") { e.preventDefault(); closeBtn.focus(); }
    });
  }

  function open(src, alt) {
    if (!overlay) build();
    lastFocus = document.activeElement;
    frame.src = src;
    frame.alt = alt || "";
    caption.textContent = alt || "";
    caption.hidden = !alt;
    overlay.hidden = false;
    document.body.classList.add("el-lightbox-open");
    closeBtn.focus();
  }

  function close() {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    frame.removeAttribute("src");
    document.body.classList.remove("el-lightbox-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function wire() {
    var imgs = document.querySelectorAll(FIGURES);
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      if (img.getAttribute("data-el-zoom")) continue;
      img.setAttribute("data-el-zoom", "1");
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      img.setAttribute("aria-label", (img.alt || "Figure") + " — select to enlarge");

      img.addEventListener("click", function () {
        open(this.currentSrc || this.src, this.alt);
      });
      img.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
          e.preventDefault();
          open(this.currentSrc || this.src, this.alt);
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
  // Material re-renders content on instant navigation; re-wire when it does.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(wire);
  }
})();
