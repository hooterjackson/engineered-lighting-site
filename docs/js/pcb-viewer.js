/* Doc 9 board viewer, schematic browser and parts-list cross-linking.
 *
 * Loaded on every page (extra_javascript), so it does nothing at all unless the
 * page contains #el-pcb. Written against no library on purpose: the site's
 * requirements are pinned and CI installs exactly that list.
 *
 * Coordinate contract, which the whole file depends on:
 *   - world space is native KiCad millimetres, x right, y down, unmirrored
 *   - the root <svg> viewBox IS the pan/zoom state, in world units
 *   - the physical back view is ONE transform, matrix(-1 0 0 1 200 0), on the
 *     group that holds every piece of geometry; nothing else is mirrored
 *   - pointer positions come back through getScreenCTM().inverse(), never
 *     through ad-hoc pixel arithmetic
 *   - pad geometry is already world-positioned: translate(cx cy) rotate(-rot)
 */
(function () {
  "use strict";

  var SVG = "http://www.w3.org/2000/svg";
  var PAD = 1.5;            // mm of air around the fitted board
  var MIN_W = 2;            // closest zoom, in mm of visible width
  var MAX_SCALE = 2;        // furthest zoom, as a multiple of the fit width
  var TAP_SLOP = 24;        // px: how far a touch may miss and still select
  var Z_BASE = { copper: 8, mask: 9, silk: 10, fab: 11, courtyard: 12 };

  function el(name, attrs, parent) {
    var node = document.createElement(name);
    apply(node, attrs);
    if (parent) parent.appendChild(node);
    return node;
  }

  function svg(name, attrs, parent) {
    var node = document.createElementNS(SVG, name);
    apply(node, attrs);
    if (parent) parent.appendChild(node);
    return node;
  }

  function apply(node, attrs) {
    if (!attrs) return;
    Object.keys(attrs).forEach(function (key) {
      var value = attrs[key];
      if (value === null || value === undefined) return;
      if (key === "text") node.textContent = value;
      else if (key === "html") node.innerHTML = value;
      else if (key === "class") node.setAttribute("class", value);
      else node.setAttribute(key, value);
    });
  }

  function refKey(ref) {
    var m = /^([A-Za-z]+)(\d+)$/.exec(ref || "");
    return m ? [m[1], parseInt(m[2], 10)] : [ref || "", 0];
  }

  function byRef(a, b) {
    var ka = refKey(a), kb = refKey(b);
    if (ka[0] !== kb[0]) return ka[0] < kb[0] ? -1 : 1;
    return ka[1] - kb[1];
  }

  function faceWord(side) { return side === "F" ? "front" : "back"; }

  /* ----------------------------------------------------------------- data */
  function fetchJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " returned " + r.status);
      return r.json();
    });
  }

  function fetchSVG(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " returned " + r.status);
      return r.text();
    }).then(function (text) {
      var doc = new DOMParser().parseFromString(text, "image/svg+xml");
      if (doc.querySelector("parsererror")) throw new Error(url + " is not valid SVG");
      return doc.documentElement;
    });
  }

  /* ------------------------------------------------------------- pan/zoom */
  function PanZoom(root, bounds, opts) {
    this.root = root;
    this.bounds = bounds;
    this.minW = (opts && opts.minW) || MIN_W;
    this.maxW = bounds[2] * MAX_SCALE;
    this.reduced = opts && opts.reduced;
    this.view = null;
    this.frame = null;
    this.fit();
  }

  PanZoom.prototype.fit = function () {
    var b = this.bounds;
    this.set({ x: b[0], y: b[1], w: b[2], h: b[3] });
  };

  PanZoom.prototype.set = function (view) {
    this.view = view;
    var self = this;
    if (this.frame) return;
    this.frame = requestAnimationFrame(function () {
      self.frame = null;
      var v = self.view;
      self.root.setAttribute("viewBox", v.x + " " + v.y + " " + v.w + " " + v.h);
      if (self.onApply) self.onApply();
    });
  };

  PanZoom.prototype.clampWidth = function (w) {
    return Math.max(this.minW, Math.min(this.maxW, w));
  };

  PanZoom.prototype.zoomAt = function (factor, clientX, clientY) {
    var v = this.view;
    var w = this.clampWidth(v.w * factor);
    var k = w / v.w;
    var p = this.toWorld(clientX, clientY);
    if (!p) { this.set({ x: v.x, y: v.y, w: w, h: v.h * k }); return; }
    this.set({
      x: p.x - (p.x - v.x) * k,
      y: p.y - (p.y - v.y) * k,
      w: w, h: v.h * k
    });
  };

  PanZoom.prototype.zoomBy = function (factor) {
    var box = this.root.getBoundingClientRect();
    this.zoomAt(factor, box.left + box.width / 2, box.top + box.height / 2);
  };

  PanZoom.prototype.panBy = function (dx, dy) {
    var v = this.view;
    this.set({ x: v.x + dx, y: v.y + dy, w: v.w, h: v.h });
  };

  PanZoom.prototype.panFraction = function (fx, fy) {
    this.panBy(this.view.w * fx, this.view.h * fy);
  };

  PanZoom.prototype.zoomTo = function (box, minWidth) {
    var v = this.view;
    var want = this.clampWidth(Math.max(minWidth || 12, box[2] * 4, box[3] * 4 * (v.w / v.h)));
    var h = want * (v.h / v.w);
    this.set({
      x: box[0] + box[2] / 2 - want / 2,
      y: box[1] + box[3] / 2 - h / 2,
      w: want, h: h
    });
  };

  PanZoom.prototype.ensureVisible = function (box) {
    var v = this.view;
    var cx = box[0] + box[2] / 2, cy = box[1] + box[3] / 2;
    if (cx >= v.x && cx <= v.x + v.w && cy >= v.y && cy <= v.y + v.h) return;
    this.set({ x: cx - v.w / 2, y: cy - v.h / 2, w: v.w, h: v.h });
  };

  PanZoom.prototype.toWorld = function (clientX, clientY) {
    var ctm = this.frameNode ? this.frameNode.getScreenCTM() : this.root.getScreenCTM();
    if (!ctm) return null;
    var p = new DOMPoint(clientX, clientY).matrixTransform(ctm.inverse());
    return { x: p.x, y: p.y };
  };

  PanZoom.prototype.toScreen = function (x, y) {
    var ctm = this.frameNode ? this.frameNode.getScreenCTM() : this.root.getScreenCTM();
    if (!ctm) return null;
    var p = new DOMPoint(x, y).matrixTransform(ctm);
    return { x: p.x, y: p.y };
  };

  /* ---------------------------------------------------------- hit testing */
  function HitIndex(components) {
    this.items = components.map(function (c) {
      var pads = [];
      var through = [];
      c.pads.forEach(function (p) {
        if (p.paste) return;
        var w = p.size[0], h = p.size[1];
        var shape = {
          cx: p.xy[0], cy: p.xy[1], w: w, h: h,
          rot: p.rot * Math.PI / 180,
          round: p.shape === 0 || p.shape === 2,
          area: w * h, custom: p.shape === 6, bbox: p.bbox
        };
        pads.push(shape);
        if (p.through) through.push(shape);
      });
      return {
        ref: c.ref, side: c.side, through: !!c.through,
        box: c.bbox, area: c.bbox[2] * c.bbox[3],
        pads: pads, throughPads: through
      };
    });
    this.byRef = {};
    var self = this;
    this.items.forEach(function (i) { self.byRef[i.ref] = i; });
  }

  function inPad(pad, x, y, slop) {
    var dx = x - pad.cx, dy = y - pad.cy;
    if (pad.custom) {
      return x >= pad.bbox[0] - slop && x <= pad.bbox[0] + pad.bbox[2] + slop &&
             y >= pad.bbox[1] - slop && y <= pad.bbox[1] + pad.bbox[3] + slop;
    }
    var c = Math.cos(pad.rot), s = Math.sin(pad.rot);
    var lx = c * dx - s * dy, ly = s * dx + c * dy;
    if (pad.round && pad.w === pad.h) {
      return Math.hypot(lx, ly) <= pad.w / 2 + slop;
    }
    return Math.abs(lx) <= pad.w / 2 + slop && Math.abs(ly) <= pad.h / 2 + slop;
  }

  function inBox(box, x, y) {
    return x >= box[0] && x <= box[0] + box[2] && y >= box[1] && y <= box[1] + box[3];
  }

  HitIndex.prototype.hitTest = function (x, y, face) {
    var candidates = [];
    this.items.forEach(function (item) {
      var visible = item.side === face;
      var reachable = visible;
      if (!visible && item.through) {
        reachable = item.throughPads.some(function (p) { return inPad(p, x, y, 0); });
      }
      if (!reachable || !inBox(item.box, x, y)) return;
      var best = null;
      item.pads.forEach(function (p) {
        var slop = Math.min(p.w, p.h) < 0.5 ? 0.15 : 0;
        if (inPad(p, x, y, slop) && (best === null || p.area < best)) best = p.area;
      });
      candidates.push({ ref: item.ref, padHit: best !== null, padArea: best, boxArea: item.area });
    });
    if (!candidates.length) return null;
    candidates.sort(function (a, b) {
      if (a.padHit !== b.padHit) return a.padHit ? -1 : 1;
      if (a.padHit && a.padArea !== b.padArea) return a.padArea - b.padArea;
      if (a.boxArea !== b.boxArea) return a.boxArea - b.boxArea;
      return byRef(a.ref, b.ref);
    });
    return candidates[0];
  };

  HitIndex.prototype.nearest = function (x, y, face, limit) {
    var best = null;
    this.items.forEach(function (item) {
      if (item.side !== face && !item.through) return;
      var cx = item.box[0] + item.box[2] / 2, cy = item.box[1] + item.box[3] / 2;
      var d = Math.hypot(cx - x, cy - y);
      if (d <= limit && (!best || d < best.d)) best = { ref: item.ref, d: d };
    });
    return best ? { ref: best.ref, padHit: false, padArea: null, boxArea: null } : null;
  };

  /* -------------------------------------------------------- layer loading */
  function LayerStore(base, container, slots) {
    this.base = base;
    this.container = container;
    this.slots = slots;
    this.cache = {};
    this.pending = {};
  }

  LayerStore.prototype.group = function (id) {
    return this.container.querySelector('[data-layer="' + id + '"]');
  };

  LayerStore.prototype.load = function (layer) {
    var id = layer.id;
    if (this.cache[id]) return Promise.resolve(this.cache[id]);
    if (this.pending[id]) return this.pending[id];
    var self = this;
    var group = this.group(id);
    var p = fetchSVG(this.base + layer.file).then(function (root) {
      while (root.firstChild) group.appendChild(root.firstChild);
      self.cache[id] = group;
      delete self.pending[id];
      return group;
    }).catch(function (err) {
      delete self.pending[id];
      throw err;
    });
    this.pending[id] = p;
    return p;
  };

  /* ============================================================ the viewer */
  function boot(root) {
    var base = new URL(root.dataset.base, location.href).href;
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var fallback = root.querySelector(".el-pcb-fallback");
    var schRoot = document.getElementById("el-sch");
    root.dataset.state = "loading";

    var state = {
      face: "F", preset: "components", inner: "In1_Cu", appearance: "material",
      layers: {}, hover: null, selected: null, group: [],
      tipRef: null, tipPinned: false,
      autoFit: true, reduced: reduced, lockPan: false
    };
    var data = {};
    var ui = {};
    var pz = null, hits = null, store = null;

    function fail(what, err) {
      root.dataset.state = "error";
      if (fallback) {
        fallback.hidden = false;
        var img = fallback.querySelector("img[data-src]");
        if (img && !img.getAttribute("src")) img.setAttribute("src", img.dataset.src);
        var note = fallback.querySelector(".el-pcb-error");
        if (!note) {
          note = el("p", { class: "el-pcb-error" });
          fallback.insertBefore(note, fallback.firstChild);
        }
        note.textContent = "The board viewer could not load " + what +
          ". The drawings and tables below still work.";
      }
      if (window.console && console.warn) console.warn("[pcb] " + what + ": " + (err && err.message));
    }

    Promise.all([
      fetchJSON(base + "board.json"),
      fetchJSON(base + "teaching.json"),
      fetchJSON(base + "bom.json"),
      fetchJSON(base + "schematic/index.json")
    ]).then(function (loaded) {
      data.board = loaded[0];
      data.teach = loaded[1];
      data.bom = loaded[2];
      data.sch = loaded[3];
      data.comp = {};
      data.board.components.forEach(function (c) { data.comp[c.ref] = c; });
      data.rowByItem = {};
      data.bom.rows.forEach(function (r) { data.rowByItem[r.item] = r; });
      build();
      return Promise.all([
        store.load(layerById("Edge_Cuts")),
        store.load(layerById("F_Fab"))
      ]);
    }).then(function () {
      applyPreset("components", true);
      pz.fit();
      root.dataset.state = "ready";
      if (fallback) fallback.hidden = true;
      readHash();
      prefetch();
    }).catch(function (err) {
      fail(err && err.message ? err.message : "its data", err);
    });

    function layerById(id) {
      return data.board.layers.filter(function (l) { return l.id === id; })[0];
    }

    /* ------------------------------------------------------------- build */
    function build() {
      var head = el("div", { class: "el-pcb-head" }, root);
      el("h3", { class: "el-pcb-title", text: data.board.revision }, head);
      var prov = el("p", { class: "el-pcb-prov" }, head);
      prov.appendChild(document.createTextNode("PCB "));
      var link = el("a", { href: "#provenance", class: "el-pcb-hash", text: data.board.pcb_sha256.slice(0, 8) }, prov);
      link.title = data.board.pcb_sha256;
      ui.faceBadge = el("span", { class: "el-pcb-badge" }, prov);

      var bar = el("div", { class: "el-pcb-toolbar", role: "toolbar" }, root);
      bar.setAttribute("aria-label", "Board viewer controls");
      bar.setAttribute("data-search-exclude", "");

      ui.faceInputs = segment(bar, "Face", "el-pcb-face", [
        { value: "F", label: "Front" }, { value: "B", label: "Back" }
      ], "F", function (v) { setFace(v, true); });

      ui.presetInputs = segment(bar, "View", "el-pcb-preset", [
        { value: "components", label: "Components" },
        { value: "outer", label: "+ outer traces" },
        { value: "internal", label: "Internal copper" }
      ], "components", function (v) { applyPreset(v); });
      ui.custom = el("span", { class: "el-pcb-custom", text: "Custom", hidden: "hidden" },
        ui.presetInputs.wrap);

      ui.innerWrap = segment(bar, "Inner layer", "el-pcb-inner",
        ["In1_Cu", "In2_Cu", "In3_Cu", "In4_Cu", "In5_Cu", "In6_Cu"].map(function (id) {
          return { value: id, label: id.replace("_Cu", "").replace("In", "In ") };
        }), "In1_Cu", function (v) { setInner(v); });
      ui.innerWrap.wrap.hidden = true;

      root.dataset.appearance = state.appearance;
      segment(bar, "Appearance", "el-pcb-appearance", [
        { value: "material", label: "Board materials" },
        { value: "diagram", label: "Engineering colors" }
      ], state.appearance, function (value) {
        state.appearance = value;
        root.dataset.appearance = value;
        if (state.preset !== "custom") applyPreset(state.preset, true);
        else setCaption();
      });
      var refs = el("label", { class: "el-pcb-check" }, bar);
      var refToggle = el("input", { type: "checkbox", name: "el-pcb-references" }, refs);
      refs.classList.add("el-pcb-reference-control");
      el("span", { text: "Assembly references" }, refs);
      refToggle.addEventListener("change", function () {
        root.classList.toggle("el-pcb-show-references", refToggle.checked);
      });
      buildLayerMenu(bar);
      buildButtons(bar);
      ui.legend = el("ul", { class: "el-pcb-legend" }, bar);

      ui.caption = el("p", { class: "el-pcb-caption" }, root);

      var stage = el("div", { class: "el-pcb-stage" }, root);
      var canvas = el("div", {
        class: "el-pcb-canvas", tabindex: "0", role: "group",
        "aria-roledescription": "board viewer",
        "aria-describedby": "el-pcb-keys"
      }, stage);
      ui.canvas = canvas;

      var frame = data.board.frame;
      ui.svg = svg("svg", {
        class: "el-pcb-svg", preserveAspectRatio: "xMidYMid meet",
        "aria-hidden": "true", focusable: "false"
      }, canvas);
      var defs = svg("defs", {}, ui.svg);
      [["el-pcb-metal", [["0%", "#646e79"], ["24%", "#dce2e8"], ["43%", "#ffffff"], ["52%", "#a7b1bd"], ["100%", "#e6ebef"]]],
       ["el-pcb-shield", [["0%", "#707983"], ["35%", "#cbd0d5"], ["48%", "#edf0f2"], ["100%", "#929ca6"]]]].forEach(function (spec) {
        var grad=svg("linearGradient", {id:spec[0], x1:"0%", y1:"0%", x2:"100%", y2:"65%"}, defs);
        spec[1].forEach(function (stop) {svg("stop", {offset:stop[0], "stop-color":stop[1]}, grad);});
      });
      ui.mirror = svg("g", { class: "el-pcb-mirror" }, ui.svg);
      var board = svg("g", { class: "el-pcb-board" }, ui.mirror);
      svg("path", { class: "el-pcb-silhouette", d: frame.silhouette_path }, board);
      ui.layers = svg("g", { class: "el-pcb-layers" }, ui.mirror);
      ui.synth = svg("g", { class: "el-pcb-synth" }, ui.mirror);
      ui.path = svg("g", { class: "el-pcb-path", hidden: "hidden" }, ui.mirror);
      ui.hitG = svg("g", { class: "el-pcb-hits" }, ui.mirror);
      ui.rings = svg("g", { class: "el-pcb-rings" }, ui.mirror);

      data.board.layers.forEach(function (l) {
        svg("g", { class: "el-pcb-layer", "data-layer": l.id, style: "display:none" }, ui.layers);
      });
      ui.bodies = svg("g", { class: "el-pcb-bodies" }, ui.mirror);
      ui.mirror.insertBefore(ui.bodies, ui.path);
      buildSynthetic();
      buildHits();

      ui.tip = el("div", {
        id: "el-pcb-tip", class: "el-pcb-tip", role: "dialog",
        "aria-label": "Part summary", "aria-modal": "false", hidden: "hidden"
      }, canvas);
      ui.status = el("p", { id: "el-pcb-status", class: "el-pcb-status", role: "status" }, canvas);
      ui.status.setAttribute("aria-live", "polite");
      el("p", {
        id: "el-pcb-keys", class: "el-pcb-visually-hidden",
        text: "Board viewer. Arrow keys pan, plus and minus zoom, zero fits the board, " +
              "f flips to the other face. Use the search box below to find a part by name. " +
              "Selecting a part opens a summary with a button that jumps to its row in the parts list."
      }, canvas);

      var side = el("div", { class: "el-pcb-side" }, stage);
      buildFinder(side);
      ui.detail = el("section", { class: "el-pcb-detail", id: "el-pcb-detail" }, side);
      ui.detail.setAttribute("aria-labelledby", "el-pcb-detail-title");
      ui.detail.setAttribute("data-search-exclude", "");
      clearDetail();

      pz = new PanZoom(ui.svg, frame.fit.slice(), { reduced: reduced });
      pz.frameNode = ui.hitG;
      pz.onApply = repositionTip;
      hits = new HitIndex(data.board.components);
      store = new LayerStore(base, ui.layers, null);
      var loadLayer = store.load.bind(store);
      store.load = function (layer) {
        return loadLayer(layer).then(function (group) {
          if (/_Fab$/.test(layer.id) && !group.dataset.materialPrepared) {
            prepareBodies(group, layer.side || layer.id.charAt(0));
            group.dataset.materialPrepared = "true";
          }
          return group;
        });
      };

      wirePointer(canvas);
      wireKeys(canvas);
      wireResize(canvas);
      enhanceBOM();
      enhanceRefs(document);
      if (schRoot) buildSchematic(schRoot);
      window.addEventListener("hashchange", readHash);
      exposeAPI();
    }

    function segment(parent, label, name, options, initial, onChange) {
      var wrap = el("fieldset", { class: "el-pcb-seg" }, parent);
      el("legend", { text: label }, wrap);
      var inputs = {};
      options.forEach(function (opt) {
        var id = name + "-" + opt.value;
        var lab = el("label", { class: "el-pcb-seg-opt" }, wrap);
        var input = el("input", { type: "radio", name: name, id: id, value: opt.value }, lab);
        if (opt.value === initial) input.checked = true;
        el("span", { text: opt.label }, lab);
        input.addEventListener("change", function () { if (input.checked) onChange(opt.value); });
        inputs[opt.value] = input;
      });
      return { wrap: wrap, inputs: inputs };
    }

    function buildLayerMenu(bar) {
      var details = el("details", { class: "el-pcb-layers-menu" }, bar);
      el("summary", { text: "Layers" }, details);
      var list = el("div", { class: "el-pcb-layer-list" }, details);
      ui.layerInputs = {};
      var groups = [
        ["Outer copper", ["F_Cu", "B_Cu"]],
        ["Inner copper", ["In1_Cu", "In2_Cu", "In3_Cu", "In4_Cu", "In5_Cu", "In6_Cu"]],
        ["Mask openings", ["F_Mask", "B_Mask"]],
        ["Silkscreen", ["F_Silkscreen", "B_Silkscreen"]],
        ["Assembly outlines", ["F_Fab", "B_Fab"]],
        ["Courtyard", ["F_Courtyard", "B_Courtyard"]],
        ["From the board data", ["Lands", "Holes"]],
        ["Outline", ["Edge_Cuts"]]
      ];
      groups.forEach(function (g) {
        var box = el("fieldset", { class: "el-pcb-layer-group" }, list);
        el("legend", { text: g[0] }, box);
        g[1].forEach(function (id) {
          var meta = layerById(id) || synthById(id);
          var lab = el("label", { class: "el-pcb-check" }, box);
          var input = el("input", { type: "checkbox", value: id }, lab);
          el("span", { text: meta.label }, lab);
          if (meta.plain) lab.title = meta.plain;
          input.addEventListener("change", function () {
            toggleLayer(id, input.checked, true);
          });
          ui.layerInputs[id] = input;
        });
      });
    }

    function synthById(id) {
      return data.board.synthetic_layers.filter(function (l) { return l.id === id; })[0];
    }

    function buildButtons(bar) {
      var box = el("div", { class: "el-pcb-buttons" }, bar);
      function button(label, title, fn) {
        var b = el("button", { type: "button", class: "el-pcb-btn", text: label }, box);
        b.title = title;
        b.addEventListener("click", fn);
        return b;
      }
      button("Zoom in", "Zoom in (+)", function () { state.autoFit = false; pz.zoomBy(1 / 1.25); });
      button("Zoom out", "Zoom out (-)", function () { state.autoFit = false; pz.zoomBy(1.25); });
      button("Fit", "Fit the whole board (0)", function () { state.autoFit = true; pz.fit(); });
      ui.flip = button("Flip face", "Show the other face (f)", function () {
        setFace(state.face === "F" ? "B" : "F", true);
      });
      ui.pathBtn = button("Show 24 V path", "Trace the supply from the inlet to each branch", function () {
        showPath(ui.pathBtn.getAttribute("aria-pressed") !== "true");
      });
      ui.pathBtn.setAttribute("aria-pressed", "false");
      ui.lockBtn = button("Lock board for panning", "Let a single finger pan the board instead of scrolling the page",
        function () { setLock(ui.lockBtn.getAttribute("aria-pressed") !== "true"); });
      ui.lockBtn.setAttribute("aria-pressed", "false");
      ui.clearBtn = button("Clear selection", "Clear the pinned selection", function () {
        select(null, "cleared");
      });
    }

    function buildSynthetic() {
      var lands = svg("g", { class: "el-pcb-layer", "data-layer": "Lands", style: "display:none" }, ui.synth);
      var holes = svg("g", { class: "el-pcb-layer", "data-layer": "Holes", style: "display:none" }, ui.synth);
      ui.landsF = svg("g", { "data-side": "F" }, lands);
      ui.landsB = svg("g", { "data-side": "B" }, lands);
      data.board.components.forEach(function (c) {
        var target = c.side === "F" ? ui.landsF : ui.landsB;
        c.pads.forEach(function (p) {
          if (p.paste) return;
          var node = padShape(p);
          if (node) target.appendChild(node);
          if (p.drill) {
            var hole = svg("circle", {
              cx: p.xy[0], cy: p.xy[1], r: Math.max(p.drill[0], p.drill[1]) / 2,
              class: p.attr === 3 ? "el-pcb-hole npth" : "el-pcb-hole pth"
            });
            holes.appendChild(hole);
          }
        });
      });
    }

    function padShape(p) {
      var w = p.size[0], h = p.size[1];
      var t = "translate(" + p.xy[0] + " " + p.xy[1] + ") rotate(" + (-p.rot) + ")";
      if (p.shape === 6) {
        return svg("rect", {
          x: p.bbox[0], y: p.bbox[1], width: p.bbox[2], height: p.bbox[3],
          class: "el-pcb-land", "data-approx": "custom"
        });
      }
      if (p.shape === 0) {
        return svg("circle", { cx: p.xy[0], cy: p.xy[1], r: w / 2, class: "el-pcb-land" });
      }
      var r = 0;
      if (p.shape === 2) r = Math.min(w, h) / 2;
      else if (p.shape === 4 || p.shape === 5) r = p.r || 0;
      return svg("rect", {
        x: -w / 2, y: -h / 2, width: w, height: h, rx: r, ry: r,
        transform: t, class: "el-pcb-land"
      });
    }


    // Appearance only: recover closed contours from real fabrication outlines.
    // Never invent a bounding-box body if a contour cannot be resolved.
    function prepareBodies(group, side) {
      var seen = {};
      group.querySelectorAll(".stroked-text[data-ref]").forEach(function (label) {
        var ref = label.dataset.ref;
        if (seen[ref]) label.classList.add("el-pcb-duplicate-reference");
        seen[ref] = true;
      });
      var contours = [], edges = [], graph = {};
      function key(pt) { return pt.map(function (x) { return x.toFixed(4); }).join(","); }
      group.querySelectorAll("path").forEach(function (path) {
        if (path.closest(".stroked-text")) return;
        var d = path.getAttribute("d") || "";
        if (/[a-kno-wy]/i.test(d.replace(/[MLZ]/g, ""))) return;
        var nums = d.match(/[-+]?(?:\d*\.)?\d+/g) || [];
        var points = [];
        for (var i=0; i+1<nums.length; i+=2) points.push([+nums[i], +nums[i+1]]);
        if (points.length < 2) return;
        if (/Z/i.test(d) || (points.length > 2 && key(points[0]) === key(points[points.length-1]))) {
          contours.push(points); return;
        }
        if (points.length !== 2) return;
        var index = edges.length; edges.push(points);
        points.forEach(function (pt) { var k=key(pt); (graph[k] || (graph[k]=[])).push(index); });
      });
      var used = {};
      edges.forEach(function (edge, start) {
        if (used[start]) return;
        var points=[edge[0]], current=start, pt=edge[1], chain=[start], closed=false;
        while (chain.length <= edges.length) {
          points.push(pt);
          if (key(pt) === key(points[0])) { closed=true; break; }
          var links=graph[key(pt)] || [];
          if (links.length !== 2) break;
          var next=links[0] === current ? links[1] : links[0];
          if (chain.indexOf(next) >= 0 || used[next]) break;
          chain.push(next); current=next;
          var pair=edges[next]; pt=key(pair[0]) === key(pt) ? pair[1] : pair[0];
        }
        chain.forEach(function (i) { used[i]=true; });
        if (closed && points.length>3) contours.push(points);
      });
      var bodies = {};
      contours.forEach(function (points) {
        var xs=points.map(function (p) {return p[0];}), ys=points.map(function (p) {return p[1];});
        var x=Math.min.apply(null,xs), y=Math.min.apply(null,ys);
        var w=Math.max.apply(null,xs)-x, h=Math.max.apply(null,ys)-y;
        if (w<.15 || h<.15) return;
        var candidates=data.board.components.filter(function (c) {
          var b=c.bbox;
          return c.side===side && !c.feature && x>=b[0]-.03 && y>=b[1]-.03 &&
            x+w<=b[0]+b[2]+.03 && y+h<=b[1]+b[3]+.03;
        }).sort(function (a,b) {
          return Math.hypot(a.xy[0]-x-w/2,a.xy[1]-y-h/2)-Math.hypot(b.xy[0]-x-w/2,b.xy[1]-y-h/2);
        });
        if (!candidates.length) return;
        var c=candidates[0];
        if (!bodies[c.ref] || w*h>bodies[c.ref].area) bodies[c.ref]={c:c,points:points,area:w*h};
      });
      var face = svg("g", { "data-side": side }, ui.bodies);
      // U1 outline is on User.Eco2, not F.Fab, in native revision cbb8d9fc.
      // 18 x 25.5 mm body; 6 mm antenna section. No invented antenna trace geometry.
      var module=data.board.components.find(function(c) {return c.ref==="U1" && c.mpn==="ESP32-C6-WROOM-1-N8";});
      var moduleRevision = "cbb8d9fc060c7f2b3e6b27b096a5728e789e816102ddba393c69e91020144abb";
      if (side==="F" && data.board.pcb_sha256===moduleRevision && module && module.xy[0]===100 && module.xy[1]===72.6) {
        var mod=svg("g", {class:"el-pcb-module", "data-ref":"U1"}, face);
        svg("rect", {x:91,y:56.85,width:18,height:25.5,rx:.12,fill:"#18241e",stroke:"#626b5c","stroke-width":.12},mod);
        svg("rect", {x:91.25,y:63.1,width:17.5,height:19,rx:.4,fill:"url(#el-pcb-shield)",stroke:"#68737b","stroke-width":.16},mod);
        svg("text", {x:100,y:75,"text-anchor":"middle","font-size":1.1,fill:"#354047",text:"ESP32-C6"},mod);
        svg("text", {x:100,y:60.4,"text-anchor":"middle","font-size":.8,fill:"#b5b9a4",text:"ANTENNA"},mod);
        svg("title", {text:"U1: native mechanical outline and antenna extent; shield finish is illustrative, not a 3D model"},mod);
      }
      Object.keys(bodies).forEach(function (ref) {
        var b=bodies[ref], family=(ref.match(/^[A-Za-z]+/) || [""])[0];
        var material=family==="C" ? "ceramic" : family==="J" ? "connector" : family==="L" ? "inductor" : family==="F" ? "fuse" : "package";
        var node=svg("path", { d:"M"+b.points.map(function (p) {return p.join(",");}).join(" L")+" Z",
          class:"el-pcb-body el-pcb-body-"+material, "data-ref":ref }, face);
        svg("title", {text:ref+": footprint outline with illustrative material color; not a 3D model"}, node);
      });
    }

    function buildHits() {
      data.board.components.forEach(function (c) {
        var g = svg("g", {
          class: "el-pcb-hit", "data-ref": c.ref, "data-side": c.side,
          "data-through": c.through ? "1" : null
        }, ui.hitG);
        svg("rect", {
          x: c.bbox[0], y: c.bbox[1], width: c.bbox[2], height: c.bbox[3]
        }, g);
      });
    }

    /* -------------------------------------------------------- layer state */
    function zOf(layer, face) {
      if (!layer.side) return layer.z;
      return Z_BASE[layer.kind] + (layer.side === face ? 0.5 : -0.5);
    }

    function reorder() {
      var order = data.board.layers.slice().sort(function (a, b) {
        return zOf(a, state.face) - zOf(b, state.face);
      });
      order.forEach(function (l) {
        var g = ui.layers.querySelector('[data-layer="' + l.id + '"]');
        if (g) ui.layers.appendChild(g);
      });
    }

    function setVisible(id, on) {
      var g = ui.layers.querySelector('[data-layer="' + id + '"]') ||
              ui.synth.querySelector('[data-layer="' + id + '"]');
      if (g) g.style.display = on ? "" : "none";
      state.layers[id] = on;
      if (ui.layerInputs[id]) ui.layerInputs[id].checked = on;
    }

    function toggleLayer(id, on, manual) {
      if (manual) markCustom();
      if (!on) { setVisible(id, false); updateLegend(); return Promise.resolve(); }
      var meta = layerById(id);
      if (!meta) { setVisible(id, true); updateLegend(); return Promise.resolve(); }
      return store.load(meta).then(function () {
        setVisible(id, true);
        updateLegend();
      }).catch(function (err) {
        if (ui.layerInputs[id]) ui.layerInputs[id].checked = false;
        state.layers[id] = false;
        layerError(id, meta);
        if (window.console && console.warn) console.warn("[pcb] layer " + id + ": " + err.message);
      });
    }

    function layerError(id, meta) {
      var box = ui.layerInputs[id] ? ui.layerInputs[id].closest("label") : null;
      if (!box || box.querySelector(".el-pcb-retry")) return;
      var retry = el("button", { type: "button", class: "el-pcb-retry", text: "Retry" }, box);
      retry.addEventListener("click", function (e) {
        e.preventDefault();
        retry.remove();
        toggleLayer(id, true, false);
      });
      say(meta.label + " could not be loaded. Use Retry to try again.");
    }

    function markCustom() {
      state.preset = "custom";
      root.dataset.preset = "custom";
      Object.keys(ui.presetInputs.inputs).forEach(function (k) {
        ui.presetInputs.inputs[k].checked = false;
      });
      ui.custom.hidden = false;
      ui.innerWrap.wrap.hidden = true;
      setCaption();
    }

    function presetLayers(name, face) {
      var f = face === "F" ? "F" : "B";
      if (name === "components") {
        return ["Edge_Cuts", f + "_Fab", "Lands", "Holes"].concat(state.appearance === "material" ? [f + "_Silkscreen"] : []);
      }
      if (name === "outer") {
        return ["Edge_Cuts", f + "_Fab", "Lands", "Holes", f + "_Cu"].concat(state.appearance === "material" ? [f + "_Silkscreen"] : []);
      }
      return ["Edge_Cuts", "Holes", "Lands", state.inner];
    }

    function applyPreset(name, quiet) {
      state.preset = name;
      root.dataset.preset = name;
      ui.custom.hidden = true;
      if (ui.presetInputs.inputs[name]) ui.presetInputs.inputs[name].checked = true;
      ui.innerWrap.wrap.hidden = name !== "internal";
      var want = presetLayers(name, state.face);
      var all = data.board.layers.map(function (l) { return l.id; }).concat(["Lands", "Holes"]);
      all.forEach(function (id) { if (want.indexOf(id) < 0) setVisible(id, false); });
      var jobs = want.map(function (id) { return toggleLayer(id, true, false); });
      reorder();
      setCaption();
      if (!quiet) say(captionFor(name));
      return Promise.all(jobs).then(updateLegend);
    }

    function setInner(id) {
      state.inner = id;
      if (state.preset === "internal") applyPreset("internal");
    }

    function captionFor(name) {
      if (name === "components") {
        return "Assembly-outline view: real positions, body outlines and land shapes from the board's own " +
               "data. Select a component to read its reference and explanation.";
      }
      if (name === "outer") {
        return "The same outlines with the " + faceWord(state.face) +
               " copper layer underneath, so you can see where each part's traces run.";
      }
      if (name === "internal") {
        var meta = layerById(state.inner);
        return "Inner layer " + meta.label + " — " + meta.plain +
               ". A layer's purpose is a guide, not proof that every shape on it belongs to one net. " +
               "The voids are real; the colours are view colours, not the colour of copper.";
      }
      return "Custom layer selection.";
    }

    function setCaption() {
      ui.caption.textContent = captionFor(state.preset) + (state.appearance === "material" ?
        " Board materials: black substrate, white production silkscreen, silver-colored lands and colored footprint bodies. Materials are illustrative, not a photograph or 3D model. Outer traces are shown through the mask for learning." :
        " Engineering colors retain the layer palette. Assembly references are optional; duplicate references are suppressed.");
    }

    function updateLegend() {
      ui.legend.innerHTML = "";
      var ids = Object.keys(state.layers).filter(function (id) { return state.layers[id]; });
      ids.sort(function (a, b) {
        var la = layerById(a), lb = layerById(b);
        return (la ? zOf(la, state.face) : 20) - (lb ? zOf(lb, state.face) : 20);
      });
      ids.forEach(function (id) {
        var meta = layerById(id) || synthById(id);
        var li = el("li", { class: "el-pcb-chip", "data-layer": id }, ui.legend);
        svg("svg", { class: "el-pcb-swatch", viewBox: "0 0 10 10", "aria-hidden": "true" }, li)
          .appendChild(svg("rect", { x: 0, y: 0, width: 10, height: 10 }));
        el("span", { text: meta.label }, li);
      });
    }

    /* ---------------------------------------------------------- face flip */
    function setFace(face, announce) {
      if (state.face === face) return;
      state.face = face;
      root.dataset.face = face;
      ui.mirror.setAttribute("transform", face === "B" ? "matrix(-1 0 0 1 200 0)" : "");
      ui.faceInputs.inputs[face].checked = true;
      ui.faceBadge.textContent = "viewing the " + faceWord(face) + " face";
      ui.canvas.setAttribute("aria-label", data.board.revision + ", " + faceWord(face) + " face");
      ui.landsF.style.display = face === "F" ? "" : "none";
      ui.landsB.style.display = face === "B" ? "" : "none";
      if (state.preset !== "custom") applyPreset(state.preset, true);
      else reorder();
      drawRings();
      if (state.selected) renderDetail(state.selected);
      if (announce) say("Now viewing the " + faceWord(face) + " face.");
      setCaption();
    }

    /* ----------------------------------------------------- selection etc. */
    function say(message) {
      ui.status.textContent = message;
    }

    function hitBox(ref) {
      var c = data.comp[ref];
      return c ? c.bbox : null;
    }

    function drawRings() {
      ui.rings.innerHTML = "";
      state.group.forEach(function (ref) {
        var box = hitBox(ref);
        if (box && data.comp[ref].side === state.face) ringAt(box, "group");
      });
      if (state.hover && state.hover !== state.selected) {
        var hb = hitBox(state.hover);
        if (hb && visibleHere(state.hover)) ringAt(hb, "hover");
      }
      if (state.selected) {
        var sb = hitBox(state.selected);
        if (sb && visibleHere(state.selected)) ringAt(sb, "selected");
      }
    }

    function visibleHere(ref) {
      var c = data.comp[ref];
      return c && (c.side === state.face || c.through);
    }

    function ringAt(box, kind) {
      svg("rect", {
        x: box[0], y: box[1], width: box[2], height: box[3],
        class: "el-pcb-ring " + kind
      }, ui.rings);
    }

    /* The tooltip is the primary way to inspect a part, on every input device.
       Hovering opens it; clicking or tapping pins it so its buttons can be
       reached -- which is what makes this work on a phone, where there is no
       hover and where jumping straight to the parts list would throw the
       reader down the page. */
    function setHover(ref, clientPoint) {
      state.hover = ref;
      drawRings();
      if (state.tipPinned) return;          // a pinned summary stays put
      if (!ref) { hideTip(); return; }
      showTip(ref, clientPoint, false);
    }

    function hideTip() {
      ui.tip.hidden = true;
      state.tipRef = null;
      state.tipPinned = false;
    }

    function showTip(ref, clientPoint, pinned) {
      var c = data.comp[ref], t = data.teach.components[ref];
      if (!c || !t) return;
      state.tipRef = ref;
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

      el("strong", { text: ref + " · " + t.name }, ui.tip);
      var meta = [c.value, c.mpn].filter(Boolean).join(" · ");
      if (meta) el("span", { class: "el-pcb-tip-meta", text: meta }, ui.tip);
      el("span", {
        class: "el-pcb-tip-meta",
        text: faceWord(c.side) + " face · sheet " + c.sheet + " " + c.sheet_title
      }, ui.tip);
      el("span", { class: "el-pcb-tip-here", text: "Here: " + firstSentence(t.here) }, ui.tip);
      el("span", { class: "el-pcb-tip-how", text: "How: " + firstSentence(t.how) }, ui.tip);

      if (pinned) {
        var actions = el("div", { class: "el-pcb-tip-actions" }, ui.tip);
        if (c.bom) {
          var bom = el("button", {
            type: "button", class: "el-pcb-btn el-pcb-tip-bom",
            "data-act": "bom", text: "Show in parts list"
          }, actions);
          bom.addEventListener("click", function () { jumpToRow(c.bom); });
        } else {
          el("span", {
            class: "el-pcb-tip-meta el-pcb-tip-nobom",
            text: "made with the PCB — not in the parts list"
          }, actions);
        }
        var sheet = el("button", {
          type: "button", class: "el-pcb-btn el-pcb-tip-sheet",
          "data-act": "sheet", text: "Show on sheet " + c.sheet
        }, actions);
        sheet.addEventListener("click", function () { showOnSheet(ref); });
        var more = el("button", {
          type: "button", class: "el-pcb-btn el-pcb-tip-more",
          "data-act": "detail", text: "Full explanation"
        }, actions);
        more.addEventListener("click", function () {
          ui.detail.scrollIntoView({ block: "nearest", behavior: state.reduced ? "auto" : "smooth" });
          var h = ui.detail.querySelector("h3");
          if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
        });
      }

      ui.tip.hidden = false;
      placeTip(c.bbox, clientPoint);
    }

    function repositionTip() {
      if (ui.tip.hidden || !state.tipRef) return;
      var c = data.comp[state.tipRef];
      if (c) placeTip(c.bbox, null);
    }

    function firstSentence(text) {
      var m = /^(.+?\.)(\s|$)/.exec(text || "");
      return m ? m[1] : (text || "");
    }

    function placeTip(box, clientPoint) {
      var stage = ui.canvas.getBoundingClientRect();
      var tip = ui.tip.getBoundingClientRect();
      var a = pz.toScreen(box[0], box[1]);
      var b = pz.toScreen(box[0] + box[2], box[1] + box[3]);
      if (!a || !b) return;
      var partRect = {
        left: Math.min(a.x, b.x), right: Math.max(a.x, b.x),
        top: Math.min(a.y, b.y), bottom: Math.max(a.y, b.y)
      };
      var gap = 8;
      var candidates = [
        { x: (partRect.left + partRect.right) / 2 - tip.width / 2, y: partRect.top - tip.height - gap },
        { x: (partRect.left + partRect.right) / 2 - tip.width / 2, y: partRect.bottom + gap },
        { x: partRect.right + gap, y: (partRect.top + partRect.bottom) / 2 - tip.height / 2 },
        { x: partRect.left - tip.width - gap, y: (partRect.top + partRect.bottom) / 2 - tip.height / 2 }
      ];
      var chosen = null;
      for (var i = 0; i < candidates.length; i++) {
        var c = candidates[i];
        var fits = c.x >= stage.left + 2 && c.x + tip.width <= stage.right - 2 &&
                   c.y >= stage.top + 2 && c.y + tip.height <= stage.bottom - 2;
        var overlaps = !(c.x + tip.width < partRect.left || c.x > partRect.right ||
                         c.y + tip.height < partRect.top || c.y > partRect.bottom);
        if (fits && !overlaps) { chosen = c; break; }
      }
      if (!chosen) {
        chosen = {
          x: Math.min(Math.max((clientPoint ? clientPoint.x : partRect.left) + gap, stage.left + 2),
                      stage.right - tip.width - 2),
          y: Math.min(Math.max(partRect.bottom + gap, stage.top + 2), stage.bottom - tip.height - 2)
        };
      }
      ui.tip.style.left = (chosen.x - stage.left) + "px";
      ui.tip.style.top = (chosen.y - stage.top) + "px";
    }

    function select(ref, reason, opts) {
      opts = opts || {};
      if (ref && !data.comp[ref]) { say("There is no part called " + ref + " on this board."); return; }
      state.selected = ref;
      root.dataset.selected = ref || "";
      if (!ref) {
        state.group = [];
        clearDetail();
        hideTip();
        drawRings();
        markBOM(null);
        setHash();
        say("Selection cleared.");
        return;
      }
      var c = data.comp[ref];
      var switched = false;
      if (c.side !== state.face && !c.through) {
        setFace(c.side, false);
        switched = true;
      }
      drawRings();
      renderDetail(ref);
      markBOM(c.bom);
      setHash();
      if (opts.tip !== false) {
        showTip(ref, opts.point || null, true);
        if (opts.focusTip) {
          var first = ui.tip.querySelector("button:not(.el-pcb-tip-close)");
          if (first) first.focus({ preventScroll: true });
        }
      }
      var msg = ref + ", " + data.teach.components[ref].name + ".";
      if (switched) msg += " Switched to the " + faceWord(c.side) + " face to show it.";
      if (c.bom) msg += " Use “Show in parts list” to jump to row " + c.bom + ".";
      if (reason) msg += " " + reason;
      say(msg);
    }

    function locate(ref, zoom) {
      var box = hitBox(ref);
      if (!box) return;
      state.autoFit = false;
      if (zoom) pz.zoomTo(box, 12); else pz.ensureVisible(box);
    }

    function clearDetail() {
      ui.detail.innerHTML = "";
      el("h3", { id: "el-pcb-detail-title", text: "Nothing selected" }, ui.detail);
      el("p", {
        text: "Click any part on the board, or search for one, to read what it does here. " +
              "Hovering shows a summary; selecting keeps it."
      }, ui.detail);
    }

    function renderDetail(ref) {
      var c = data.comp[ref], t = data.teach.components[ref];
      ui.detail.innerHTML = "";
      el("h3", { id: "el-pcb-detail-title", text: ref + " · " + t.name }, ui.detail);

      var meta = el("dl", { class: "el-pcb-meta" }, ui.detail);
      function row(k, v) {
        if (!v) return;
        el("dt", { text: k }, meta);
        var dd = el("dd", {}, meta);
        if (typeof v === "string") dd.textContent = v; else dd.appendChild(v);
      }
      row("Face", faceWord(c.side) + (c.through ? " (its holes go right through)" : ""));
      row("Value", c.value);
      row("Part number", c.mpn && c.mpn !== "PCB FEATURE" ? c.mpn : null);
      row("Manufacturer", c.mfr && c.mfr !== "PCB" ? c.mfr : null);
      row("Package", c.pkg);
      var sheetBtn = el("button", {
        type: "button", class: "el-pcb-link",
        text: "sheet " + c.sheet + " · " + c.sheet_title
      });
      sheetBtn.addEventListener("click", function () { showOnSheet(ref); });
      row("Schematic", sheetBtn);
      if (c.bom) {
        var bomBtn = el("button", { type: "button", class: "el-pcb-link", text: "parts list row " + c.bom });
        bomBtn.addEventListener("click", function () { jumpToRow(c.bom); });
        row("Parts list", bomBtn);
      } else {
        row("Parts list", "not purchased — this feature is made with the PCB itself");
      }

      el("h4", { text: "What it does here" }, ui.detail);
      el("p", { text: t.here }, ui.detail);
      el("h4", { text: "How it works" }, ui.detail);
      el("p", { text: t.how }, ui.detail);

      if (t.nets && t.nets.length) {
        el("h4", { text: "Pins and nets" }, ui.detail);
        var wrap = el("div", { class: "el-pcb-scroll" }, ui.detail);
        var table = el("table", { class: "el-pcb-table el-pcb-pins" }, wrap);
        table.innerHTML = "<thead><tr><th>Pin</th><th>Net</th></tr></thead>";
        var tbody = el("tbody", {}, table);
        var seen = {};
        t.nets.forEach(function (n) {
          var key = n.pin + "|" + (n.net || "");
          if (seen[key]) { seen[key].count += 1; seen[key].cell.textContent = n.net || "no connect (intentional)"; return; }
          var tr = el("tr", {}, tbody);
          el("td", { text: n.pin || "(mechanical)" }, tr);
          var td = el("td", { text: n.net || "no connect (intentional)" }, tr);
          if (!n.net) td.className = "el-pcb-nc";
          seen[key] = { count: 1, cell: td };
        });
      }

      if (t.claims && t.claims.length) {
        el("h4", { text: "What is known" }, ui.detail);
        var ul = el("ul", { class: "el-pcb-claims" }, ui.detail);
        t.claims.forEach(function (cl) {
          var li = el("li", {}, ul);
          el("span", { class: "el-pcb-tag kind-" + cl.kind, text: cl.kind }, li);
          el("span", { class: "el-pcb-tag ev", text: cl.evidence }, li);
          el("span", { text: " " + cl.text }, li);
          var basis = cl.basis + (cl.bound_to ? " (bound to board " + cl.bound_to + ")" : "");
          el("span", { class: "el-pcb-basis", text: basis }, li);
        });
      }

      if (t.open && t.open.length) {
        el("h4", { text: "Still open" }, ui.detail);
        var ol = el("ul", { class: "el-pcb-open" }, ui.detail);
        t.open.forEach(function (o) { el("li", { text: o }, ol); });
      }

      if (t.inspect) {
        el("h4", { text: "When boards arrive" }, ui.detail);
        el("p", { text: t.inspect }, ui.detail);
      }

      if (t.assembly && t.assembly.length) {
        el("h4", { text: "Assembly notes" }, ui.detail);
        var al = el("ul", {}, ui.detail);
        t.assembly.forEach(function (a) { el("li", { text: a }, al); });
        if (c.assembly_note) el("li", { text: c.assembly_note }, al);
      } else if (c.assembly_note && c.bom) {
        el("h4", { text: "Assembly note" }, ui.detail);
        el("p", { text: c.assembly_note }, ui.detail);
      }

      var updates = (data.bom.note_updates || []).filter(function (u) {
        return u.refs.indexOf(ref) >= 0;
      });
      updates.forEach(function (u) {
        var p = el("p", { class: "el-pcb-note-update" }, ui.detail);
        p.textContent = u.text;
      });

      if (t.related && t.related.length) {
        el("h4", { text: "Related parts" }, ui.detail);
        var rel = el("p", { class: "el-pcb-related" }, ui.detail);
        t.related.slice().sort(byRef).forEach(function (r) {
          var b = el("button", { type: "button", class: "el-pcb-ref", text: r }, rel);
          b.addEventListener("click", function () { select(r); locate(r, false); });
        });
      }

      if (t.sources && t.sources.length) {
        el("h4", { text: "Sources" }, ui.detail);
        var sl = el("ul", { class: "el-pcb-sources" }, ui.detail);
        t.sources.forEach(function (s) {
          var li = el("li", {}, sl);
          var a = el("a", { href: s.url, text: s.label }, li);
          a.rel = "noopener";
          if (s.context) el("span", { class: "el-pcb-basis", text: s.context }, li);
        });
      }

      if (c.side !== state.face && !c.through) {
        var notice = el("p", { class: "el-pcb-notice" }, ui.detail);
        notice.textContent = ref + " is on the " + faceWord(c.side) + " face. ";
        var b = el("button", {
          type: "button", class: "el-pcb-btn",
          text: "Show the " + faceWord(c.side) + " face"
        }, notice);
        b.addEventListener("click", function () { setFace(c.side, true); renderDetail(ref); });
      }

      var prov = el("details", { class: "el-pcb-provenance" }, ui.detail);
      el("summary", { text: "Provenance" }, prov);
      el("p", {
        text: "Footprint " + c.uuid.fp + " · symbol " + c.uuid.sch +
              ". Position " + c.xy[0] + ", " + c.xy[1] + " mm, rotation " + c.rot + "°."
      }, prov);
    }

    /* -------------------------------------------------------- 24 V path */
    var PATH_STEPS = [
      ["J1", "the inlet"], ["F1", "backup fuse"], ["Q500", "reverse blocking"],
      ["U12", "the electronic breaker"], ["C504", "the protected bus"]
    ];
    var PATH_BRANCHES = [
      ["F2", "J12"], ["F3", "J13"], ["F4", "J2"], ["F5", "J3"], ["F6", "J4"],
      ["F7", "J5"], ["F8", "J6"], ["F9", "J7"], ["F10", "J8"], ["F11", "U10"]
    ];

    function centre(ref) {
      var b = hitBox(ref);
      return b ? [b[0] + b[2] / 2, b[1] + b[3] / 2] : null;
    }

    function showPath(on) {
      ui.pathBtn.setAttribute("aria-pressed", on ? "true" : "false");
      ui.path.hidden = !on;
      ui.path.innerHTML = "";
      if (!on) { say("Supply path hidden."); return; }
      var chain = PATH_STEPS.map(function (s) { return s[0]; });
      polyline(chain);
      PATH_BRANCHES.forEach(function (b) { polyline(["C504", b[0], b[1]]); });
      polyline(["U12", "U14"]);
      ["U14", "U7"].forEach(function () {});
      polyline(["U14", "U7"]); polyline(["U14", "U8"]); polyline(["U14", "U9"]);
      polyline(["U10", "U11"]);
      say("Showing the supply path from the inlet through the breaker to every branch. " +
          "This is an explanation, not a live electrical measurement.");
    }

    function polyline(refs) {
      var pts = refs.map(centre).filter(Boolean);
      if (pts.length < 2) return;
      svg("polyline", {
        points: pts.map(function (p) { return p[0] + "," + p[1]; }).join(" "),
        class: "el-pcb-flow"
      }, ui.path);
    }

    /* ------------------------------------------------------------ finder */
    function buildFinder(side) {
      var wrap = el("div", { class: "el-pcb-finder" }, side);
      wrap.setAttribute("data-search-exclude", "");
      var id = "el-pcb-search";
      el("label", { for: id, text: "Find a part" }, wrap);
      var input = el("input", {
        type: "search", id: id, class: "el-pcb-search", role: "combobox",
        "aria-expanded": "false", "aria-controls": "el-pcb-list", "aria-autocomplete": "list",
        placeholder: "reference, name, value, part number or net"
      }, wrap);
      var list = el("ul", { id: "el-pcb-list", class: "el-pcb-list", role: "listbox" }, wrap);
      list.setAttribute("aria-label", "Parts on this board");
      ui.search = input;
      ui.list = list;

      data.board.components.slice().sort(function (a, b) { return byRef(a.ref, b.ref); })
        .forEach(function (c) {
          var t = data.teach.components[c.ref];
          var li = el("li", {
            role: "option", id: "el-pcb-opt-" + c.ref, "data-ref": c.ref,
            class: "el-pcb-option"
          }, list);
          li.setAttribute("aria-selected", "false");
          el("span", { class: "el-pcb-option-ref", text: c.ref }, li);
          el("span", { class: "el-pcb-option-name", text: t.name }, li);
          li.dataset.haystack = [
            c.ref, t.name, c.value, c.mpn, c.pkg, c.sheet_title,
            Object.keys(c.pins).map(function (k) { return c.pins[k]; }).join(" ")
          ].join(" ").toLowerCase();
          li.addEventListener("mousedown", function (e) { e.preventDefault(); });
          li.addEventListener("click", function () {
            select(c.ref); locate(c.ref, true); closeList();
          });
        });

      input.addEventListener("input", function () { filterList(input.value); });
      input.addEventListener("focus", function () { filterList(input.value); });
      input.addEventListener("blur", function () { setTimeout(closeList, 120); });
      input.addEventListener("keydown", function (e) {
        var visible = visibleOptions();
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          if (!visible.length) return;
          var i = visible.indexOf(ui.active);
          i = e.key === "ArrowDown" ? Math.min(visible.length - 1, i + 1) : Math.max(0, i - 1);
          setActive(visible[i]);
        } else if (e.key === "Home" && visible.length) {
          e.preventDefault(); setActive(visible[0]);
        } else if (e.key === "End" && visible.length) {
          e.preventDefault(); setActive(visible[visible.length - 1]);
        } else if (e.key === "Enter") {
          if (ui.active) {
            e.preventDefault();
            var ref = ui.active.dataset.ref;
            select(ref, null, { focusTip: true }); locate(ref, true); closeList();
          }
        } else if (e.key === "Escape") {
          if (!ui.list.classList.contains("is-open")) return;
          e.preventDefault(); e.stopPropagation(); closeList();
        }
      });
    }

    function visibleOptions() {
      return Array.prototype.filter.call(ui.list.children, function (li) { return !li.hidden; });
    }

    function filterList(query) {
      var q = (query || "").trim().toLowerCase();
      var shown = 0;
      Array.prototype.forEach.call(ui.list.children, function (li) {
        var match = !q || li.dataset.haystack.indexOf(q) >= 0;
        li.hidden = !match;
        if (match) shown += 1;
      });
      ui.list.classList.add("is-open");
      ui.search.setAttribute("aria-expanded", "true");
      if (ui.active && ui.active.hidden) setActive(null);
      if (q && shown === 0) say("No part matches " + query + ".");
    }

    function setActive(li) {
      if (ui.active) ui.active.classList.remove("is-active");
      ui.active = li || null;
      if (!li) { ui.search.removeAttribute("aria-activedescendant"); setHover(null); return; }
      li.classList.add("is-active");
      ui.search.setAttribute("aria-activedescendant", li.id);
      li.scrollIntoView({ block: "nearest" });
      var ref = li.dataset.ref;
      var c = data.comp[ref];
      if (c.side !== state.face && !c.through) {
        // Browsing the list does not flip the board; committing to a part does.
        say(ref + " is on the " + faceWord(c.side) + " face. Press Enter to show it.");
        setHover(null);
        return;
      }
      locate(ref, false);
      setHover(ref, null);
    }

    function closeList() {
      ui.list.classList.remove("is-open");
      ui.search.setAttribute("aria-expanded", "false");
      setActive(null);
    }

    /* --------------------------------------------------------------- BOM */
    function enhanceBOM() {
      var table = document.querySelector('table.el-pcb-table tr[data-item]');
      if (!table) return;
      var rows = document.querySelectorAll("tr[data-item]");
      var container = rows[0].closest(".el-pcb-scroll");
      ui.bomScroll = container;

      var tools = el("div", { class: "el-pcb-bom-tools" });
      container.parentNode.insertBefore(tools, container);
      var summary = el("p", { class: "el-pcb-bom-summary" }, tools);
      summary.textContent = data.bom.totals.per_board + " purchased packages per board · " +
        data.bom.totals.rows + " rows · " + data.bom.totals.features +
        " board features that are not purchased";
      var filterId = "el-pcb-bom-filter";
      el("label", { for: filterId, text: "Filter rows" }, tools);
      var filter = el("input", { type: "search", id: filterId, class: "el-pcb-search" }, tools);
      filter.addEventListener("input", function () {
        var q = filter.value.trim().toLowerCase();
        Array.prototype.forEach.call(rows, function (tr) {
          tr.hidden = !!q && tr.textContent.toLowerCase().indexOf(q) < 0;
        });
      });

      Array.prototype.forEach.call(rows, function (tr) {
        var item = parseInt(tr.dataset.item, 10);
        var cell = tr.cells[1];
        var locateBtn = el("button", {
          type: "button", class: "el-pcb-btn el-pcb-locate", text: "Locate all",
          "data-locate": String(item)
        });
        cell.appendChild(document.createTextNode(" "));
        cell.appendChild(locateBtn);
        locateBtn.addEventListener("click", function () { locateRow(item); });
      });
    }

    function locateRow(item) {
      var row = data.rowByItem[item];
      if (!row) return;
      state.group = row.refs.slice();
      var front = row.refs.filter(function (r) { return data.comp[r].side === "F"; }).length;
      drawRings();
      say(row.refs.length + " place" + (row.refs.length === 1 ? "" : "s") + " on the board: " +
          front + " front, " + (row.refs.length - front) + " back.");
      ui.detail.innerHTML = "";
      el("h3", { id: "el-pcb-detail-title", text: "Row " + item + " · " + row.value }, ui.detail);
      el("p", { text: row.mpn + " — fitted in " + row.refs.length + " place" +
                      (row.refs.length === 1 ? "" : "s") + ". Choose one:" }, ui.detail);
      var box = el("p", { class: "el-pcb-related" }, ui.detail);
      row.refs.slice().sort(byRef).forEach(function (r) {
        var b = el("button", { type: "button", class: "el-pcb-ref", text: r }, box);
        b.addEventListener("click", function () { select(r); locate(r, true); });
      });
      markBOM(item);
    }

    function markBOM(item) {
      var rows = document.querySelectorAll("tr[data-item]");
      Array.prototype.forEach.call(rows, function (tr) {
        var on = item !== null && parseInt(tr.dataset.item, 10) === item;
        if (on) {
          tr.setAttribute("aria-current", "true");
          if (!tr.querySelector(".el-pcb-rowmark")) {
            el("span", { class: "el-pcb-rowmark", text: "selected" }, tr.cells[0]);
          }
          // Deliberately no scrollIntoView: selecting a part must never move the
          // reader away from the board. The summary's button does that on request.
        } else {
          tr.removeAttribute("aria-current");
          var mark = tr.querySelector(".el-pcb-rowmark");
          if (mark) mark.remove();
        }
      });
    }

    function jumpToRow(item) {
      var tr = document.querySelector('tr[data-item="' + item + '"]');
      if (!tr) return;
      markBOM(item);
      tr.scrollIntoView({ block: "center", behavior: state.reduced ? "auto" : "smooth" });
      var first = tr.querySelector(".el-pcb-ref");
      if (first) { first.setAttribute("tabindex", "-1"); first.focus({ preventScroll: true }); }
      say("Moved to parts list row " + item + ".");
    }

    function enhanceRefs(scope) {
      var spans = scope.querySelectorAll("span.el-pcb-ref[data-pcb-ref]");
      Array.prototype.forEach.call(spans, function (span) {
        if (span.dataset.upgraded) return;
        span.dataset.upgraded = "1";
        var ref = span.dataset.pcbRef;
        if (!data.comp[ref]) return;
        var b = el("button", { type: "button", class: "el-pcb-ref", text: ref });
        b.dataset.pcbRef = ref;
        b.title = data.teach.components[ref].name;
        b.addEventListener("click", function () {
          select(ref); locate(ref, true);
          root.scrollIntoView({ block: "start", behavior: state.reduced ? "auto" : "smooth" });
        });
        span.parentNode.replaceChild(b, span);
      });
      var links = scope.querySelectorAll("a[data-pcb-ref]");
      Array.prototype.forEach.call(links, function (a) {
        if (a.dataset.upgraded) return;
        a.dataset.upgraded = "1";
        a.addEventListener("click", function (e) {
          var ref = a.dataset.pcbRef;
          if (!data.comp[ref]) return;
          e.preventDefault();
          select(ref); locate(ref, true);
          root.scrollIntoView({ block: "start", behavior: state.reduced ? "auto" : "smooth" });
        });
      });
    }

    /* -------------------------------------------------------- interaction */
    function wirePointer(canvas) {
      var dragging = false, moved = false, last = null, pointers = {}, pinch = null;

      canvas.addEventListener("pointerdown", function (e) {
        if (inTip(e)) return;             // the summary sits over the board
        pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        var ids = Object.keys(pointers);
        if (ids.length === 2) {
          pinch = pinchState(pointers, ids);
          dragging = false;
          return;
        }
        dragging = true; moved = false; last = { x: e.clientX, y: e.clientY };
        canvas.setPointerCapture(e.pointerId);
      });

      canvas.addEventListener("pointermove", function (e) {
        if (inTip(e) && !dragging) return;
        if (pointers[e.pointerId]) { pointers[e.pointerId] = { x: e.clientX, y: e.clientY }; }
        var ids = Object.keys(pointers);
        if (ids.length === 2 && pinch) {
          var now = pinchState(pointers, ids);
          var factor = pinch.dist / now.dist;
          state.autoFit = false;
          pz.zoomAt(factor, now.cx, now.cy);
          pinch = now;
          if (!state.tipPinned) hideTip();
          return;
        }
        if (dragging) {
          var dx = e.clientX - last.x, dy = e.clientY - last.y;
          if (Math.abs(dx) > 5 || Math.abs(dy) > 5) moved = true;
          if (moved) {
            var box = canvas.getBoundingClientRect();
            var v = pz.view;
            state.autoFit = false;
            pz.panBy(-dx * v.w / box.width, -dy * v.h / box.height);
            if (!state.tipPinned) hideTip();
          }
          last = { x: e.clientX, y: e.clientY };
          return;
        }
        if (e.pointerType === "touch") return;
        var p = pz.toWorld(e.clientX, e.clientY);
        if (!p) return;
        var hit = hits.hitTest(p.x, p.y, state.face);
        setHover(hit ? hit.ref : null, { x: e.clientX, y: e.clientY });
      });

      function end(e) {
        var wasDragging = dragging, wasMoved = moved;
        delete pointers[e.pointerId];
        if (Object.keys(pointers).length < 2) pinch = null;
        dragging = false;
        if (!wasDragging || wasMoved) return;
        var p = pz.toWorld(e.clientX, e.clientY);
        if (!p) return;
        var hit = hits.hitTest(p.x, p.y, state.face);
        if (!hit && e.pointerType === "touch") {
          var box = canvas.getBoundingClientRect();
          var mmPerPx = pz.view.w / box.width;
          hit = hits.nearest(p.x, p.y, state.face, TAP_SLOP * mmPerPx);
        }
        if (hit) {
          select(hit.ref, null, { point: { x: e.clientX, y: e.clientY } });
          canvas.focus({ preventScroll: true });
        } else {
          hideTip();
          state.hover = null;
          drawRings();
        }
      }

      function inTip(e) {
        return !!(e.target && e.target.closest && e.target.closest(".el-pcb-tip"));
      }
      canvas.addEventListener("pointerup", end);
      canvas.addEventListener("pointercancel", function (e) {
        delete pointers[e.pointerId]; pinch = null; dragging = false;
      });
      canvas.addEventListener("pointerleave", function () {
        if (!dragging) setHover(null);
      });

      canvas.addEventListener("wheel", function (e) {
        e.preventDefault();
        state.autoFit = false;
        var step = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
        pz.zoomAt(step > 0 ? 1.12 : 1 / 1.12, e.clientX, e.clientY);
      }, { passive: false });

      canvas.addEventListener("dblclick", function (e) {
        state.autoFit = false;
        pz.zoomAt(0.5, e.clientX, e.clientY);
      });
    }

    function pinchState(pointers, ids) {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      return {
        dist: Math.max(1, Math.hypot(a.x - b.x, a.y - b.y)),
        cx: (a.x + b.x) / 2, cy: (a.y + b.y) / 2
      };
    }

    function setLock(on) {
      state.lockPan = on;
      ui.lockBtn.setAttribute("aria-pressed", on ? "true" : "false");
      ui.canvas.classList.toggle("is-locked", on);
      say(on ? "One finger now pans the board. Press again to scroll the page normally."
             : "One finger scrolls the page again. Two fingers still pan and zoom the board.");
    }

    function wireKeys(canvas) {
      canvas.addEventListener("keydown", function (e) {
        var handled = true;
        switch (e.key) {
          case "ArrowLeft": pz.panFraction(-0.1, 0); state.autoFit = false; break;
          case "ArrowRight": pz.panFraction(0.1, 0); state.autoFit = false; break;
          case "ArrowUp": pz.panFraction(0, -0.1); state.autoFit = false; break;
          case "ArrowDown": pz.panFraction(0, 0.1); state.autoFit = false; break;
          case "+": case "=": pz.zoomBy(1 / 1.25); state.autoFit = false; break;
          case "-": case "_": pz.zoomBy(1.25); state.autoFit = false; break;
          case "0": pz.fit(); state.autoFit = true; break;
          case "f": case "F": setFace(state.face === "F" ? "B" : "F", true); break;
          case "Escape": hideTip(); state.hover = null; drawRings(); break;
          default: handled = false;
        }
        if (handled) e.preventDefault();
      });
    }

    function wireResize(canvas) {
      if (typeof ResizeObserver === "undefined") return;
      var ro = new ResizeObserver(function () {
        var box = canvas.getBoundingClientRect();
        if (!box.width || !box.height) return;
        if (state.autoFit) { pz.fit(); return; }
        var v = pz.view;
        pz.set({ x: v.x, y: v.y, w: v.w, h: v.w * box.height / box.width });
      });
      ro.observe(canvas);
    }

    function prefetch() {
      if (typeof requestIdleCallback !== "function") return;
      requestIdleCallback(function () {
        var other = state.face === "F" ? "B_Fab" : "F_Fab";
        store.load(layerById(other)).catch(function () {});
      });
    }

    /* ------------------------------------------------------- schematic */
    function buildSchematic(host) {
      var fallbackEl = host.querySelector(".el-sch-fallback");
      host.dataset.state = "ready";
      var bar = el("div", { class: "el-sch-toolbar", role: "toolbar" }, host);
      bar.setAttribute("aria-label", "Schematic sheet controls");
      bar.setAttribute("data-search-exclude", "");
      el("label", { for: "el-sch-pick", text: "Sheet" }, bar);
      var pick = el("select", { id: "el-sch-pick", class: "el-sch-pick" }, bar);
      data.sch.sheets.forEach(function (s) {
        el("option", {
          value: String(s.n),
          text: s.n + " · " + s.title + " (" + s.refs.length + " part" +
                (s.refs.length === 1 ? "" : "s") + ")"
        }, pick);
      });
      pick.addEventListener("change", function () { loadSheet(parseInt(pick.value, 10), null); });

      function navBtn(label, delta) {
        var b = el("button", { type: "button", class: "el-pcb-btn", text: label }, bar);
        b.addEventListener("click", function () {
          var n = Math.min(19, Math.max(1, (ui.sheetN || 1) + delta));
          loadSheet(n, null);
        });
        return b;
      }
      navBtn("Previous", -1);
      navBtn("Next", 1);
      var zi = el("button", { type: "button", class: "el-pcb-btn", text: "Zoom in" }, bar);
      var zo = el("button", { type: "button", class: "el-pcb-btn", text: "Zoom out" }, bar);
      var zf = el("button", { type: "button", class: "el-pcb-btn", text: "Fit" }, bar);
      ui.schOpen = el("a", { class: "el-sch-open", text: "Open this sheet on its own", href: "#" }, bar);
      ui.schNative = el("a", { class: "el-sch-open", text: "Native .kicad_sch", href: "#" }, bar);
      ui.schBoard = el("button", { type: "button", class: "el-pcb-btn", text: "Show on board" }, bar);
      ui.schBoard.addEventListener("click", function () {
        if (!state.selected) { say("Select a part first."); return; }
        select(state.selected); locate(state.selected, true);
        root.scrollIntoView({ block: "start", behavior: state.reduced ? "auto" : "smooth" });
      });

      ui.schCaption = el("p", { class: "el-sch-caption" }, host);
      var canvas = el("div", { class: "el-sch-canvas", tabindex: "0", role: "group" }, host);
      canvas.setAttribute("aria-label", "Schematic sheet");
      ui.schCanvas = canvas;
      ui.schSvg = svg("svg", {
        class: "el-sch-svg", preserveAspectRatio: "xMidYMid meet",
        viewBox: data.sch.frame.viewBox.join(" ")
      }, canvas);
      ui.schSheet = svg("g", { class: "el-sch-sheet" }, ui.schSvg);
      ui.schRings = svg("g", { class: "el-sch-rings" }, ui.schSvg);
      ui.schStatus = el("p", { class: "el-pcb-status", role: "status" }, host);
      ui.schStatus.setAttribute("aria-live", "polite");
      ui.schRefs = el("p", { class: "el-pcb-related" }, host);

      ui.schPz = new PanZoom(ui.schSvg, data.sch.frame.viewBox.slice(), { minW: 20 });
      ui.schPz.frameNode = ui.schSheet;
      zi.addEventListener("click", function () { ui.schPz.zoomBy(1 / 1.25); });
      zo.addEventListener("click", function () { ui.schPz.zoomBy(1.25); });
      zf.addEventListener("click", function () { ui.schPz.fit(); });
      wireSchPointer(canvas);
      if (fallbackEl) fallbackEl.hidden = true;
      loadSheet(1, null);
    }

    function wireSchPointer(canvas) {
      var dragging = false, last = null;
      canvas.addEventListener("pointerdown", function (e) {
        dragging = true; last = { x: e.clientX, y: e.clientY };
        canvas.setPointerCapture(e.pointerId);
      });
      canvas.addEventListener("pointermove", function (e) {
        if (!dragging) return;
        var box = canvas.getBoundingClientRect();
        var v = ui.schPz.view;
        ui.schPz.panBy(-(e.clientX - last.x) * v.w / box.width,
                       -(e.clientY - last.y) * v.h / box.height);
        last = { x: e.clientX, y: e.clientY };
      });
      canvas.addEventListener("pointerup", function () { dragging = false; });
      canvas.addEventListener("pointercancel", function () { dragging = false; });
      canvas.addEventListener("wheel", function (e) {
        e.preventDefault();
        ui.schPz.zoomAt(e.deltaY > 0 ? 1.12 : 1 / 1.12, e.clientX, e.clientY);
      }, { passive: false });
      canvas.addEventListener("keydown", function (e) {
        if (e.key === "+" || e.key === "=") { ui.schPz.zoomBy(1 / 1.25); e.preventDefault(); }
        else if (e.key === "-") { ui.schPz.zoomBy(1.25); e.preventDefault(); }
        else if (e.key === "0") { ui.schPz.fit(); e.preventDefault(); }
      });
    }

    function sheetByNumber(n) {
      return data.sch.sheets.filter(function (s) { return s.n === n; })[0];
    }

    function loadSheet(n, ref) {
      var sheet = sheetByNumber(n);
      if (!sheet) return Promise.resolve();
      ui.sheetN = n;
      var pick = document.getElementById("el-sch-pick");
      if (pick) pick.value = String(n);
      ui.schOpen.href = base + sheet.file;
      ui.schNative.href = base + "kicad/" + sheet.native;
      ui.schCaption.textContent = sheet.plain;
      ui.schRefs.innerHTML = "";
      sheet.refs.forEach(function (r) {
        var b = el("button", { type: "button", class: "el-pcb-ref", text: r }, ui.schRefs);
        b.dataset.pcbRef = r;
        b.addEventListener("click", function () { select(r); locate(r, true); });
      });
      var url = base + sheet.file;
      if (ui.schCache && ui.schCache.n === n) {
        ui.schPz.fit();
        if (ref) ringSheetRef(ref);
        return Promise.resolve();
      }
      ui.schStatus.textContent = "Loading sheet " + n + "…";
      return fetchSVG(url).then(function (svgRoot) {
        ui.schSheet.innerHTML = "";
        ui.schRings.innerHTML = "";
        while (svgRoot.firstChild) ui.schSheet.appendChild(svgRoot.firstChild);
        ui.schCache = { n: n };
        ui.schPz.fit();
        ui.schStatus.textContent = "Sheet " + n + ": " + sheet.title + ".";
        setHash();
        if (ref) ringSheetRef(ref);
      }).catch(function (err) {
        ui.schStatus.textContent = "Sheet " + n + " could not be loaded. " +
          "The complete schematic PDF is linked in the downloads table.";
        if (window.console && console.warn) console.warn("[pcb] sheet " + n + ": " + err.message);
      });
    }

    function ringSheetRef(ref) {
      ui.schRings.innerHTML = "";
      var node = ui.schSheet.querySelector('[data-ref="' + ref + '"]');
      var box = null;
      if (node && node.getBBox) {
        var bb = node.getBBox();
        box = [bb.x, bb.y, bb.width, bb.height];
      }
      if (!box) return;
      var pad = 6;
      svg("rect", {
        x: box[0] - pad, y: box[1] - pad, width: box[2] + pad * 2, height: box[3] + pad * 2,
        class: "el-sch-ring"
      }, ui.schRings);
      ui.schPz.zoomTo([box[0] - pad, box[1] - pad, box[2] + pad * 2, box[3] + pad * 2], 60);
      ui.schStatus.textContent = ref + " is on sheet " + ui.sheetN + ", " +
        sheetByNumber(ui.sheetN).title + ".";
    }

    function showOnSheet(ref) {
      if (!schRoot) return;
      var n = data.sch.ref_to_sheet[ref];
      if (!n) return;
      loadSheet(n, ref).then(function () {
        schRoot.scrollIntoView({ block: "start", behavior: state.reduced ? "auto" : "smooth" });
      });
    }

    /* -------------------------------------------------------------- hash */
    var hashLock = false;

    function setHash() {
      if (hashLock) return;
      var parts = [];
      if (state.selected) parts.push("part=" + state.selected);
      if (ui.sheetN && ui.sheetN !== 1) parts.push("sheet=" + ui.sheetN);
      var hash = parts.length ? "#" + parts.join("&") : "";
      if (hash !== location.hash) {
        hashLock = true;
        history.replaceState(null, "", location.pathname + location.search + hash);
        hashLock = false;
      }
    }

    function readHash() {
      var hash = location.hash.replace(/^#/, "");
      if (!hash || hash.indexOf("=") < 0) return;
      var params = {};
      hash.split("&").forEach(function (chunk) {
        var kv = chunk.split("=");
        if (kv.length === 2) params[kv[0]] = decodeURIComponent(kv[1]);
      });
      if (params.sheet) {
        var n = parseInt(params.sheet, 10);
        if (n >= 1 && n <= 19) loadSheet(n, null);
      }
      if (params.part) {
        if (data.comp[params.part]) { select(params.part); locate(params.part, true); }
        else say("There is no part called " + params.part + " on this board.");
      }
    }

    /* --------------------------------------------------------------- API */
    function exposeAPI() {
      window.elPcb = {
        hitTest: function (x, y, face) { return hits.hitTest(x, y, face || state.face); },
        toScreen: function (x, y) { return pz.toScreen(x, y); },
        toWorld: function (x, y) { return pz.toWorld(x, y); },
        select: function (ref) { select(ref); },
        locate: function (ref, zoom) { locate(ref, zoom !== false); },
        setFace: setFace,
        setPreset: applyPreset,
        toggleLayer: function (id, on) { return toggleLayer(id, on, true); },
        showSheet: function (n, ref) { return loadSheet(n, ref || null); },
        getState: function () {
          return {
            face: state.face, preset: state.preset, appearance: state.appearance, selected: state.selected,
            layers: Object.keys(state.layers).filter(function (k) { return state.layers[k]; }).sort(),
            view: pz.view, fit: data.board.frame.fit, sheet: ui.sheetN || null,
            reducedMotion: !!state.reduced, group: state.group.slice()
          };
        }
      };
    }
  }

  /* Doc 10's flex viewer is a simpler instance of the same idea, so it borrows
     the pan/zoom core and the DOM helpers rather than copying them. */
  window.elPcbKit = {
    PanZoom: PanZoom, el: el, svg: svg, fetchJSON: fetchJSON, fetchSVG: fetchSVG, byRef: byRef
  };

  function initAll() {
    var root = document.getElementById("el-pcb");
    if (!root || root.dataset.init) return;
    root.dataset.init = "1";
    try {
      boot(root);
    } catch (err) {
      root.dataset.state = "error";
      if (window.console && console.warn) console.warn("[pcb] " + err.message);
    }
  }

  if (typeof document$ !== "undefined") document$.subscribe(initAll);
  else document.addEventListener("DOMContentLoaded", initAll);
})();
