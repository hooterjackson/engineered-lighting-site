/* BoM checklist: localStorage persistence, progress math, copy/reset.
   State key: el-bom-v1  →  {"d3-motors":1, ...} (checked ids only). */
(function () {
  var KEY = "el-bom-v1";

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; }
    catch (e) { return {}; }
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
    function done() {
      var old = btn.textContent;
      btn.textContent = "Copied ✓";
      setTimeout(function () { btn.textContent = old; }, 1500);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
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

  // Works with or without Material's instant navigation.
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
