// Opening journey: room → network → wordmark counter → engineering overview.
// Vanilla three.js port of landing-demo-site (FinalLandingJourney, PointScene,
// NetworkLayer, points-material, network-topology/cloud, ambient-dust,
// synthetic-floor, text-to-points, zoom-journey, network-visibility).
import * as THREE from '../vendor/three/three.module.min.js';
// Asset paths (data/, scans/) resolve against docs/assets/site/.
const SITE = new URL('../', import.meta.url);

const clamp01 = n => Math.max(0, Math.min(1, n));
const ease = n => { const t = clamp01(n); return t * t * (3 - 2 * t); };
const smoother = n => { const t = clamp01(n); return t * t * t * (t * (t * 6 - 15) + 10); };
const sstep = (a, b, x) => ease((x - a) / (b - a));
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) | 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// ── zoom-journey.ts / network-visibility.ts (verbatim maths) ────────────────
function roomZoomRatio(mobile) {
  const near = mobile ? Math.hypot(1.95, -1.65, 3.03) : Math.hypot(2.55, -2.85, 2.55);
  return Math.hypot(320, 180, 320) / near;
}
function zoomJourney(progress, mobile, letterScaleRatio) {
  const roomTravel = Math.log(roomZoomRatio(mobile));
  const letterTravel = Math.log(letterScaleRatio);
  const p = clamp01(progress);
  let paced = 0.3 * p + 0.7 * p * p * p;
  if (p > .7) {
    const t = (p - .7) / .3;
    const start = .3 * .7 + .7 * .7 ** 3;
    const tangent = (.3 + 2.1 * .7 ** 2) * .3;
    const curvature = (4.2 * .7) * .3 ** 2 / 2;
    const remaining = 1 - start;
    paced = start + tangent * t + curvature * t ** 2
      + (10 * remaining - 6 * tangent - 3 * curvature) * t ** 3
      + (-15 * remaining + 8 * tangent + 3 * curvature) * t ** 4
      + (6 * remaining - 3 * tangent - curvature) * t ** 5;
  }
  const travel = paced * (roomTravel + letterTravel);
  return { room: Math.min(1, travel / roomTravel), reveal: Math.max(0, (travel - roomTravel) / letterTravel) };
}
// ── zoom-journey.ts momentumRate ───────────────────────────────────────────
function momentumRate(progress) {
  // Give the network a readable glide, then tighten the spring into the wordmark.
  const t = clamp01((progress - 0.49) / 0.24);
  return 0.25 + 5.25 * t * t * t * (10 + t * (-15 + 6 * t));
}

// ── use-chapter-momentum.ts ────────────────────────────────────────────────
// Smooths the single document timeline (window scroll), never the camera or
// mask independently. Film-chapter stops are replaced by native scrolling of
// the engineering content; a fresh gesture is required after arrival.
function installMomentum({ section, isReady }) {
  let target = scrollY, position = scrollY, velocity = 0, raf = 0, last = 0;
  let lastWheel = 0, gesture = 0, queued = 0, touchY = null;
  const end = () => Math.max(0, section.offsetTop + section.offsetHeight - innerHeight);
  const tick = time => {
    const dt = document.hidden ? 0 : Math.max(0, (time - last) / 1000 || 1 / 60); last = time;
    const limit = end();
    // Analytic critically damped spring: no overshoot, stable at variable frame rates.
    const blend = clamp01((position - limit) / Math.max(1, innerHeight * .35));
    const rate = target < position ? 2.4 : momentumRate(position / Math.max(1, limit));
    const omega = rate * (1 - blend) + 1.65 * blend, displacement = position - target;
    const b = velocity + omega * displacement, decay = Math.exp(-omega * dt);
    position = target + (displacement + b * dt) * decay;
    velocity = (velocity - omega * b * dt) * decay;
    scrollTo({ top: position, behavior: 'instant' });
    if (Math.abs(position - target) < .5 && Math.abs(velocity) < 1) {
      position = target; velocity = 0;
      scrollTo({ top: target, behavior: 'instant' }); raf = 0;
    } else raf = requestAnimationFrame(tick);
  };
  const stop = () => { cancelAnimationFrame(raf); raf = 0; velocity = 0; target = position = scrollY; };
  // Returns true when the input was consumed by the intro timeline.
  const advance = delta => {
    if (!delta || !Number.isFinite(delta)) return false;
    const limit = end(), time = performance.now();
    if (!raf) position = target = scrollY;
    if (position >= limit - 1) {
      // Ignore the whole tail of the gesture that completed the intro.
      if (raf || time - lastWheel < 180) { lastWheel = time; return true; }
      // Engineering content scrolls natively; only an upward gesture at the
      // handoff point re-enters the intro.
      if (delta > 0 || position > limit + 1) { lastWheel = time; return false; }
    }
    if (!isReady()) { queued = Math.sign(delta); return true; }
    // A reverse gesture takes ownership immediately.
    const direction = Math.sign(delta);
    const reversing = (Math.abs(velocity) > 1 && Math.sign(velocity) !== direction)
      || (Math.abs(target - position) > .5 && Math.sign(target - position) !== direction);
    if (reversing) { position = target = scrollY; velocity = 0; gesture = 0; }
    if (time - lastWheel > 180 || Math.sign(gesture) !== direction) gesture = 0;
    gesture += delta; lastWheel = time;
    target = Math.abs(gesture) >= 100 ? (delta > 0 ? limit : 0) : Math.max(0, Math.min(limit, target + delta * 5));
    if (!raf) { last = time; raf = requestAnimationFrame(tick); }
    return true;
  };
  const nested = el => el && el.closest && el.closest('input,textarea,select,[data-native-scroll]');
  const wheel = e => {
    if (e.ctrlKey || Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
    if (nested(e.composedPath ? e.composedPath()[0] : e.target)) return;
    if (advance(e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? innerHeight : 1))) e.preventDefault();
  };
  const touchStart = e => { touchY = e.touches[0] ? e.touches[0].clientY : null; if (raf) stop(); };
  const touchMove = e => {
    if (touchY === null || e.touches.length !== 1 || nested(e.target)) return;
    const y = e.touches[0].clientY, delta = touchY - y, limit = end();
    const inIntro = scrollY < limit - 1 || (delta < 0 && scrollY <= limit + 1);
    if (!inIntro) return;
    e.preventDefault();
    if (Math.abs(delta) >= 8) { touchY = y; advance(delta * 4); }
  };
  const key = e => {
    if (e.target && e.target.closest && e.target.closest('input,textarea,select,button,a,[contenteditable]')) return;
    const delta = ['ArrowDown', 'PageDown', ' '].includes(e.key) ? (e.shiftKey ? -120 : 120) : ['ArrowUp', 'PageUp'].includes(e.key) ? -120 : 0;
    if (!delta) return;
    const limit = end();
    if (!(scrollY < limit - 1 || (delta < 0 && scrollY <= limit + 1))) return;
    e.preventDefault();
    if (!e.repeat) advance(delta);
  };
  const resetClock = () => { last = performance.now(); };
  document.addEventListener('visibilitychange', resetClock);
  addEventListener('wheel', wheel, { passive: false });
  addEventListener('touchstart', touchStart, { passive: true });
  addEventListener('touchmove', touchMove, { passive: false });
  addEventListener('keydown', key); addEventListener('resize', stop);
  return {
    stop,
    flush() { if (queued && isReady()) { const dir = queued; queued = 0; lastWheel = -Infinity; advance(dir * 120); } },
    destroy() { stop(); document.removeEventListener('visibilitychange', resetClock); removeEventListener('wheel', wheel); removeEventListener('touchstart', touchStart); removeEventListener('touchmove', touchMove); removeEventListener('keydown', key); removeEventListener('resize', stop); },
  };
}

function networkVisibility(pixelSpan, finalPixelSpan) {
  const extinction = Math.max(.6, finalPixelSpan * 1.02);
  const start = Math.max(70, extinction * 8);
  const t = clamp01(Math.log(Math.max(extinction, pixelSpan) / extinction) / Math.log(start / extinction));
  return t * t * (3 - 2 * t);
}

// ── points-material.ts ─────────────────────────────────────────────────────
function pointsMaterial({ pointSize = 0.04, pixelRatio = 1, opacity = 0.15, twinkle = 0.15, aliveDrift = 0 }) {
  return new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }, uPointSize: { value: pointSize }, uPixelRatio: { value: pixelRatio },
      uOpacity: { value: opacity }, uTwinkle: { value: twinkle }, uDioramaEnabled: { value: 0 },
      uDioramaCamPos: { value: new THREE.Vector3() }, uDioramaViewDir: { value: new THREE.Vector3(0, 0, 1) },
      uDioramaOffset: { value: 0 }, uZoomNoise: { value: 0 }, uAliveDrift: { value: aliveDrift },
    },
    transparent: true, depthWrite: false, depthTest: true, blending: THREE.AdditiveBlending,
    vertexShader: `
      uniform float uTime, uPointSize, uPixelRatio, uTwinkle, uDioramaEnabled, uDioramaOffset, uZoomNoise, uAliveDrift;
      uniform vec3 uDioramaCamPos, uDioramaViewDir;
      attribute float aBrightness; attribute float aSeed;
      varying float vBrightness;
      float hash1(float n) { return fract(sin(n) * 43758.5453123); }
      void main() {
        vec4 wp4 = modelMatrix * vec4(position, 1.0);
        if (uAliveDrift > 0.0001) {
          if (step(fract(aSeed * 0.1373), 0.20) > 0.5) {
            float tt = uTime * 0.05 + aSeed * 6.2831;
            wp4.xyz += vec3(sin(tt * 1.20), cos(tt * 0.73 + 1.1), sin(tt * 1.51 + 2.3)) * uAliveDrift;
          }
          if (step(fract(aSeed * 0.4919 + 0.31), 0.03) > 0.5) {
            float zt = uTime * 0.1 + aSeed * 3.14;
            wp4.xyz += vec3(sin(zt * 2.4), cos(zt * 1.9 + 0.8), sin(zt * 3.1 + 1.7)) * uAliveDrift * 1.6;
          }
        }
        if (uDioramaEnabled > 0.5) {
          float d = dot(wp4.xyz - uDioramaCamPos, uDioramaViewDir);
          if (d < uDioramaOffset) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 0.0; vBrightness = 0.0; return; }
        }
        vec4 mv = viewMatrix * wp4;
        gl_Position = projectionMatrix * mv;
        float size = uPointSize * uPixelRatio * (320.0 / max(-mv.z, 0.3));
        gl_PointSize = clamp(size, 1.0, 12.0);
        float phase = hash1(aSeed) * 6.2831;
        float t = sin(uTime * 0.08 + phase) * 0.5 + 0.5;
        vBrightness = aBrightness * mix(1.0, t, uTwinkle);
      }`,
    fragmentShader: `
      precision highp float;
      uniform float uOpacity; varying float vBrightness;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        gl_FragColor = vec4(1.0, 1.0, 1.0, (1.0 - smoothstep(0.42, 0.5, d)) * vBrightness * uOpacity);
      }`,
  });
}
function makePoints(data, opts) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(data.positions, 3));
  g.setAttribute('aBrightness', new THREE.BufferAttribute(data.brightness, 1));
  const n = data.positions.length / 3, seeds = new Float32Array(n);
  for (let i = 0; i < n; i++) seeds[i] = Math.random() * 1000;
  g.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1));
  const m = pointsMaterial(opts);
  const pts = new THREE.Points(g, m);
  pts.frustumCulled = false;
  return { pts, u: m.uniforms, count: n };
}

// ── synthetic-floor.ts ─────────────────────────────────────────────────────
function hash2(ix, iy, seed) { let a = (ix * 73856093) ^ (iy * 19349663) ^ seed; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), a | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
function vnoise(x, y, seed) { const x0 = Math.floor(x), y0 = Math.floor(y), fx = ease(x - x0), fy = ease(y - y0); const a = hash2(x0, y0, seed) * (1 - fx) + hash2(x0 + 1, y0, seed) * fx; const b = hash2(x0, y0 + 1, seed) * (1 - fx) + hash2(x0 + 1, y0 + 1, seed) * fx; return a * (1 - fy) + b * fy; }
function buildFloor({ radius, count, y = -0.05, thickness = 0.35, peak = 0.48, seed = 0xf100 }) {
  const positions = new Float32Array(count * 3), brightness = new Float32Array(count), rng = mulberry32(seed);
  for (let i = 0; i < count; i++) {
    const rN = Math.sqrt(rng()), th = rng() * Math.PI * 2, c = Math.cos(th), s = Math.sin(th);
    const r = rN * radius * (0.55 + vnoise(c * 2.2, s * 2.2, seed ^ 0x51) * 0.9), x = r * c, z = r * s;
    const patch = Math.pow(vnoise(x * 0.55, z * 0.55, seed ^ 0x2a1), 1.6);
    positions[i * 3] = x; positions[i * 3 + 1] = y - (1 - Math.pow(rng(), 2)) * thickness; positions[i * 3 + 2] = z;
    brightness[i] = peak * (1 - Math.min(1, r / radius) * 0.75) * (0.12 + patch * 1.1);
  }
  return { positions, brightness };
}

// ── ambient-dust.ts ────────────────────────────────────────────────────────
function buildDust({ count, extent, brightness: [b0, b1], seed = 0xc303, clearance = 3.5 }) {
  const rng = mulberry32(seed), positions = new Float32Array(count * 3), br = new Float32Array(count);
  let n = 0, tries = 0;
  while (n < count && tries++ < count * 4) {
    const x = (rng() - .5) * 2 * extent.x, y = (rng() - .5) * 2 * extent.y, z = (rng() - .5) * 2 * extent.z;
    if (x * x + y * y + z * z < clearance * clearance) continue;
    positions[n * 3] = x; positions[n * 3 + 1] = y; positions[n * 3 + 2] = z; br[n] = b0 + rng() * (b1 - b0); n++;
  }
  return { positions: positions.slice(0, n * 3), brightness: br.slice(0, n) };
}

// ── network-topology.ts ────────────────────────────────────────────────────
function makeShape(rng) {
  const roll = rng(), blobCount = roll < 0.25 ? 3 : roll < 0.7 ? 4 : 5, blobs = [];
  let remaining = 1;
  for (let b = 0; b < blobCount; b++) {
    const isLast = b === blobCount - 1;
    const weight = isLast ? remaining : (b === 0 ? 0.64 + rng() * 0.12 : 0.28 + rng() * 0.18) * remaining;
    remaining -= weight;
    const mag = b === 0 ? rng() * 0.15 : 0.8 + rng() * 1.1;
    const ox = rng() - .5, oy = rng() - .5, oz = rng() - .5, nm = Math.hypot(ox, oy, oz) || 1;
    const offset = [ox / nm * mag, oy / nm * mag, oz / nm * mag];
    const sizeMul = b === 0 ? 0.65 + rng() * 0.35 : 0.2 + rng() * 0.55;
    const sa = Math.floor(rng() * 3), axes = [0, 0, 0];
    if (b === 0) {
      if (rng() < 0.35) for (let a = 0; a < 3; a++) axes[a] = a === sa ? 1.6 + rng() * 1.6 : 0.35 + rng() * 0.55;
      else for (let a = 0; a < 3; a++) axes[a] = 0.4 + rng() * 1.4;
    } else for (let a = 0; a < 3; a++) axes[a] = a === sa ? 2.2 + rng() * 2.3 : 0.1 + rng() * 0.35;
    const rotation = [rng() * Math.PI * 2, rng() * Math.PI * 2, rng() * Math.PI * 2];
    const densityExponent = b === 0 ? 10 + rng() * 12 : 2.5 + rng() * 2.5;
    blobs.push({ offset, sizeMul, axes, rotation, densityExponent, weight });
  }
  return { blobs, surfaceJitter: 0.2 + rng() * 0.5 };
}
function buildGraph({ count, seed = 0xa101, extent, minSep, roomClearance, labelFraction = 0.24 }) {
  const rng = mulberry32(seed);
  const nodes = [{ position: [0, 0, 0], radius: 3.5, labelSeed: 0, hasLabel: false, shape: makeShape(rng) }];
  let attempts = 0;
  while (nodes.length < count && attempts++ < count * 500) {
    const p = [(rng() - .5) * 2 * extent.x, (rng() - .5) * 2 * extent.y, (rng() - .5) * 2 * extent.z];
    if (Math.hypot(...p) < roomClearance) continue;
    if (nodes.some(n => Math.hypot(n.position[0] - p[0], n.position[1] - p[1], n.position[2] - p[2]) < minSep)) continue;
    nodes.push({ position: p, radius: 5.3 + rng() * 3, labelSeed: Math.floor(rng() * 1e9), hasLabel: rng() < labelFraction, shape: makeShape(rng) });
  }
  const edges = [], seen = new Set();
  for (let i = 0; i < nodes.length; i++) {
    const d = [];
    for (let j = 0; j < nodes.length; j++) if (j !== i) d.push({ j, d: Math.hypot(nodes[j].position[0] - nodes[i].position[0], nodes[j].position[1] - nodes[i].position[1], nodes[j].position[2] - nodes[i].position[2]) });
    d.sort((p, q) => p.d - q.d);
    for (let m = 0; m < Math.min(5, d.length); m++) {
      const a = Math.min(i, d[m].j), b = Math.max(i, d[m].j), key = a + '-' + b;
      if (seen.has(key)) continue; seen.add(key);
      const pa = nodes[a].position, pb = nodes[b].position;
      const amp = Math.min(6, 0.18 * Math.hypot(pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]) + 1.2);
      const voidStart = 0.18 + rng() * 0.48, voidEnd = Math.min(0.95, voidStart + 0.05 + rng() * 0.12);
      edges.push({ a, b, curveOffset: [(rng() - .5) * 2 * amp, (rng() - .5) * 1.3 * amp, (rng() - .5) * 2 * amp], jitterAmp: 0.06 + rng() * 0.22, voidStart, voidEnd });
    }
  }
  return { nodes, edges };
}

// ── network-cloud.ts ───────────────────────────────────────────────────────
function rotXYZ(out, vx, vy, vz, [rx, ry, rz]) {
  let c = Math.cos(rx), s = Math.sin(rx); const y1 = vy * c - vz * s, z1 = vy * s + vz * c, x1 = vx;
  c = Math.cos(ry); s = Math.sin(ry); const x2 = x1 * c + z1 * s, z2 = -x1 * s + z1 * c, y2 = y1;
  c = Math.cos(rz); s = Math.sin(rz); out[0] = x2 * c - y2 * s; out[1] = x2 * s + y2 * c; out[2] = z2;
}
function buildNetworkCloud(graph, { pointsPerNode, pointsPerEdge, seed = 0xb202 }) {
  const rng = mulberry32(seed), nodes = graph.nodes.slice(1);
  const total = nodes.length * pointsPerNode, np = new Float32Array(total * 3), nb = new Float32Array(total), local = [0, 0, 0];
  let i = 0;
  for (const node of nodes) {
    let used = 0;
    node.shape.blobs.forEach((blob, b) => {
      const n = b === node.shape.blobs.length - 1 ? pointsPerNode - used : Math.floor(pointsPerNode * blob.weight);
      used += n;
      for (let k = 0; k < n; k++) {
        const rNorm = Math.pow(rng(), blob.densityExponent), r = rNorm * node.radius * blob.sizeMul;
        const th = Math.acos(2 * rng() - 1), ph = rng() * Math.PI * 2, st = Math.sin(th);
        rotXYZ(local, st * Math.cos(ph) * r * blob.axes[0], st * Math.sin(ph) * r * blob.axes[1], Math.cos(th) * r * blob.axes[2], blob.rotation);
        const sj = node.shape.surfaceJitter;
        const u1 = rng() || 1e-9, u2 = rng(), mg = Math.sqrt(-2 * Math.log(u1)) * sj;
        const u3 = rng() || 1e-9, u4 = rng();
        np[i * 3] = node.position[0] + local[0] + blob.offset[0] * node.radius + mg * Math.cos(2 * Math.PI * u2);
        np[i * 3 + 1] = node.position[1] + local[1] + blob.offset[1] * node.radius + mg * Math.sin(2 * Math.PI * u2);
        np[i * 3 + 2] = node.position[2] + local[2] + blob.offset[2] * node.radius + Math.sqrt(-2 * Math.log(u3)) * sj * Math.cos(2 * Math.PI * u4);
        const c2 = (1 - rNorm) ** 2; nb[i] = 0.22 + c2 * c2 * 1.1; i++;
      }
    });
  }
  const et = graph.edges.length * pointsPerEdge, ep = new Float32Array(et * 3), eb = new Float32Array(et);
  let e = 0;
  for (const edge of graph.edges) {
    const a = graph.nodes[edge.a].position, b = graph.nodes[edge.b].position;
    const mid = [(a[0] + b[0]) / 2 + edge.curveOffset[0], (a[1] + b[1]) / 2 + edge.curveOffset[1], (a[2] + b[2]) / 2 + edge.curveOffset[2]];
    const wx = Math.cos(edge.voidStart * 12.9) * .8, wy = Math.cos(edge.voidEnd * 17.3) * .8, wz = Math.sin(edge.voidStart * 9.3 + edge.voidEnd * 4.1) * .8;
    const wf = 1.5 + ((edge.a * 7 + edge.b * 11) % 5), wa = edge.jitterAmp * 1.5;
    for (let k = 0; k < pointsPerEdge; k++) {
      const t = rng();
      if (t > edge.voidStart && t < edge.voidEnd) {
        const vm = (edge.voidStart + edge.voidEnd) / 2, vh = (edge.voidEnd - edge.voidStart) / 2;
        if (rng() < (1 - Math.abs(t - vm) / vh) * 0.9) continue;
      }
      const mt = 1 - t, env = Math.sin(Math.PI * t) * Math.sin(t * wf * Math.PI * 2) * wa;
      ep[e * 3] = mt * mt * a[0] + 2 * mt * t * mid[0] + t * t * b[0] + wx * env + (rng() - .5) * edge.jitterAmp;
      ep[e * 3 + 1] = mt * mt * a[1] + 2 * mt * t * mid[1] + t * t * b[1] + wy * env + (rng() - .5) * edge.jitterAmp;
      ep[e * 3 + 2] = mt * mt * a[2] + 2 * mt * t * mid[2] + t * t * b[2] + wz * env + (rng() - .5) * edge.jitterAmp;
      eb[e] = (0.42 + Math.pow(Math.abs(t - .5) * 2, 1.2) * 0.38) * (0.7 + rng() * 0.5); e++;
    }
  }
  return { nodes: { positions: np, brightness: nb }, edges: { positions: ep.slice(0, e * 3), brightness: eb.slice(0, e) } };
}

// ── text-to-points.ts ──────────────────────────────────────────────────────
function buildTextPoints({ text, font, worldWidth, densityMultiplier = 1, zJitter = 0.05, brightnessRange: [bMin, bMax] = [0.85, 1.2], letterSpacing = 0.02 }) {
  const mctx = document.createElement('canvas').getContext('2d');
  mctx.font = font;
  const met = mctx.measureText(text), ascent = met.actualBoundingBoxAscent || 140, descent = met.actualBoundingBoxDescent || 40;
  const fontSize = parseFloat((font.match(/(\d+(?:\.\d+)?)px/) || [0, 180])[1]), ls = fontSize * letterSpacing;
  let tw = 0; for (let i = 0; i < text.length; i++) tw += mctx.measureText(text[i]).width + (i < text.length - 1 ? ls : 0);
  const padX = fontSize * .15, padY = fontSize * .15, W = Math.ceil(tw + padX * 2), H = Math.ceil(ascent + descent + padY * 2);
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d', { willReadFrequently: true });
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.fillStyle = '#fff'; ctx.textBaseline = 'alphabetic'; ctx.font = font;
  let x = padX; for (let i = 0; i < text.length; i++) { ctx.fillText(text[i], x, padY + ascent); x += ctx.measureText(text[i]).width + (i < text.length - 1 ? ls : 0); }
  const data = ctx.getImageData(0, 0, W, H).data, lum = i => (data[i] + data[i + 1] + data[i + 2]) / 3;
  const edgeIdx = [], intIdx = [], cand = [];
  for (let py = 0; py < H; py++) for (let px = 0; px < W; px++) {
    const v = lum((py * W + px) * 4); if (v <= 165) continue;
    let edge = 0;
    outer: for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) {
      if (!dx && !dy) continue; const nx = px + dx, ny = py + dy;
      if (nx < 0 || ny < 0 || nx >= W || ny >= H || lum((ny * W + nx) * 4) <= 60) { edge = 1; break outer; }
    }
    (edge ? edgeIdx : intIdx).push(cand.length / 3); cand.push(px, py, v);
  }
  const rng = mulberry32(1337), totalC = cand.length / 3, req = Math.floor(totalC * densityMultiplier * 1.35);
  const pos = new Float32Array(req * 3), br = new Float32Array(req), wH = H / W * worldWidth, edgeReq = Math.floor(req * (edgeIdx.length ? 0.68 : 0));
  let n = 0;
  for (let i = 0; i < req; i++) {
    const pickEdge = i < edgeReq ? edgeIdx.length > 0 : intIdx.length === 0 && edgeIdx.length > 0;
    const pool = pickEdge ? edgeIdx : intIdx; if (!pool.length) continue;
    const ci = pool[Math.floor(rng() * pool.length)] * 3, px = cand[ci], py = cand[ci + 1], v = cand[ci + 2] / 255;
    const AMP = pickEdge ? 0.4 : 10, TRIES = pickEdge ? 12 : 2; let jx = NaN, jy = NaN;
    for (let k = 0; k < TRIES; k++) {
      const tx = (rng() - .5) * 2 * AMP, ty = (rng() - .5) * 2 * AMP, sx = Math.round(px + tx), sy = Math.round(py + ty);
      if (sx < 0 || sy < 0 || sx >= W || sy >= H) continue;
      if (lum((sy * W + sx) * 4) > 165) { jx = tx; jy = ty; break; }
    }
    if (Number.isNaN(jx)) continue;
    pos[n * 3] = (px + jx) / W * worldWidth - worldWidth / 2;
    pos[n * 3 + 1] = -((py + jy) / H * wH - wH / 2);
    pos[n * 3 + 2] = (rng() - .5) * zJitter;
    br[n] = bMin + rng() * (bMax - bMin) * v; n++;
  }
  return { positions: pos.slice(0, n * 3), brightness: br.slice(0, n) };
}

// ── load-cloud.ts (parts are concatenated client-side, like worker/index.js) ─
async function fetchBytes(urls, sizes, onProgress) {
  const got = urls.map(() => 0), total = sizes.reduce((a, b) => a + b, 0);
  const parts = await Promise.all(urls.map(async (url, i) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error('cloud fetch failed: ' + res.status);
    if (!res.body || !res.body.getReader) { const b = new Uint8Array(await res.arrayBuffer()); got[i] = b.length; onProgress(got.reduce((a, c) => a + c, 0) / total); return b; }
    const reader = res.body.getReader(), chunks = [];
    for (;;) { const { done, value } = await reader.read(); if (done) break; chunks.push(value); got[i] += value.length; onProgress(Math.min(1, got.reduce((a, c) => a + c, 0) / total)); }
    const b = new Uint8Array(got[i]); let o = 0; for (const c of chunks) { b.set(c, o); o += c.length; } return b;
  }));
  const len = parts.reduce((a, p) => a + p.length, 0), all = new Uint8Array(len); let o = 0;
  for (const p of parts) { all.set(p, o); o += p.length; }
  return all.buffer;
}
function parseCloud(buf, targetRadius) {
  const N = new DataView(buf).getUint32(0, true);
  const positions = new Float32Array(buf, 4, N * 3).slice(), brightness = new Float32Array(buf, 4 + N * 12, N).slice();
  const stride = Math.max(1, Math.floor(N / 12000)), sample = [];
  for (let i = 0; i < N; i += stride) sample.push(Math.hypot(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]));
  sample.sort((a, b) => a - b);
  const scale = targetRadius / Math.max(sample[Math.floor(sample.length * .95)] || 1, 1e-6);
  for (let i = 0; i < N * 3; i++) positions[i] *= scale;
  return { positions, brightness };
}

// ── wordmark (IBM Plex Sans Regular outlines, data/wordmark-plex.json) ──────
let wmPromise;
const getWordmark = () => wmPromise || (wmPromise = fetch(new URL('data/wordmark-plex.json', SITE)).then(r => r.json()));
export async function fillWordmark(el) {
  const wm = await getWordmark(), k = wm.ink;
  el.innerHTML = `<svg viewBox="${k.x1} ${k.y1} ${k.x2 - k.x1} ${k.y2 - k.y1}" width="100%" height="100%" preserveAspectRatio="xMinYMin meet" aria-hidden="true" style="display:block;overflow:visible"><path d="${wm.letters}" fill="#fff" fill-rule="evenodd"/></svg>`;
  return wm;
}

const LABELS = ['Reading', 'Cooking', 'Watching a movie', 'Working', 'Relaxing', 'Sleeping', 'Cleaning', 'Empty room', 'Conversation', 'Dinner', 'Ambient mode', 'Focus', 'Morning routine', 'Evening wind-down', 'Arriving home', 'Late night'];
const NEAR = { d: [new THREE.Vector3(-1.55, 1.25, -1.55), new THREE.Vector3(1.0, -1.6, 1.0)], m: [new THREE.Vector3(-1.55, 1.55, -1.55), new THREE.Vector3(0.4, -0.1, 1.48)] };
const FAR_POS = new THREE.Vector3(-320, 180, -320), FAR_LOOK = new THREE.Vector3(0, 0, 0);

export async function mountOpening(o) {
  const { section, stage, backdrop, sceneWindow, canvasHost, labelsLayer, overlayHost, slot, content, hint, skip, note, pill, mobile } = o;
  const status = s => { try { o.onStatus && o.onStatus(s); } catch (e) {} };
  let alive = true, raf = 0, running = false;
  const timers = [], cleanups = [];
  const wm = await fillWordmark(slot);
  const ink = wm.ink, inkW = ink.x2 - ink.x1;
  slot.style.opacity = '0';

  // Overlay: black field with the e counter cut out, plus the white letters.
  const id = 'elj' + Math.random().toString(36).slice(2, 7);
  overlayHost.innerHTML = `<svg width="100%" height="100%" style="position:absolute;inset:0;display:block"><defs><mask id="${id}" maskUnits="userSpaceOnUse" x="0" y="0" width="100%" height="100%" style="mask-type:luminance"><rect width="100%" height="100%" fill="white"/><g data-k="opening"><path d="${wm.counter}" fill="black"/></g></mask></defs><rect data-k="field" width="100%" height="100%" fill="black" mask="url(#${id})"/><g data-k="letters"><path d="${wm.letters}" fill="white" fill-rule="evenodd"/></g></svg>`;
  const svg = overlayHost.firstChild, gOpen = svg.querySelector('[data-k=opening]'), gLetters = svg.querySelector('[data-k=letters]'), field = svg.querySelector('[data-k=field]');

  // Three.js scene
  let renderer = null, scene, camera, ready = false, cloudDone = false, netReady = false, momentum = null;
  const isReady = () => !renderer || (cloudDone && netReady);
  const onReadyChange = () => { if (momentum) momentum.flush(); };
  const zoom = { v: 0 };
  const updaters = [];
  const [nearPos, nearLook] = mobile ? NEAR.m : NEAR.d;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: /[?&]capture=1/.test(location.search) });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, mobile ? 1.5 : 2));
    renderer.setClearColor(0x000000, 1);
    renderer.domElement.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block';
    canvasHost.appendChild(renderer.domElement);
  } catch (e) { renderer = null; status({ status: 'error', pct: 0 }); }
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(55, 1, 0.05, 2000);
  camera.position.copy(nearPos); camera.lookAt(nearLook);
  const pr = Math.min(devicePixelRatio || 1, 2);
  const viewDir = new THREE.Vector3().subVectors(nearLook, nearPos).normalize();
  const diorama = u => { u.uDioramaEnabled.value = 1; u.uDioramaCamPos.value.copy(nearPos); u.uDioramaViewDir.value.copy(viewDir); u.uDioramaOffset.value = 1.8; };
  const add = (m, fn) => { scene.add(m.pts); updaters.push((z, t) => { m.u.uTime.value = t; fn && fn(z, m); }); return m; };

  if (renderer) {
    const floor = add(makePoints(buildFloor({ radius: mobile ? 3.6 : 4.2, count: mobile ? 40000 : 70000 }), { pointSize: mobile ? 0.025 : 0.03, pixelRatio: pr, opacity: 0.14, twinkle: 0.04, aliveDrift: 0.003 }),
      (z, m) => { m.u.uDioramaOffset.value = THREE.MathUtils.lerp(1.8, -100, sstep(0, .35, z)); m.u.uOpacity.value = 0.14 * (1 - sstep(0, .13, z)); });
    diorama(floor.u);

    // Wordmark points inside the room, set in IBM Plex Sans 500.
    const textFont = '500 180px "IBM Plex Sans"';
    const buildText = () => {
      if (!alive) return;
      const group = new THREE.Group();
      group.rotation.y = mobile ? -Math.PI * 0.818 : -Math.PI * 0.75;
      const common = { font: textFont, densityMultiplier: 0.34, zJitter: 0.04, letterSpacing: 0.01, brightnessRange: [0.45, 1.45] };
      [['engineered', mobile ? 1.05 : 1.35, mobile ? [0.46, -0.42, -1.42] : [-0.7, 0, 0]], ['lighting', mobile ? 0.86 : 1.12, mobile ? [0.46, -0.6, -1.42] : [0.58, 0, 0]]].forEach(([text, worldWidth, p]) => {
        const m = makePoints(buildTextPoints({ ...common, text, worldWidth }), { pointSize: mobile ? 0.022 : 0.025, pixelRatio: pr, opacity: 0.32, twinkle: 0.02 });
        m.pts.position.set(...p); group.add(m.pts); updaters.push((z, t) => { m.u.uTime.value = t; });
      });
      scene.add(group);
    };
    const fontReady = async () => {
      if (!document.fonts || !document.fonts.load) return;
      for (let i = 0; i < 40; i++) {
        try { await document.fonts.load(textFont); } catch (e) {}
        if (document.fonts.check(textFont)) return;
        await new Promise(r => setTimeout(r, 100));
      }
    };
    fontReady().then(buildText);

    // Captured apartment cloud.
    status({ status: 'loading', pct: 0 });
    // Parts and byte sizes come from large-assets.json (passed in by home.js).
    // A cloud that is not published yet takes the error path without a request.
    const cloudSrc = (o.clouds || {})[mobile ? 'mobile' : 'desktop'] || { present: false, parts: [] };
    const urls = cloudSrc.parts.map(p => new URL(p.path, SITE).href);
    const sizes = cloudSrc.parts.map(p => p.bytes);
    let lastPct = -1;
    (cloudSrc.present ? fetchBytes(urls, sizes, f => { const pct = Math.round(f * 100); if (pct !== lastPct) { lastPct = pct; status({ status: 'loading', pct }); } }) : Promise.reject(new Error('cloud not published')))
      .then(buf => {
        if (!alive) return;
        const cloud = parseCloud(buf, mobile ? 3.2 : 4);
        const m = add(makePoints(cloud, { pointSize: mobile ? 0.024 : 0.035, pixelRatio: pr, opacity: 0.08, twinkle: 0.12, aliveDrift: 0.006 }), (z, m) => {
          m.u.uDioramaOffset.value = THREE.MathUtils.lerp(1.8, -100, sstep(0, .35, z));
          if (mobile) {
            m.pts.geometry.setDrawRange(0, Math.floor(m.count * THREE.MathUtils.lerp(1, 0.2, sstep(.05, .55, z))));
            m.u.uPointSize.value = 0.024 * THREE.MathUtils.lerp(1, 3.5, sstep(.02, .2, z));
          }
        });
        diorama(m.u);
        ready = true; cloudDone = true; status({ status: netReady ? 'ready' : 'loading', pct: 100 }); kick(); onReadyChange();
      })
      .catch(() => { if (alive) { cloudDone = true; status({ status: 'error', pct: 0 }); onReadyChange(); } });

    // Network, deferred so the room paints first.
    timers.push(setTimeout(() => {
      if (!alive) return;
      const graph = buildGraph({ count: mobile ? 56 : 98, extent: mobile ? { x: 95, y: 260, z: 95 } : { x: 195, y: 120, z: 195 }, minSep: 22, roomClearance: 38 });
      const nc = buildNetworkCloud(graph, { pointsPerNode: mobile ? 2800 : 8400, pointsPerEdge: mobile ? 650 : 1850 });
      add(makePoints(buildDust({ count: mobile ? 32000 : 170000, extent: mobile ? { x: 105, y: 285, z: 105 } : { x: 215, y: 135, z: 215 }, brightness: [0.15, 0.45] }), { pointSize: mobile ? 0.028 : 0.032, pixelRatio: pr, opacity: 0, twinkle: 0.5, aliveDrift: 0.28 }),
        (z, m) => { m.u.uOpacity.value = 0.1 * sstep(0.2, 0.55, z); });
      add(makePoints(nc.edges, { pointSize: mobile ? 0.055 : 0.06, pixelRatio: pr, opacity: 0.55, twinkle: 0.4, aliveDrift: 0.09 }));
      add(makePoints(nc.nodes, { pointSize: mobile ? 0.075 : 0.09, pixelRatio: pr, opacity: 0.85, twinkle: 0.28, aliveDrift: 0.12 }));
      if (o.labels !== false) buildLabels(graph);
      // Let the network's GPU resources paint before accepting a flick.
      requestAnimationFrame(() => requestAnimationFrame(() => { netReady = true; if (cloudDone && ready) status({ status: 'ready', pct: 100 }); onReadyChange(); }));
      kick();
    }, 250));
  }

  // Illustrative inference labels (not a live feed).
  const labelEls = [];
  function buildLabels(graph) {
    const list = graph.nodes.slice(1).filter(n => n.hasLabel).slice(0, mobile ? 12 : Infinity);
    list.forEach((node, i) => {
      const el = document.createElement('div');
      el.style.cssText = "position:absolute;left:0;top:0;display:flex;align-items:center;gap:10px;padding:5px 10px;white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:" + (mobile ? 11 : 12) + "px;line-height:1.3;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.92);background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.12);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);opacity:0;transition:opacity 220ms ease;will-change:transform,opacity";
      const idEl = document.createElement('span'); idEl.style.color = '#8F8F8F'; idEl.textContent = 'N-' + String(i + 1).padStart(2, '0');
      const tx = document.createElement('span'); tx.textContent = LABELS[node.labelSeed % LABELS.length];
      el.append(idEl, tx); labelsLayer.appendChild(el);
      const rec = { el, tx, dim: false, v: new THREE.Vector3(node.position[0], node.position[1] + node.radius + 0.4, node.position[2]) };
      labelEls.push(rec);
      const base = 3200 + (node.labelSeed % 3400);
      const tick = () => {
        if (!alive) return;
        rec.dim = true;
        timers.push(setTimeout(() => { if (!alive) return; tx.textContent = LABELS[Math.floor(Math.random() * LABELS.length)]; rec.dim = false; }, 180));
        timers.push(setTimeout(tick, base + Math.random() * 2600));
      };
      timers.push(setTimeout(tick, base + Math.random() * 1500));
    });
  }

  // Pointer parallax (desktop pointer only).
  const mouseRaw = { x: 0, y: 0 }, mouse = { x: 0, y: 0 };
  if (!matchMedia('(pointer: coarse)').matches) {
    const mm = e => { mouseRaw.x = e.clientX / innerWidth * 2 - 1; mouseRaw.y = -(e.clientY / innerHeight * 2 - 1); };
    addEventListener('mousemove', mm); cleanups.push(() => removeEventListener('mousemove', mm));
  }

  const resize = () => {
    if (!renderer) return;
    const w = sceneWindow.offsetWidth || innerWidth, h = sceneWindow.offsetHeight || innerHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  resize(); addEventListener('resize', resize); cleanups.push(() => removeEventListener('resize', resize));

  // Everything below derives from the one document position the momentum controller moves.
  let d = 0, last = performance.now(), bb = null;
  const pos = new THREE.Vector3(), look = new THREE.Vector3(), proj = new THREE.Vector3();
  const clock = new THREE.Clock();
  const frame = now => {
    raf = 0;
    if (!alive) return;
    const dt = Math.min(0.05, Math.max(0, (now - last) / 1000)); last = now;
    const w = document.documentElement.clientWidth || innerWidth, h = innerHeight;
    const target = typeof window.__elJourneyD === 'number' ? window.__elJourneyD : -section.getBoundingClientRect().top;
    d = Math.max(0, target);

    const journeyLen = Math.max(1, section.offsetHeight - 2 * h);
    const p = clamp01(d / journeyLen);
    const dockT = smoother((d - journeyLen) / h);
    const fit = w * (mobile ? 0.9 : 0.86) / wm.width;
    const start = Math.max(w / wm.hole.width, h / wm.hole.height) * 36;
    const j = zoomJourney(p, mobile, start / fit);
    zoom.v = j.room;
    const reveal = j.reveal;
    let scale = start * Math.pow(fit / start, reveal);
    const shrink = Math.min(1, scale / start);
    const netA = networkVisibility(Math.max(w, h) * shrink, Math.max(w, h) * fit / start);
    const xF = (w - wm.width * fit) / 2 + wm.hole.x * fit, yF = h * 0.48 + (wm.hole.y - wm.height / 2) * fit;
    let x = w / 2 + (xF - w / 2) * ease(reveal), y = h / 2 + (yF - h / 2) * ease(reveal);
    if (dockT > 0) {
      // Continue the same shrink into the header slot's resting position,
      // measured from the rendered slot glyphs so both copies coincide exactly.
      const sp = slot.querySelector('path'), r = sp ? sp.getBoundingClientRect() : slot.getBoundingClientRect(), c = content.getBoundingClientRect();
      if (!bb) { try { bb = gLetters.querySelector('path').getBBox(); } catch (e) {} if (!bb || !bb.width) bb = { x: ink.x1, y: ink.y1, width: inkW }; }
      const sS = r.width / bb.width, xs = r.left + (wm.hole.x - bb.x) * sS, ys = r.top - c.top + (wm.hole.y - bb.y) * sS;
      scale = fit * Math.pow(sS / fit, dockT); x = xF + (xs - xF) * dockT; y = yF + (ys - yF) * dockT;
    }
    const tf = `translate(${x} ${y}) scale(${scale}) translate(${-wm.hole.x} ${-wm.hole.y})`;
    gOpen.setAttribute('transform', tf); gLetters.setAttribute('transform', tf);
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    overlayHost.style.visibility = reveal > 0 && !(d >= journeyLen + h - 1) ? 'visible' : 'hidden';
    field.setAttribute('opacity', String(1 - dockT));
    backdrop.style.opacity = String(1 - dockT);
    const done = d >= journeyLen + h - 1;
    stage.style.visibility = done ? 'hidden' : 'visible';
    slot.style.opacity = done ? '1' : '0';

    sceneWindow.style.transform = `translate(${x - w / 2}px, ${y - h / 2}px) scale(${shrink})`;
    sceneWindow.style.opacity = String(netA);
    if (pill) pill.style.opacity = String(1 - dockT);
    if (hint) hint.style.opacity = String(1 - ease(p / 0.08));
    if (skip) { skip.style.opacity = String(1 - dockT); skip.style.visibility = dockT > 0.6 ? 'hidden' : 'visible'; }
    const labelsOn = zoom.v > 0.32 && labelEls.length > 0;
    if (note) note.style.opacity = String(labelsOn ? netA * (1 - dockT) : 0);

    const sceneActive = renderer && netA > 0 && !document.hidden;
    if (sceneActive) {
      const ratio = roomZoomRatio(mobile), z = zoom.v;
      const ez = (Math.pow(ratio, z) - 1) / (ratio - 1);
      const pk = 1 - Math.pow(0.001, dt * 0.3);
      mouse.x += (mouseRaw.x - mouse.x) * pk; mouse.y += (mouseRaw.y - mouse.y) * pk;
      const par = 1 - ez;
      pos.lerpVectors(nearPos, FAR_POS, ez); look.lerpVectors(nearLook, FAR_LOOK, ez);
      pos.x += mouse.x * 0.25 * par; pos.y += mouse.y * 0.15 * par; look.x += mouse.x * 0.6 * par; look.y += mouse.y * 0.4 * par;
      camera.position.copy(pos); camera.lookAt(look); camera.updateMatrixWorld();
      const t = clock.getElapsedTime();
      for (const u of updaters) u(z, t);
      renderer.render(scene, camera);
      if (labelEls.length) {
        const lw = sceneWindow.offsetWidth, lh = sceneWindow.offsetHeight;
        for (const L of labelEls) {
          proj.copy(L.v).project(camera);
          const vis = labelsOn && proj.z < 1 && Math.abs(proj.x) < 1.2 && Math.abs(proj.y) < 1.2;
          L.el.style.opacity = vis ? (L.dim ? '0.45' : '1') : '0';
          if (vis) L.el.style.transform = `translate(${((proj.x + 1) / 2 * lw).toFixed(1)}px, ${((1 - proj.y) / 2 * lh).toFixed(1)}px) translate(-50%, -50%)`;
        }
      }
    }
    if (running) raf = requestAnimationFrame(frame);
  };
  const kick = () => { if (!raf && alive) { last = performance.now(); raf = requestAnimationFrame(frame); } };
  const io = new IntersectionObserver(([e]) => { running = e.isIntersecting; if (running) kick(); else frame(performance.now()); }, { rootMargin: '50% 0px' });
  io.observe(section);
  const onScroll = () => kick();
  addEventListener('scroll', onScroll, { passive: true }); cleanups.push(() => removeEventListener('scroll', onScroll));
  const vis = () => kick(); document.addEventListener('visibilitychange', vis); cleanups.push(() => document.removeEventListener('visibilitychange', vis));

  const endY = () => section.offsetTop + section.offsetHeight - innerHeight;
  const skipTo = () => { if (momentum) momentum.stop(); scrollTo({ top: endY(), behavior: 'instant' }); kick(); };
  momentum = installMomentum({ section, isReady });
  cleanups.push(() => momentum.destroy());
  // Deep links open their content immediately.
  if (location.hash && location.hash.length > 1 && location.hash !== '#top') {
    requestAnimationFrame(() => { const el = document.getElementById(location.hash.slice(1)); skipTo(); if (el && el !== content) scrollTo({ top: el.getBoundingClientRect().top + scrollY - 24, behavior: 'instant' }); });
  }
  kick();

  return {
    skip: skipTo,
    destroy() {
      alive = false; cancelAnimationFrame(raf); io.disconnect(); timers.forEach(clearTimeout); cleanups.forEach(f => f());
      labelEls.forEach(L => L.el.remove()); overlayHost.innerHTML = '';
      if (renderer) {
        scene.traverse(ob => { if (ob.geometry) ob.geometry.dispose(); if (ob.material) ob.material.dispose(); });
        renderer.dispose(); renderer.forceContextLoss && renderer.forceContextLoss(); renderer.domElement.remove();
      }
      stage.style.visibility = ''; slot.style.opacity = '1';
    },
  };
}
