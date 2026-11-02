// Hardware page: board controls for the full-screen Doc 9 viewer, and the
// Runbooks link. The viewer listens for keys on its canvas: "f" flips the
// board, "0" fits it to the frame.
(function () {
  "use strict";
  var reduced = false;
  try { reduced = matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  var root = document.getElementById("el-pcb");
  var key = function (k) {
    var c = root && root.querySelector(".el-pcb-canvas");
    if (c) c.dispatchEvent(new KeyboardEvent("keydown", { key: k, bubbles: true, cancelable: true }));
  };

  var face = "F";
  var flip = document.querySelector('[data-board="flip"]');
  flip.addEventListener("click", function () {
    key("f");
    face = face === "F" ? "B" : "F";
    flip.textContent = face === "F" ? "Show back" : "Show front";
  });
  document.querySelector('[data-board="fit"]').addEventListener("click", function () { key("0"); });

  // Re-fit once the viewer reports ready, and whenever the window changes size.
  if (root) {
    var refitWhenReady = function () {
      if (root.dataset.state === "ready") { requestAnimationFrame(function () { key("0"); }); return true; }
      return false;
    };
    if (!refitWhenReady()) {
      var mo = new MutationObserver(function () { if (refitWhenReady()) mo.disconnect(); });
      mo.observe(root, { attributes: true, attributeFilter: ["data-state"] });
    }
  }
  var rt = 0;
  window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { key("0"); }, 150); });

  var link = document.querySelector('[data-scroll-to="runbooks"]');
  link.addEventListener("click", function (e) {
    var target = document.getElementById("runbooks");
    if (!target) return;
    e.preventDefault();
    window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY, behavior: reduced ? "auto" : "smooth" });
    history.replaceState(null, "", "#runbooks");
  });
})();
