/* BoM checklist: localStorage persistence, progress math, copy/reset.
   State key: el-bom-v1  →  {"d3-motors":1, ...} (checked ids only).
   Chapter "Done when" verdict lists share the pattern under el-done-v1,
   keyed by page slug + checkbox position (reordering a doc's checklist
   items shifts saved state — accepted trade-off, documented in README). */
(function () {
  var KEY = "el-bom-v1";
  var DONE_KEY = "el-done-v1";

  function load() {
    try {
      var s = JSON.parse(localStorage.getItem(KEY));
      return (s && typeof s === "object" && !Array.isArray(s)) ? s : {};
    } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  function boxes(section) {
    return Array.prototype.slice.call(section.querySelectorAll("input.bom-box"));
  }

  function midpoint(box) {
    var lo = parseFloat(box.dataset.lo);
    var hi = parseFloat(box.dataset.hi);
    if (isNaN(lo)) return 0; // no estimate (—, dealer quote, free)
    return (lo + (isNaN(hi) ? lo : hi)) / 2;
  }

  function render(sections) {
    var total = 0, checked = 0;
    sections.forEach(function (sec) {
      var bs = boxes(sec);
      var done = bs.filter(function (b) { return b.checked; });
      var dollars = done.reduce(function (s, b) { return s + midpoint(b); }, 0);
      sec.querySelector(".bom-progress").textContent =
        done.length + "/" + bs.length + " · ~$" + Math.round(dollars) + " checked";
      total += bs.length;
      checked += done.length;
    });
    var bar = document.getElementById("bom-bar");
    if (bar) { bar.max = total; bar.value = checked; }
    var txt = document.getElementById("bom-global-text");
    if (txt) txt.textContent = checked + "/" + total + " items";
  }

  function partName(cell) {
    var clone = cell.cloneNode(true);
    var badge = clone.querySelector(".bom-optional");
    if (badge) badge.remove();
    return clone.textContent.replace(/\s+/g, " ").trim();
  }

  function shoppingList(sec) {
    var lines = [sec.querySelector("summary strong").textContent, ""];
    boxes(sec).forEach(function (b) {
      if (b.checked) return;
      var cells = b.closest("tr").querySelectorAll("td");
      lines.push("- [ ] " + cells[2].textContent.trim() + " × " + partName(cells[1]) +
        " — " + cells[3].textContent.trim() + " (" + cells[4].textContent.trim() + ")");
    });
    return lines.join("\n");
  }

  function copyText(text, btn) {
    if (btn.dataset.busy) return; // ignore clicks while feedback is showing
    var label = btn.dataset.label || (btn.dataset.label = btn.textContent);
    function feedback(message) {
      btn.dataset.busy = "1";
      btn.textContent = message;
      setTimeout(function () { btn.textContent = label; delete btn.dataset.busy; }, 1500);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) {}
      document.body.removeChild(ta);
      feedback(ok ? "Copied ✓" : "Copy failed");
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { feedback("Copied ✓"); }, fallback);
    } else fallback();
  }

  function init() {
    var sections = Array.prototype.slice.call(document.querySelectorAll(".bom-section"));
    if (!sections.length || sections[0].dataset.bomInit) return;
    sections[0].dataset.bomInit = "1";

    var state = load();
    sections.forEach(function (sec) {
      boxes(sec).forEach(function (b) { b.checked = !!state[b.id]; });

      sec.addEventListener("change", function (e) {
        if (!e.target.classList.contains("bom-box")) return;
        if (e.target.checked) state[e.target.id] = 1;
        else delete state[e.target.id];
        save(state);
        render(sections);
      });

      sec.querySelector("[data-reset]").addEventListener("click", function () {
        boxes(sec).forEach(function (b) { b.checked = false; delete state[b.id]; });
        save(state);
        render(sections);
      });

      sec.querySelector("[data-copy]").addEventListener("click", function (e) {
        copyText(shoppingList(sec), e.target);
      });
    });
    render(sections);
  }

  function initDone() {
    var boxes = Array.prototype.slice.call(
      document.querySelectorAll(".md-content .task-list-item > .task-list-control > [type=checkbox]"));
    if (!boxes.length || boxes[0].dataset.doneInit) return;
    boxes[0].dataset.doneInit = "1";

    var slug = location.pathname.replace(/\/+$/, "").split("/").pop() || "index";
    var state;
    try {
      var s = JSON.parse(localStorage.getItem(DONE_KEY));
      state = (s && typeof s === "object" && !Array.isArray(s)) ? s : {};
    } catch (e) { state = {}; }

    var lists = [];
    boxes.forEach(function (b, i) {
      b.disabled = false;
      b.checked = !!state[slug + ":" + i];
      b.addEventListener("change", function () {
        if (b.checked) state[slug + ":" + i] = 1;
        else delete state[slug + ":" + i];
        try { localStorage.setItem(DONE_KEY, JSON.stringify(state)); } catch (e) {}
        renderDone();
      });
      var ul = b.closest("ul");
      if (ul && lists.indexOf(ul) < 0) lists.push(ul);
    });

    function renderDone() {
      lists.forEach(function (ul) {
        var bs = Array.prototype.slice.call(ul.querySelectorAll("[type=checkbox]"));
        var n = bs.filter(function (b) { return b.checked; }).length;
        var chip = ul.nextElementSibling;
        if (!chip || !chip.classList || !chip.classList.contains("el-done-progress")) {
          chip = document.createElement("p");
          chip.className = "el-done-progress";
          ul.parentNode.insertBefore(chip, ul.nextSibling);
        }
        chip.textContent = n + "/" + bs.length + " done";
      });
    }
    renderDone();
  }

  function initAll() { init(); initDone(); }

  // Works with or without Material's instant navigation.
  if (typeof document$ !== "undefined") document$.subscribe(initAll);
  else document.addEventListener("DOMContentLoaded", initAll);
})();
