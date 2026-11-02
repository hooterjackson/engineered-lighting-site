// Vision page: lazy concept films and the scroll-driven light/shadow sweep.
// Ported from the Vision prototype's page logic; the progress, mask and
// inversion maths are unchanged.
(function () {
  "use strict";
  var reduced = false;
  try { reduced = matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}

  // ---- Films: src within 600px of the viewport, autoplay muted at >= 35%
  // visible, pause offscreen; a manual pause sticks. Reduced motion shows the
  // poster until the reader presses play.
  function setupFilms() {
    var vids = Array.prototype.slice.call(document.querySelectorAll("video[data-film]"));
    var userPaused = new Set();
    var ensureSrc = function (v) {
      if (!v.getAttribute("src") && v.dataset.src) { v.src = v.dataset.src; v.preload = "auto"; }
    };
    var buttonFor = function (id) { return document.querySelector('button[data-film="' + id + '"]'); };
    vids.forEach(function (v) {
      v.muted = true; v.defaultMuted = true; v.playsInline = true;
      var id = v.dataset.film, btn = buttonFor(id);
      var sync = function () {
        if (!btn) return;
        btn.textContent = v.paused ? "Play film" : "Pause film";
        btn.setAttribute("aria-label", (v.paused ? "Play" : "Pause") + " the " + id + " concept render");
      };
      v.addEventListener("play", sync); v.addEventListener("pause", sync);
      // A film that is not published yet keeps its black frame and caption only.
      v.addEventListener("error", function () { var f = v.closest("figure"); if (f) f.setAttribute("data-missing", ""); });
      if (btn) btn.addEventListener("click", function () {
        ensureSrc(v);
        if (v.paused) { userPaused.delete(id); v.play().catch(function () {}); }
        else { userPaused.add(id); v.pause(); }
      });
    });
    if (!("IntersectionObserver" in window)) return;
    var near = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) ensureSrc(e.target); });
    }, { rootMargin: "600px 0px" });
    var vis = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target, id = v.dataset.film;
        if (e.isIntersecting) { if (!reduced && !userPaused.has(id)) { ensureSrc(v); v.play().catch(function () {}); } }
        else if (!v.paused) v.pause();
      });
    }, { threshold: 0.35 });
    vids.forEach(function (v) { near.observe(v); vis.observe(v); });
  }

  // ---- Light/shadow sweep. Each field is revealed over the previous one with
  // a diagonal mask driven by one shared progress per transition; text whose
  // centre sits on a lit field flips to dark instead of sitting on a panel.
  function setupLight() {
    var fields = Array.prototype.slice.call(document.querySelectorAll("[data-light-field]"));
    if (!fields.length) return;
    var LIT = ["ideal-experience", "flows"];
    var items = fields.map(function (f, i) {
      return { f: f, el: document.getElementById(f.dataset.trigger), angle: i % 2 ? 62 : 138, lit: LIT.indexOf(f.dataset.trigger) >= 0, p: 0, edge: -30 };
    });
    var content = document.querySelector(".v-content");
    var collect = function () {
      var out = [];
      content.querySelectorAll(":scope > header, :scope > div, :scope > nav, :scope > section, :scope > footer, figcaption, blockquote").forEach(function (block) {
        Array.prototype.forEach.call(block.children, function (c) {
          if (c.tagName === "UL" || c.tagName === "OL") Array.prototype.forEach.call(c.children, function (li) { out.push(li); });
          else out.push(c);
        });
      });
      // Never invert both an element and its ancestor; a double inversion cancels out.
      var set = new Set(out);
      var uniq = out.filter(function (el) {
        for (var p = el.parentElement; p; p = p.parentElement) if (set.has(p)) return false;
        return true;
      });
      uniq.forEach(function (el) { el.style.transition = "filter 480ms cubic-bezier(0.65,0,0.35,1)"; });
      return uniq;
    };
    var inks = collect();
    var litAt = function (x, y, W, H) {
      for (var k = items.length - 1; k >= 0; k--) {
        var it = items[k];
        if (it.p <= 0) continue;
        if (it.p >= 1) return it.lit;
        var a = it.angle * Math.PI / 180, sx = Math.sin(a), sy = -Math.cos(a);
        var L = Math.abs(W * sx) + Math.abs(H * sy);
        var t = (((x - W / 2) * sx + (y - H / 2) * sy) / L + 0.5) * 100;
        if (t < it.edge) return it.lit;
      }
      return false;
    };
    var qSteps = Array.prototype.slice.call(document.querySelectorAll("[data-q-step]")), qSecond = null;
    var raf = 0;
    var draw = function () {
      raf = 0;
      var vh = window.innerHeight;
      items.forEach(function (it) {
        if (!it.el) return;
        // One shared progress per transition: the trigger's top travels from 95% to 20% of the viewport.
        var top = it.el.getBoundingClientRect().top;
        var p = Math.max(0, Math.min(1, (vh * 0.95 - top) / (vh * 0.75)));
        if (reduced) p = p >= 0.5 ? 1 : 0;
        var e = p * p * (3 - 2 * p), edge = -30 + 160 * e;
        var m = p >= 1 ? "none" : "linear-gradient(" + it.angle + "deg, #000 " + (edge - 12) + "%, transparent " + (edge + 12) + "%)";
        it.p = p; it.edge = edge;
        it.f.style.opacity = p === 0 ? "0" : "1";
        it.f.style.maskImage = m; it.f.style.webkitMaskImage = m;
        it.f.style.transform = reduced ? "none" : "translate3d(0, " + ((1 - e) * 3).toFixed(2) + "%, 0)";
      });
      // Two-phrase quote: the second phrase takes the light as the quote rises past mid-screen.
      if (qSteps.length === 2) {
        var q = qSteps[0].closest("blockquote").getBoundingClientRect();
        var second = (q.top + q.height * 0.5) < vh * (reduced ? 0.6 : 0.5);
        if (qSecond !== second) {
          qSecond = second;
          qSteps[0].style.color = second ? "#5C5C5C" : "#FFFFFF";
          qSteps[1].style.color = second ? "#FFFFFF" : "#5C5C5C";
        }
      }
      var W = window.innerWidth;
      inks.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -40 || r.top > vh + 40 || !r.width) return;
        var cy = Math.max(0, Math.min(vh, r.top + r.height / 2));
        var on = litAt(r.left + r.width / 2, cy, W, vh);
        if (el.__lit !== on) {
          el.__lit = on; el.style.filter = on ? "invert(1) hue-rotate(180deg)" : "";
          if (on) el.setAttribute("data-lit", ""); else el.removeAttribute("data-lit");
          // Code blocks stay dark with light text: cancel the parent's inversion.
          el.querySelectorAll("pre").forEach(function (p) { p.style.filter = on ? "invert(1) hue-rotate(180deg)" : ""; });
        }
      });
    };
    var request = function () { if (!raf) raf = requestAnimationFrame(draw); };
    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request);
    if ("ResizeObserver" in window) {
      new ResizeObserver(function () { inks = collect(); request(); }).observe(document.querySelector("main"));
    }
    draw();
  }

  var start = function () { setupFilms(); setupLight(); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
