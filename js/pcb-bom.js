/* The PCB fixture purchases have stable IDs and their own storage namespace.
   Existing bench checklist progress is deliberately independent. */
(function () {
  "use strict";
  var KEY = "el-pcb-fixture-orders-v1";
  function init() {
    var root = document.getElementById("pcb-shopping");
    if (!root || root.dataset.initialized) return;
    root.dataset.initialized = "true";
    var boxes = Array.from(root.querySelectorAll(".pcb-order-box"));
    var message = document.getElementById("pcb-save-message");
    var state = {};
    var saveFailed = false;
    function read() {
      try {
        var value = JSON.parse(localStorage.getItem(KEY));
        return value && typeof value === "object" && !Array.isArray(value) ? value : {};
      } catch (e) {
        message.textContent = "Saved progress could not be read. Keep a copy of your shopping list.";
        return {};
      }
    }
    function render() {
      boxes.forEach(function (box) {
        box.checked = state[box.id] === true;
        box.closest("tr").classList.toggle("is-ordered", box.checked);
      });
      var required = boxes.filter(function (box) { return box.dataset.required === "true"; });
      var done = required.filter(function (box) { return box.checked; }).length;
      var bar = document.getElementById("pcb-order-progress");
      bar.max = required.length;
      bar.value = done;
      document.getElementById("pcb-order-total").textContent = done + " / " + required.length + " required purchase lines covered";
      root.querySelectorAll(".pcb-purchase-section").forEach(function (section) {
        var local = Array.from(section.querySelectorAll(".pcb-order-box"));
        section.querySelector(".pcb-section-progress").textContent = local.filter(function (box) { return box.checked; }).length + " / " + local.length + " checked";
      });
    }
    state = read();
    render();
    boxes.forEach(function (box) {
      box.disabled = false;
      box.addEventListener("change", function () {
        // Merge the current saved state so another open tab's orders survive.
        if (!saveFailed) state = Object.assign({}, state, read());
        state[box.id] = box.checked;
        try {
          localStorage.setItem(KEY, JSON.stringify(state));
          saveFailed = false;
          message.textContent = "Saved in this browser. Progress does not sync to other devices.";
        } catch (e) {
          saveFailed = true;
          message.textContent = "This browser cannot save progress. Your current checks will be lost when you leave; copy the remaining list now.";
        }
        render();
      });
    });
    window.addEventListener("storage", function (event) {
      if (!root.isConnected || saveFailed) return;
      if (event.key === KEY || event.key === null) { state = read(); render(); }
    });
    var copy = document.getElementById("pcb-copy-remaining");
    copy.disabled = false;
    copy.addEventListener("click", async function () {
      var lines = ["LIGHT v0.2 — two-fixture shopping list", "Required items not yet covered by orders, usable inventory or a selected equivalent. Resolve selection notes before buying.", ""];
      boxes.filter(function (box) { return box.dataset.required === "true" && !box.checked; }).forEach(function (box) {
        var row = box.closest("tr");
        var get = function (name) { return row.querySelector("[data-field='" + name + "']").textContent.replace(/\s+/g, " ").trim(); };
        var links = Array.from(row.querySelectorAll("a")).map(function (a) { return a.href; });
        lines.push("- " + get("product") + " | " + get("quantity") + " | " + get("selection") + " | " + get("purpose") + (links.length ? " | " + links.join(" ") : ""));
      });
      var text = lines.join("\n");
      try {
        if (!navigator.clipboard) throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(text);
        document.getElementById("pcb-copy-message").textContent = "Remaining required purchases copied.";
      } catch (e) {
        var fallback = document.getElementById("pcb-copy-fallback");
        fallback.hidden = false;
        fallback.value = text;
        fallback.focus();
        fallback.select();
        document.getElementById("pcb-copy-message").textContent = "Select and copy the shopping list below.";
      }
    });
  }
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
