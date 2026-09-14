/* Doc 10 flex-circuit viewer.
 *
 * Simpler than the board viewer: three passive circuits, no faces, no presets,
 * no parts to buy. What matters here is where each pad or insertion contact is and what rail
 * it carries, so the pads are the interactive objects.
 *
 * Shares the pan/zoom core and DOM helpers with pcb-viewer.js through
 * window.elPcbKit, and reuses its stylesheet by carrying the .el-pcb class.
 *
 * Coordinates are native KiCad millimetres, x right and y down. The published
 * layer renderings were rewritten at build time to land in that same frame, so
 * a pad from the connection table can be drawn straight on top of the copper.
 */
(function () {
  "use strict";

  var PAD_HIT_MM = 1.1;      // how close a pointer must be to claim a pad
  var kit = null;

  function boot(root) {
    kit = window.elPcbKit;
    if (!kit) return;
    var el = kit.el, svg = kit.svg;
    var base = new URL(root.dataset.base, location.href).href;
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var fallback = root.querySelector(".el-flex-fallback");
    root.dataset.state = "loading";

    var data = null, board = null, pz = null, ui = {}, store = {};
    var state = { boardId: null, layers: {}, hover: null, selected: null,
                  tipRef: null, tipPinned: false, reduced: reduced };

    kit.fetchJSON(base + "index.json").then(function (index) {
      data = index;
      build();
      return setBoard(data.boards[0].id);
    }).then(function () {
      root.dataset.state = "ready";
      if (fallback) fallback.hidden = true;
    }).catch(function (err) {
      root.dataset.state = "error";
      if (fallback) {
        fallback.hidden = false;
        var note = fallback.querySelector(".el-pcb-error");
        if (!note) {
          note = el("p", { class: "el-pcb-error" });
          fallback.insertBefore(note, fallback.firstChild);
        }
        note.textContent = "The flex viewer could not load its data. " +
          "The drawings and tables below still work.";
      }
      if (window.console && console.warn) console.warn("[flex] " + (err && err.message));
    });

    /* ---------------------------------------------------------------- DOM */
    function build() {
      var head = el("div", { class: "el-pcb-head" }, root);
      el("h3", { class: "el-pcb-title", text: "Upper v0.3 · lower and arm v0.2" }, head);
      ui.headNote = el("p", { class: "el-pcb-prov" }, head);

      var bar = el("div", { class: "el-pcb-toolbar", role: "toolbar" }, root);
      bar.setAttribute("aria-label", "Flex circuit controls");
      bar.setAttribute("data-search-exclude", "");

      var pick = el("fieldset", { class: "el-pcb-seg" }, bar);
      el("legend", { text: "Circuit" }, pick);
      ui.boardInputs = {};
      data.boards.forEach(function (b, i) {
        var lab = el("label", { class: "el-pcb-seg-opt" }, pick);
        var input = el("input", {
          type: "radio", name: "el-flex-board", value: b.id, id: "el-flex-board-" + b.id
        }, lab);
        if (i === 0) input.checked = true;
        el("span", { text: b.title }, lab);
        input.addEventListener("change", function () { if (input.checked) setBoard(b.id); });
        ui.boardInputs[b.id] = input;
      });

      ui.layerBox = el("fieldset", { class: "el-pcb-seg el-flex-layers" }, bar);
      el("legend", { text: "Layers" }, ui.layerBox);

      var buttons = el("div", { class: "el-pcb-buttons" }, bar);
      function button(label, title, fn) {
        var b = el("button", { type: "button", class: "el-pcb-btn", text: label }, buttons);
        b.title = title;
        b.addEventListener("click", fn);
        return b;
      }
      button("Zoom in", "Zoom in (+)", function () { pz.zoomBy(1 / 1.25); });
      button("Zoom out", "Zoom out (-)", function () { pz.zoomBy(1.25); });
      button("Fit", "Fill the frame with the circuit's height, then pan along it (0)", fitHeight);
      button("Whole circuit", "Show the entire length at once", function () { pz.fit(); });
      ui.clear = button("Clear selection", "Clear the pinned pad", function () { select(null); });

      ui.legend = el("ul", { class: "el-pcb-legend" }, bar);
      ui.caption = el("p", { class: "el-pcb-caption" }, root);

      var stage = el("div", { class: "el-pcb-stage el-flex-stage" }, root);
      var canvas = el("div", {
        class: "el-pcb-canvas el-flex-canvas", tabindex: "0", role: "group",
        "aria-roledescription": "flex circuit viewer"
      }, stage);
      ui.canvas = canvas;
      ui.svg = svg("svg", {
        class: "el-pcb-svg", preserveAspectRatio: "xMidYMid meet",
        "aria-hidden": "true", focusable: "false"
      }, canvas);
      ui.layers = svg("g", { class: "el-pcb-layers" }, ui.svg);
      ui.padG = svg("g", { class: "el-flex-pads" }, ui.svg);
      ui.rings = svg("g", { class: "el-pcb-rings" }, ui.svg);
      ui.tip = el("div", {
        id: "el-flex-tip", class: "el-pcb-tip", role: "dialog",
        "aria-label": "Pad summary", "aria-modal": "false", hidden: "hidden"
      }, canvas);
      ui.status = el("p", { class: "el-pcb-status", role: "status" }, canvas);
      ui.status.setAttribute("aria-live", "polite");

      var finder = el("div", { class: "el-pcb-finder el-flex-finder" }, root);
      finder.setAttribute("data-search-exclude", "");
      el("label", { for: "el-flex-search", text: "Find a pad" }, finder);
      ui.search = el("input", {
        type: "search", id: "el-flex-search", class: "el-pcb-search",
        placeholder: "reference, rail or net"
      }, finder);
      ui.results = el("p", { class: "el-flex-results" }, finder);
      ui.search.addEventListener("input", runSearch);

      pz = new kit.PanZoom(ui.svg, [0, 0, 10, 10], { minW: 1.5 });
      pz.frameNode = ui.padG;
      pz.onApply = function () { sizePads(); repositionTip(); };
      wirePointer(canvas);
      wireKeys(canvas);
    }

    /* -------------------------------------------------------------- board */
    function setBoard(id) {
      board = data.boards.filter(function (b) { return b.id === id; })[0];
      state.boardId = id;
      state.selected = null;
      root.dataset.board = id;
      if (ui.boardInputs[id]) ui.boardInputs[id].checked = true;
      hideTip();

      ui.headNote.textContent = board.design + " · " + board.copper_layers +
        (board.copper_layers === 1 ? " copper layer · " : " copper layers · ") +
        board.size_mm[0].toFixed(1) + " × " + board.size_mm[1].toFixed(1) + " mm";
      ui.caption.textContent = board.what +
        " The copper and coverlay shown are this circuit's own manufacturing layers; the small markers " +
        "are the pads and insertion contacts listed in its connection table, not their exact outlines.";

      ui.layers.innerHTML = "";
      ui.layerBox.querySelectorAll("label").forEach(function (n) { n.remove(); });
      ui.layerInputs = {};
      state.layers = {};
      board.layers.forEach(function (layer) {
        svg("g", { class: "el-pcb-layer", "data-layer": layer.id, style: "display:none" }, ui.layers);
        var lab = el("label", { class: "el-pcb-check" }, ui.layerBox);
        var input = el("input", { type: "checkbox", value: layer.id }, lab);
        el("span", { text: layer.label }, lab);
        lab.title = layer.plain;
        input.addEventListener("change", function () { toggleLayer(layer.id, input.checked); });
        ui.layerInputs[layer.id] = input;
      });

      drawPads();
      pz.bounds = board.frame.viewBox.slice();
      pz.maxW = pz.bounds[2] * 2;
      fitHeight();

      var wanted = board.layers.filter(function (l) {
        return l.id === "Edge_Cuts" || l.id === "F_Cu" || l.id === "F_Silkscreen" ||
          (id === "upper" && l.id === "B_Cu");
      });
      return Promise.all(wanted.map(function (l) { return toggleLayer(l.id, true); }))
        .then(function () {
          say(board.title + ": " + board.pads.length + " pads / contacts. Drag sideways to run along "
              + "the circuit, or press Whole circuit to see its full length.");
          runSearch();
        });
    }

    /* These circuits are long and thin -- the arm ribbon is sixteen times longer
       than it is wide. Fitting the whole length makes a hairline, so the default
       view fills the frame with the circuit's height and the reader pans along
       it, the way you would run your eye down a real ribbon. */
    function fitHeight() {
      var frame = board.frame.viewBox;
      var box = ui.canvas.getBoundingClientRect();
      var aspect = (box.width && box.height) ? box.width / box.height : 4;
      var h = frame[3] * 1.15;
      var w = h * aspect;
      if (w >= frame[2]) { pz.fit(); return; }
      // The new tall upper tail is the teaching focus; starting at the band's
      // left edge would show mostly empty space and hide its actual plug.
      var insertion = board.pads.filter(function (p) { return p.ref === "J100"; });
      var left = frame[0];
      if (insertion.length) {
        var centre = insertion.reduce(function (sum, p) { return sum + p.xy[0]; }, 0) / insertion.length;
        left = centre - w / 2;
      }
      pz.set({
        x: left,
        y: frame[1] - (h - frame[3]) / 2,
        w: w, h: h
      });
    }

    function layerMeta(id) {
      return board.layers.filter(function (l) { return l.id === id; })[0];
    }

    function toggleLayer(id, on) {
      var meta = layerMeta(id);
      var g = ui.layers.querySelector('[data-layer="' + id + '"]');
      if (!meta || !g) return Promise.resolve();
      if (ui.layerInputs[id]) ui.layerInputs[id].checked = on;
      state.layers[id] = on;
      if (!on) { g.style.display = "none"; updateLegend(); return Promise.resolve(); }
      var key = board.id + "/" + id;
      // Cache the markup, not a flag: switching circuits empties these groups,
      // so coming back has to be able to put the geometry in again.
      if (store[key]) {
        if (!g.firstChild) g.innerHTML = store[key];
        g.style.display = "";
        updateLegend();
        return Promise.resolve();
      }
      return kit.fetchSVG(base + meta.file).then(function (rootNode) {
        while (rootNode.firstChild) g.appendChild(rootNode.firstChild);
        store[key] = g.innerHTML;
        g.style.display = "";
        updateLegend();
      }).catch(function (err) {
        if (ui.layerInputs[id]) ui.layerInputs[id].checked = false;
        state.layers[id] = false;
        say(meta.label + " could not be loaded.");
        if (window.console && console.warn) console.warn("[flex] " + id + ": " + err.message);
      });
    }

    function updateLegend() {
      ui.legend.innerHTML = "";
      board.layers.forEach(function (l) {
        if (!state.layers[l.id]) return;
        var li = el("li", { class: "el-pcb-chip", "data-layer": l.id }, ui.legend);
        svg("svg", { class: "el-pcb-swatch", viewBox: "0 0 10 10", "aria-hidden": "true" }, li)
          .appendChild(svg("rect", { x: 0, y: 0, width: 10, height: 10 }));
        el("span", { text: l.label }, li);
      });
    }

    function drawPads() {
      ui.padG.innerHTML = "";
      ui.rings.innerHTML = "";
      board.pads.forEach(function (p, i) {
        svg("circle", {
          cx: p.xy[0], cy: p.xy[1], r: 0.45, class: "el-flex-pad",
          "data-pad": String(i), "data-ref": p.ref
        }, ui.padG);
      });
      sizePads();
    }

    /* A marker fixed in millimetres is either a blob that swallows the copper
       finger it sits on, or invisible once the whole 325 mm band is in frame.
       Hold it at roughly four screen pixels instead, bounded so it never grows
       wider than the narrowest finger it has to mark. */
    function sizePads() {
      var box = ui.canvas.getBoundingClientRect();
      if (!box.width || !pz) return;
      var r = 4 * pz.view.w / box.width;
      r = Math.max(0.09, Math.min(0.42, r));
      var pads = ui.padG.childNodes;
      for (var i = 0; i < pads.length; i++) {
        pads[i].setAttribute("r", r);
        pads[i].setAttribute("stroke-width", r / 7);
      }
    }

    /* ------------------------------------------------------------ picking */
    function padAt(x, y) {
      var best = null;
      board.pads.forEach(function (p, i) {
        var d = Math.hypot(p.xy[0] - x, p.xy[1] - y);
        if (d <= PAD_HIT_MM && (!best || d < best.d)) best = { i: i, d: d, pad: p };
      });
      return best;
    }

    function padLabel(p) {
      return p.ref + " pin " + p.pin;
    }

    function padWhat(p) {
      if (p.net) return p.net;
      if (p.rail) return p.rail + " rail";
      return "unnamed in the bare circuit";
    }

    function drawRings() {
      ui.rings.innerHTML = "";
      if (state.hover !== null && state.hover !== state.selected) ring(state.hover, "hover");
      if (state.selected !== null) ring(state.selected, "selected");
    }

    function ring(index, kind) {
      var p = board.pads[index];
      if (!p) return;
      svg("circle", {
        cx: p.xy[0], cy: p.xy[1], r: 0.9, class: "el-pcb-ring " + kind
      }, ui.rings);
    }

    /* ----------------------------------------------------------- summary */
    function hideTip() {
      ui.tip.hidden = true;
      state.tipRef = null;
      state.tipPinned = false;
    }

    function showTip(index, point, pinned) {
      var p = board.pads[index];
      if (!p) return;
      state.tipRef = index;
      state.tipPinned = !!pinned;
      ui.tip.innerHTML = "";
      ui.tip.classList.toggle("is-pinned", !!pinned);
      if (pinned) {
        var close = el("button", {
          type: "button", class: "el-pcb-tip-close", "aria-label": "Close this summary", text: "×"
        }, ui.tip);
        close.addEventListener("click", function () {
          hideTip();
          ui.canvas.focus({ preventScroll: true });
        });
      }
      el("strong", { text: padLabel(p) }, ui.tip);
      el("span", { class: "el-pcb-tip-meta", text: board.title }, ui.tip);
      el("span", { class: "el-pcb-tip-here", text: "Carries: " + padWhat(p) }, ui.tip);
      if (p.role) el("span", { class: "el-pcb-tip-how", text: p.role }, ui.tip);
      if (pinned) {
        var actions = el("div", { class: "el-pcb-tip-actions" }, ui.tip);
        var jump = el("button", {
          type: "button", class: "el-pcb-btn el-flex-tip-table", text: "Show in the connection table"
        }, actions);
        jump.addEventListener("click", function () { jumpToRow(p); });
      }
      ui.tip.hidden = false;
      placeTip(p, point);
    }

    function repositionTip() {
      if (ui.tip.hidden || state.tipRef === null) return;
      placeTip(board.pads[state.tipRef], null);
    }

    function placeTip(p, point) {
      var stage = ui.canvas.getBoundingClientRect();
      var tip = ui.tip.getBoundingClientRect();
      var at = pz.toScreen(p.xy[0], p.xy[1]);
      if (!at) return;
      var gap = 12;
      var candidates = [
        { x: at.x - tip.width / 2, y: at.y - tip.height - gap },
        { x: at.x - tip.width / 2, y: at.y + gap },
        { x: at.x + gap, y: at.y - tip.height / 2 },
        { x: at.x - tip.width - gap, y: at.y - tip.height / 2 }
      ];
      var chosen = null;
      for (var i = 0; i < candidates.length; i++) {
        var c = candidates[i];
        if (c.x >= stage.left + 2 && c.x + tip.width <= stage.right - 2 &&
            c.y >= stage.top + 2 && c.y + tip.height <= stage.bottom - 2) { chosen = c; break; }
      }
      if (!chosen) {
        chosen = {
          x: Math.min(Math.max((point ? point.x : at.x) + gap, stage.left + 2),
                      stage.right - tip.width - 2),
          y: Math.min(Math.max(at.y + gap, stage.top + 2), stage.bottom - tip.height - 2)
        };
      }
      ui.tip.style.left = (chosen.x - stage.left) + "px";
      ui.tip.style.top = (chosen.y - stage.top) + "px";
    }

    function select(index, point) {
      state.selected = index;
      root.dataset.selected = index === null ? "" : padLabel(board.pads[index]);
      if (index === null) { hideTip(); drawRings(); markRow(null); say("Selection cleared."); return; }
      var p = board.pads[index];
      drawRings();
      showTip(index, point || null, true);
      markRow(p);
      say(padLabel(p) + " carries " + padWhat(p) +
          ". Use “Show in the connection table” to jump to its row.");
    }

    function rowFor(p) {
      return document.querySelector(
        '[data-flex-row="' + board.id + ":" + p.ref + ":" + p.pin + '"]');
    }

    function markRow(p) {
      var marked = document.querySelectorAll("[data-flex-row][aria-current]");
      Array.prototype.forEach.call(marked, function (n) { n.removeAttribute("aria-current"); });
      if (!p) return;
      var tr = rowFor(p);
      if (tr) tr.setAttribute("aria-current", "true");
    }

    function jumpToRow(p) {
      var tr = rowFor(p);
      if (!tr) { say("That pad has no row in the published table."); return; }
      var box = tr.closest("details");
      if (box && !box.open) box.open = true;
      markRow(p);
      tr.scrollIntoView({ block: "center", behavior: state.reduced ? "auto" : "smooth" });
      say("Moved to the connection table row for " + padLabel(p) + ".");
    }

    function say(message) { ui.status.textContent = message; }

    /* ------------------------------------------------------------ search */
    function runSearch() {
      var q = (ui.search.value || "").trim().toLowerCase();
      if (!q) {
        ui.results.textContent = board.pads.length + " pads on this circuit.";
        state.hover = null;
        drawRings();
        return;
      }
      var hits = [];
      board.pads.forEach(function (p, i) {
        var hay = (p.ref + " " + p.pin + " " + p.net + " " + p.rail + " " + p.role).toLowerCase();
        if (hay.indexOf(q) >= 0) hits.push(i);
      });
      ui.results.textContent = hits.length
        ? hits.length + " matching pad" + (hits.length === 1 ? "" : "s") + " highlighted."
        : "No pad matches " + ui.search.value + ".";
      ui.rings.innerHTML = "";
      hits.forEach(function (i) { ring(i, "group"); });
      if (state.selected !== null) ring(state.selected, "selected");
    }

    /* ------------------------------------------------------- interaction */
    function wirePointer(canvas) {
      var dragging = false, moved = false, last = null, pointers = {}, pinch = null;

      function inTip(e) {
        return !!(e.target && e.target.closest && e.target.closest(".el-pcb-tip"));
      }

      canvas.addEventListener("pointerdown", function (e) {
        if (inTip(e)) return;
        pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        if (Object.keys(pointers).length === 2) {
          pinch = pinchState(pointers);
          dragging = false;
          return;
        }
        dragging = true; moved = false; last = { x: e.clientX, y: e.clientY };
        canvas.setPointerCapture(e.pointerId);
      });

      canvas.addEventListener("pointermove", function (e) {
        if (inTip(e) && !dragging) return;
        if (pointers[e.pointerId]) pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        if (Object.keys(pointers).length === 2 && pinch) {
          var now = pinchState(pointers);
          pz.zoomAt(pinch.dist / now.dist, now.cx, now.cy);
          pinch = now;
          return;
        }
        if (dragging) {
          var dx = e.clientX - last.x, dy = e.clientY - last.y;
          if (Math.abs(dx) > 5 || Math.abs(dy) > 5) moved = true;
          if (moved) {
            var box = canvas.getBoundingClientRect();
            var v = pz.view;
            pz.panBy(-dx * v.w / box.width, -dy * v.h / box.height);
          }
          last = { x: e.clientX, y: e.clientY };
          return;
        }
        if (e.pointerType === "touch" || state.tipPinned) {
          if (state.tipPinned) return;
        }
        var p = pz.toWorld(e.clientX, e.clientY);
        if (!p) return;
        var hit = padAt(p.x, p.y);
        state.hover = hit ? hit.i : null;
        drawRings();
        if (hit) showTip(hit.i, { x: e.clientX, y: e.clientY }, false);
        else if (!state.tipPinned) hideTip();
      });

      canvas.addEventListener("pointerup", function (e) {
        var wasDragging = dragging, wasMoved = moved;
        delete pointers[e.pointerId];
        if (Object.keys(pointers).length < 2) pinch = null;
        dragging = false;
        if (!wasDragging || wasMoved) return;
        var p = pz.toWorld(e.clientX, e.clientY);
        if (!p) return;
        var hit = padAt(p.x, p.y);
        if (hit) {
          select(hit.i, { x: e.clientX, y: e.clientY });
          canvas.focus({ preventScroll: true });
        } else {
          hideTip();
          state.hover = null;
          drawRings();
        }
      });
      canvas.addEventListener("pointercancel", function (e) {
        delete pointers[e.pointerId]; pinch = null; dragging = false;
      });
      canvas.addEventListener("pointerleave", function () {
        if (!dragging && !state.tipPinned) { state.hover = null; drawRings(); hideTip(); }
      });
      canvas.addEventListener("wheel", function (e) {
        e.preventDefault();
        var step = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
        pz.zoomAt(step > 0 ? 1.12 : 1 / 1.12, e.clientX, e.clientY);
      }, { passive: false });
      canvas.addEventListener("dblclick", function (e) { pz.zoomAt(0.5, e.clientX, e.clientY); });
    }

    function pinchState(pointers) {
      var ids = Object.keys(pointers);
      var a = pointers[ids[0]], b = pointers[ids[1]];
      return {
        dist: Math.max(1, Math.hypot(a.x - b.x, a.y - b.y)),
        cx: (a.x + b.x) / 2, cy: (a.y + b.y) / 2
      };
    }

    function wireKeys(canvas) {
      canvas.addEventListener("keydown", function (e) {
        var handled = true;
        switch (e.key) {
          case "ArrowLeft": pz.panFraction(-0.1, 0); break;
          case "ArrowRight": pz.panFraction(0.1, 0); break;
          case "ArrowUp": pz.panFraction(0, -0.1); break;
          case "ArrowDown": pz.panFraction(0, 0.1); break;
          case "+": case "=": pz.zoomBy(1 / 1.25); break;
          case "-": case "_": pz.zoomBy(1.25); break;
          case "0": fitHeight(); break;
          case "Escape": hideTip(); state.hover = null; drawRings(); break;
          default: handled = false;
        }
        if (handled) e.preventDefault();
      });
    }

    window.elFlex = {
      setBoard: setBoard,
      fitHeight: fitHeight,
      toggleLayer: toggleLayer,
      select: function (i) { select(i); },
      padAt: padAt,
      toScreen: function (x, y) { return pz.toScreen(x, y); },
      toWorld: function (x, y) { return pz.toWorld(x, y); },
      getState: function () {
        return {
          board: state.boardId, selected: state.selected,
          pads: board ? board.pads.length : 0,
          layers: Object.keys(state.layers).filter(function (k) { return state.layers[k]; }).sort(),
          view: pz.view, pinned: state.tipPinned
        };
      }
    };
  }

  function initAll() {
    var root = document.getElementById("el-flex");
    if (!root || root.dataset.init) return;
    root.dataset.init = "1";
    try {
      boot(root);
    } catch (err) {
      root.dataset.state = "error";
      if (window.console && console.warn) console.warn("[flex] " + err.message);
    }
  }

  if (typeof document$ !== "undefined") document$.subscribe(initAll);
  else document.addEventListener("DOMContentLoaded", initAll);
})();
