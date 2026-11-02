// Victoria den hero: the real den scan, four virtual fixtures (spot + down +
// six radial segments each) and one synthetic, anonymous tracked person
// following a scripted evening. Simplified direct-light model:
//   E = Σ channels  candela · angular · max(N·L,0) / max(d², .01)
//   radiance = albedo · E / π, then exposure and 1 − e^(−x)
// No visibility rays, no bounce, no receiver arrays. Coordinates are the
// pack's own: right-handed, Z-up, metres, floor at z = 0.
import * as THREE from '../vendor/three/three.module.min.js';
// Asset paths (data/, scans/) resolve against docs/assets/site/.
const SITE = new URL('../', import.meta.url);

const clamp01 = n => Math.max(0, Math.min(1, n));
const ease = n => { const t = clamp01(n); return t * t * (3 - 2 * t); };
const easeIO = n => { const t = clamp01(n); return t * t * t * (t * (t * 6 - 15) + 10); };
const angLerp = (a, b, t) => { let d = ((b - a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI; return a + d * t; };

// ── Den geometry (pack local-2026-10-15-den-view-r1-v4, equipment revision 2) ─
const WALLS = [[2.979687079, 0.666236254], [6.725373553, 0.717248738], [6.645060137, 5.330365338], [2.899373664, 5.279352854]];
const CENTER = new THREE.Vector3(4.81, 3.0, 0.85);
// Approximate saved socket anchors; the display pivot sits 0.14 m below each.
const FIXTURES = [
  { id: 'F-01', pos: [3.3390953353, 4.8280990233, 2.4514238824] },
  { id: 'F-02', pos: [6.2217, 4.8420, 2.4240] },
  { id: 'F-03', pos: [6.2725, 1.1937, 2.3453] },
  { id: 'F-04', pos: [3.4157, 1.1548, 2.3720] },
].map(f => ({ ...f, origin: new THREE.Vector3(f.pos[0], f.pos[1], f.pos[2] - 0.14) }));
const SOFA = new THREE.Vector3(6.193892724376128, 2.587017163388598, 0.4953009593170319);   // owner sofa mark (v4)
const DESK = new THREE.Vector3(4.454342735777487, 5.056241814461323, 0.42298728069519176);  // desk target2 centre (v3 binding)
// Editorial body placements (not observed poses).
const SOFA_HIPS = [6.08, SOFA.y], DESK_HIPS = [4.55, 4.22];

// ── Lit conventions (simplified) ───────────────────────────────────────────
const SPOT_O = 16 * Math.PI / 180, SPOT_I = 7.2 * Math.PI / 180;      // 0.8·FWHM20, penumbra .55
const DOWN_O = 50 * Math.PI / 180, DOWN_I = 22 * Math.PI / 180;       // assumed wide downlight
const LM = { spot: 450, down: 350, radial: 120 };
const cdPerLm = (o, i) => 1 / (2 * Math.PI * (1 - Math.cos((o + i) / 2)));
const RAD_CD_PER_LM = 1 / (2 * Math.PI / 3);                            // cos² lobe
const perceptual = level => { const L = 100 * level; return L > 8 ? ((L + 16) / 116) ** 3 : L / (24389 / 27); };
function cctToLinear(T) {
  T = Math.max(1667, Math.min(25000, T));
  const x = T < 4000 ? -0.2661239e9 / T ** 3 - 0.2343589e6 / T ** 2 + 0.8776956e3 / T + 0.179910
    : -3.0258469e9 / T ** 3 + 2.1070379e6 / T ** 2 + 0.2226347e3 / T + 0.240390;
  const y = T < 2222 ? -1.1063814 * x ** 3 - 1.34811020 * x ** 2 + 2.18555832 * x - 0.20219683
    : T < 4000 ? -0.9549476 * x ** 3 - 1.37418593 * x ** 2 + 2.09137015 * x - 0.16748867
      : 3.0817580 * x ** 3 - 5.87338670 * x ** 2 + 3.75112997 * x - 0.37001483;
  const X = x / y, Z = (1 - x - y) / y;
  return new THREE.Vector3(Math.max(0, 3.2406 * X - 1.5372 - 0.4986 * Z), Math.max(0, -0.9689 * X + 1.8758 + 0.0415 * Z), Math.max(0, 0.0557 * X - 0.2040 + 1.0570 * Z));
}
// Radial segment k points at azimuth k·60°, slightly below horizontal.
// Mounting alignment is unknown, so segment 0 → +X is an assumption.
const SEG_DIRS = [0, 1, 2, 3, 4, 5].map(k => new THREE.Vector3(Math.cos(k * Math.PI / 3), Math.sin(k * Math.PI / 3), -0.35).normalize());

// ── Skeleton (synthetic, 14 joints) ────────────────────────────────────────
// Joint order: head, neck, lSh, rSh, lEl, rEl, lWr, rWr, lHip, rHip, lKn, rKn, lAn, rAn
const BONES = [[0, 1], [1, 2], [1, 3], [2, 4], [4, 6], [3, 5], [5, 7], [2, 8], [3, 9], [8, 9], [8, 10], [10, 12], [9, 11], [11, 13]];
const STAND = { hz: .93, tp: .03, lt: 0, rt: 0, lk: .03, rk: .03, ls: .06, rs: .06, le: .18, re: .18, ab: .10, hd: 0 };
const CROUCH = { hz: .66, tp: .55, lt: 1.05, rt: 1.05, lk: .85, rk: .85, ls: .45, rs: .45, le: .3, re: .3, ab: .14, hd: .02 };
const SIT_READ = { hz: .575, tp: -.22, lt: 1.42, rt: 1.42, lk: 1.35, rk: 1.35, ls: .35, rs: .35, le: 1.55, re: 1.55, ab: .12, hd: .05 };
const SIT_DESK = { hz: .53, tp: .12, lt: 1.5, rt: 1.5, lk: 1.45, rk: 1.45, ls: .62, rs: .62, le: .88, re: .88, ab: .16, hd: .03 };
const mixP = (a, b, t) => { const o = {}; for (const k in a) o[k] = a[k] + (b[k] - a[k]) * t; return o; };
function walkP(phi, a) {
  const s = Math.sin(phi), c = Math.cos(phi);
  return { hz: .93 - .02 * a * Math.abs(Math.cos(2 * phi)), tp: .03 + .05 * a, lt: .36 * a * s, rt: -.36 * a * s,
    lk: .05 + .6 * a * Math.max(0, c), rk: .05 + .6 * a * Math.max(0, -c), ls: .06 - .3 * a * s, rs: .06 + .3 * a * s, le: .25, re: .25, ab: .1, hd: 0 };
}
function fk(P) {
  const td = [Math.sin(P.tp), Math.cos(P.tp)];
  const pel = [0, 0, P.hz], neck = [td[0] * .59, 0, P.hz + td[1] * .59];
  const head = [neck[0] + td[0] * .14 + P.hd, 0, neck[2] + td[1] * .14];
  const sh = s => [neck[0] - td[0] * .04, s * .19, neck[2] - td[1] * .04];
  const hip = s => [pel[0], s * .1, pel[2]];
  const leg = (h, a, k) => { const kn = [h[0] + .43 * Math.sin(a), h[1], h[2] - .43 * Math.cos(a)], b = a - k; return [kn, [kn[0] + .42 * Math.sin(b), h[1], kn[2] - .42 * Math.cos(b)]]; };
  const arm = (s, side, a, e, ab) => { const ca = Math.cos(ab), el = [s[0] + .3 * Math.sin(a) * ca, s[1] + side * .3 * Math.sin(ab), s[2] - .3 * Math.cos(a) * ca], b = a + e; return [el, [el[0] + .27 * Math.sin(b) * ca, el[1] - side * .04, el[2] - .27 * Math.cos(b) * ca]]; };
  const lS = sh(1), rS = sh(-1), lH = hip(1), rH = hip(-1);
  const [lE, lW] = arm(lS, 1, P.ls, P.le, P.ab), [rE, rW] = arm(rS, -1, P.rs, P.re, P.ab);
  const [lK, lA] = leg(lH, P.lt, P.lk), [rK, rA] = leg(rH, P.rt, P.rk);
  return [head, neck, lS, rS, lE, rE, lW, rW, lH, rH, lK, rK, lA, rA];
}

// Smoothed path: Chaikin ×3 + arc length.
function makeCurve(pts) {
  let p = pts.map(q => [q[0], q[1]]);
  for (let it = 0; it < 3; it++) { const o = [p[0]]; for (let i = 0; i < p.length - 1; i++) { const a = p[i], b = p[i + 1]; o.push([a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25], [a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75]); } o.push(p[p.length - 1]); p = o; }
  const acc = [0]; for (let i = 1; i < p.length; i++) acc.push(acc[i - 1] + Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]));
  const len = acc[acc.length - 1];
  const at = s => { s = Math.max(0, Math.min(len, s)); let i = 1; while (i < acc.length - 1 && acc[i] < s) i++; const t = (s - acc[i - 1]) / Math.max(1e-6, acc[i] - acc[i - 1]); return [p[i - 1][0] + (p[i][0] - p[i - 1][0]) * t, p[i - 1][1] + (p[i][1] - p[i - 1][1]) * t]; };
  const heading = s => { const a = at(s - .25), b = at(s + .25); return Math.atan2(b[1] - a[1], b[0] - a[0]); };
  return { len, at, heading };
}

// ── Scripted evening ──────────────────────────────────────────────────────
function buildStory(paths) {
  const A = makeCurve(paths.enterToSofa), B = makeCurve(paths.sofaToDesk), C = makeCurve(paths.deskToExit);
  const v = 0.72, seg = [];
  let t = 4.5;
  const push = (type, dur, d) => { seg.push({ type, t0: t, t1: t + dur, ...d }); t += dur; };
  push('appear', .6, { at: A.at(0), h: A.heading(0), label: 'Entering' });
  push('walk', A.len / v, { curve: A, label: 'Entering' });
  push('turn', .8, { at: A.at(A.len), h0: A.heading(A.len), h1: Math.PI, label: 'Sitting down' });
  push('sit', 1.5, { from: A.at(A.len), to: SOFA_HIPS, h: Math.PI, pose: SIT_READ, label: 'Sitting down' });
  const sofaSeated = t;
  push('seated', 22.6 - t, { at: SOFA_HIPS, h: Math.PI, pose: SIT_READ, act: 'read', label: 'Reading' });
  push('stand', 1.4, { from: SOFA_HIPS, to: B.at(0), h: Math.PI, pose: SIT_READ, label: 'Standing up' });
  push('turn', .6, { at: B.at(0), h0: Math.PI, h1: B.heading(0), label: 'Walking' });
  push('walk', B.len / v, { curve: B, label: 'Walking' });
  push('turn', .7, { at: B.at(B.len), h0: B.heading(B.len), h1: Math.PI / 2, label: 'Sitting down' });
  push('sit', 1.5, { from: B.at(B.len), to: DESK_HIPS, h: Math.PI / 2, pose: SIT_DESK, label: 'Sitting down' });
  const deskSeated = t;
  push('seated', 36 - t, { at: DESK_HIPS, h: Math.PI / 2, pose: SIT_DESK, act: 'type', label: 'Working' });
  push('stand', 1.4, { from: DESK_HIPS, to: C.at(0), h: Math.PI / 2, pose: SIT_DESK, label: 'Standing up' });
  push('turn', .6, { at: C.at(0), h0: Math.PI / 2, h1: C.heading(0), label: 'Leaving' });
  push('walk', C.len / v, { curve: C, label: 'Leaving' });
  push('vanish', .6, { at: C.at(C.len), h: C.heading(C.len), label: 'Leaving' });
  const gone = t;
  const T = { enter: 4.5, sofaSeated, readOn: sofaSeated + 3, sofaStand: 22.6, deskSeated, workOn: deskSeated + .5, deskStand: 36, gone, loop: Math.ceil(gone + 4.5) };
  return { seg, T };
}
function personAt(story, t, now) {
  const s = story.seg.find(g => t >= g.t0 && t < g.t1);
  if (!s) return null;
  const u = (t - s.t0) / (s.t1 - s.t0);
  let root, h, P, ground = 1, alpha = 1;
  const breathe = .008 * Math.sin(now * 1.7);
  if (s.type === 'walk') {
    const d = s.curve.len * (u - Math.sin(2 * Math.PI * u) / (2 * Math.PI));
    const speed = 1 - Math.cos(2 * Math.PI * u);
    root = s.curve.at(d); h = s.curve.heading(d); P = walkP(d / 1.3 * 2 * Math.PI, Math.min(1, speed));
  } else if (s.type === 'turn') {
    root = s.at; h = angLerp(s.h0, s.h1, easeIO(u)); P = walkP(u * Math.PI * 2, .25 * Math.sin(Math.PI * u));
  } else if (s.type === 'sit' || s.type === 'stand') {
    const k = s.type === 'sit' ? u : 1 - u, e = easeIO(k);
    root = [s.from[0] + (s.to[0] - s.from[0]) * (s.type === 'sit' ? e : 1 - e), s.from[1] + (s.to[1] - s.from[1]) * (s.type === 'sit' ? e : 1 - e)];
    if (s.type === 'stand') root = [s.to[0] + (s.from[0] - s.to[0]) * e, s.to[1] + (s.from[1] - s.to[1]) * e];
    h = s.h;
    P = e < .5 ? mixP(STAND, CROUCH, easeIO(e * 2)) : mixP(CROUCH, s.pose, easeIO(e * 2 - 1));
    ground = e < .5 ? 1 : 1 - easeIO(e * 2 - 1);
  } else if (s.type === 'seated') {
    root = s.at; h = s.h; P = { ...s.pose, tp: s.pose.tp + breathe }; ground = 0;
    if (s.act === 'read') { const turn = Math.max(0, Math.sin((t - s.t0) * 2 * Math.PI / 6)) ** 8; P.re += .5 * turn; P.rs += .15 * turn; }
    if (s.act === 'type') { P.le += .05 * Math.sin(now * 9); P.re += .05 * Math.sin(now * 9 + 1.7); }
  } else {
    root = s.at; h = s.h; P = { ...STAND, tp: STAND.tp + breathe }; alpha = s.type === 'appear' ? u : 1 - u;
  }
  const local = fk(P);
  if (ground > 0) { const lift = .08 - Math.min(local[12][2], local[13][2]); for (const j of local) j[2] += lift * ground; }
  const c = Math.cos(h), sn = Math.sin(h);
  const joints = local.map(([x, y, z]) => new THREE.Vector3(root[0] + c * x - sn * y, root[1] + sn * x + c * y, z));
  return { joints, h, root, label: s.label, alpha, seg: s };
}

// ── Channel scene per beat ─────────────────────────────────────────────────
// Each fixture: spot {mode, target|follow, level, cct}, down {level, cct}, radial {level, cct, focus}
function scenePlan(t, T, person) {
  const off = { mode: 'off', level: 0, cct: 2700 };
  const near = person ? FIXTURES.map((f, i) => [i, Math.hypot(f.origin.x - person.root[0], f.origin.y - person.root[1])]).sort((a, b) => a[1] - b[1])[0][0] : -1;
  const P = FIXTURES.map(() => ({ spot: off, down: { level: 0, cct: 2700 }, rad: { level: 0, cct: 2700, focus: null } }));
  const chest = person ? person.joints[1].clone().add(new THREE.Vector3(0, 0, -.22)) : null;
  if (t < T.enter || t >= T.gone) { P.forEach(p => p.rad = { level: .22, cct: 2400, focus: null }); return P; }   // empty: low dusk glow
  P.forEach(p => p.down = { level: .32, cct: t >= T.deskSeated && t < T.deskStand ? 3500 : 2900 });     // occupied: room-wide down fill
  if (t < T.sofaSeated) {                          // entering: occupied ambient, path-following spot
    P.forEach(p => p.rad = { level: .62, cct: 3000, focus: chest });
    P[3].spot = { mode: 'follow', level: .35, cct: 3000, name: 'Following A' };
    if (near >= 0) P[near].down = { level: .55, cct: 3000 };
  } else if (t < T.sofaStand) {                    // sofa: warm, sofa-weighted wash; reading spot after hold-on
    P.forEach((p, i) => p.rad = { level: i === 1 || i === 2 ? .66 : .46, cct: 2700, focus: SOFA });
    P[2].down = { level: .3, cct: 2700 };
    if (t >= T.readOn) P[2].spot = { mode: 'point', target: SOFA, level: .8, cct: 2700, name: 'Sofa' };
  } else if (t < T.deskSeated) {                   // walking to the desk
    P.forEach(p => p.rad = { level: .62, cct: 3200, focus: chest });
    if (near >= 0) P[near].down = { level: .5, cct: 3200 };
    P[1].spot = { mode: 'follow', level: .4, cct: 3000, name: 'Following A' };
    if (t < T.sofaStand + 1) P[2].spot = { mode: 'point', target: SOFA, level: .8, cct: 2700, name: 'Sofa' };
  } else if (t < T.deskStand) {                    // working: neutral, desk-weighted, desk spot
    P.forEach((p, i) => p.rad = { level: i === 0 || i === 3 ? .7 : .48, cct: i === 0 || i === 3 ? 4000 : 3500, focus: DESK });
    P[0].down = { level: .5, cct: 4000 };
    if (t >= T.workOn) P[0].spot = { mode: 'point', target: DESK, level: .9, cct: 4000, name: 'Desk' };
  } else if (t < T.gone) {                         // leaving
    P.forEach(p => p.rad = { level: .55, cct: 3000, focus: chest });
    if (t < T.deskStand + 1) P[0].spot = { mode: 'point', target: DESK, level: .3, cct: 4000, name: 'Desk' };
    P[3].spot = { mode: 'follow', level: .3, cct: 3000, name: 'Following A' };
    if (near >= 0) P[near].down = { level: .45, cct: 3000 };
  }
  return P;
}
function beatName(t, T) {
  return t < T.enter ? 'Empty · dusk' : t < T.sofaSeated ? 'Entering' : t < T.readOn ? 'Seated · hold 3 s' : t < T.sofaStand ? 'Reading · sofa'
    : t < T.deskSeated ? 'Walking to the desk' : t < T.deskStand ? 'Working · desk' : t < T.gone ? 'Leaving' : 'Lights settle';
}

// ── Shaders ────────────────────────────────────────────────────────────────
const VERT = `
  attribute float aI; attribute vec3 aN;
  uniform vec3 uFP[4]; uniform vec3 uFD[4]; uniform vec3 uFC[4]; uniform vec3 uDC[4]; uniform vec3 uRC[4];
  uniform float uRL[24];
  uniform vec3 uSeg[6];
  uniform float uCosO, uCosI, uCosDO, uCosDI, uExposure, uFloor, uBase, uSize, uScale;
  uniform vec4 uCut[4];
  varying vec3 vCol;
  void main() {
    vec3 P = position;
    for (int i = 0; i < 4; i++) {
      if (uCut[i].w > 0.5 && P.z > 0.3 && uCut[i].x * P.x + uCut[i].y * P.y - uCut[i].z < 0.32) {
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 0.0; vCol = vec3(0.0); return;
      }
    }
    float alb = pow(aI / 255.0, 2.2);
    vec3 N = normalize(aN + vec3(0.0, 0.0, 1e-4));
    vec3 E = vec3(uFloor);
    for (int i = 0; i < 4; i++) {
      vec3 tl = uFP[i] - P; float d2 = dot(tl, tl); vec3 l = tl * inversesqrt(max(d2, 1e-6)); vec3 dp = -l;
      float ndl = max(dot(N, l), 0.0) / max(d2, 0.01);
      float spot = smoothstep(uCosO, uCosI, dot(uFD[i], dp));
      float down = smoothstep(uCosDO, uCosDI, -dp.z);
      float rad = 0.0;
      for (int k = 0; k < 6; k++) { float w = max(dot(uSeg[k], dp), 0.0); rad += w * w * uRL[i * 6 + k]; }
      E += (uFC[i] * spot + uDC[i] * down + uRC[i] * rad) * ndl;
    }
    vec3 rad = alb * E / 3.14159265;
    vCol = (1.0 - exp(-rad * uExposure)) + vec3(uBase * sqrt(alb));
    vec4 mv = viewMatrix * modelMatrix * vec4(P, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = clamp(uSize * uScale / max(-mv.z, 0.05), 1.0, 5.0);
  }`;
const FRAG = `precision highp float; varying vec3 vCol;
  void main() { if (length(gl_PointCoord - 0.5) > 0.5) discard; gl_FragColor = vec4(vCol, 1.0); }`;
const BEAM_VERT = `varying float vT; void main() { vT = -position.y; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const BEAM_FRAG = `precision highp float; uniform vec3 uColor; uniform float uLevel; varying float vT;
  void main() { float a = uLevel * 0.055 * smoothstep(0.0, 0.12, vT) * (1.0 - 0.6 * vT); gl_FragColor = vec4(uColor * a, a); }`;

export async function mountDenHero(o) {
  const { host, labelsLayer, mobile } = o;
  const status = s => { try { o.onStatus && o.onStatus(s); } catch (e) {} };
  let alive = true, raf = 0, visible = true;
  const cleanups = [];

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: /[?&]capture=1/.test(location.search) });
  } catch (e) { status({ status: 'error' }); return { destroy() {}, set() {} }; }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, mobile ? 1.5 : 2));
  renderer.setClearColor(0x000000, 1);
  renderer.domElement.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block';
  host.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.05, 200);
  camera.up.set(0, 0, 1);

  const uniforms = {
    uFP: { value: FIXTURES.map(f => f.origin.clone()) }, uFD: { value: FIXTURES.map(() => new THREE.Vector3(0, 0, -1)) },
    uFC: { value: FIXTURES.map(() => new THREE.Vector3()) }, uDC: { value: FIXTURES.map(() => new THREE.Vector3()) }, uRC: { value: FIXTURES.map(() => new THREE.Vector3()) },
    uRL: { value: new Array(24).fill(0) }, uSeg: { value: SEG_DIRS },
    uCosO: { value: Math.cos(SPOT_O) }, uCosI: { value: Math.cos(SPOT_I) }, uCosDO: { value: Math.cos(DOWN_O) }, uCosDI: { value: Math.cos(DOWN_I) },
    uExposure: { value: 0.038 }, uFloor: { value: 0.2 }, uBase: { value: 0.17 }, uSize: { value: mobile ? 0.016 : 0.013 }, uScale: { value: 800 },
    uCut: { value: [0, 1, 2, 3].map(() => new THREE.Vector4()) },
  };
  const walls = WALLS.map((a, i) => { const b = WALLS[(i + 1) % 4], ex = b[0] - a[0], ey = b[1] - a[1], L = Math.hypot(ex, ey), nx = -ey / L, ny = ex / L; return { nx, ny, c: nx * a[0] + ny * a[1] }; });

  status({ status: 'loading', pct: 0 });
  const story = buildStory(await (await fetch(new URL('data/den-paths.json', SITE))).json());
  const LOOP = story.T.loop;
  (async () => {
    // The scan entry comes from large-assets.json (passed in by home.js); an
    // unpublished scan takes the error path without a request.
    const scan = o.scan || { present: false };
    if (!scan.present) throw new Error('den cloud not published');
    const res = await fetch(new URL(scan.path, SITE));
    if (!res.ok) throw new Error('den cloud ' + res.status);
    const total = +res.headers.get('content-length') || scan.bytes || 11494964;
    const reader = res.body.getReader(), chunks = []; let got = 0, last = -1;
    for (;;) { const { done, value } = await reader.read(); if (done) break; chunks.push(value); got += value.length; const pct = Math.round(got / total * 100); if (pct !== last) { last = pct; status({ status: 'loading', pct: Math.min(99, pct) }); } }
    const bytes = new Uint8Array(got); let off = 0; for (const c of chunks) { bytes.set(c, off); off += c.length; }
    const buf = bytes.buffer, M = new DataView(buf).getUint32(0, true);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, 4, M * 3), 3));
    g.setAttribute('aI', new THREE.BufferAttribute(new Uint8Array(buf, 4 + M * 12, M), 1, false));
    g.setAttribute('aN', new THREE.BufferAttribute(new Int8Array(buf, 4 + M * 13, M * 3), 3, true));
    g.setDrawRange(0, mobile ? Math.floor(M * 0.55) : M);   // pre-shuffled: any prefix is a uniform subset
    const pts = new THREE.Points(g, new THREE.ShaderMaterial({ uniforms, vertexShader: VERT, fragmentShader: FRAG, depthWrite: true, depthTest: true, blending: THREE.NormalBlending }));
    pts.frustumCulled = false;
    scene.add(pts);
    status({ status: 'ready', pct: 100 });
  })().catch(() => { if (alive) status({ status: 'error' }); });

  // Beams (scattering cue only; they do not light anything) and source glows
  const beamGeo = new THREE.ConeGeometry(1, 1, 40, 1, true); beamGeo.translate(0, -0.5, 0);
  const beams = FIXTURES.map(() => {
    const m = new THREE.Mesh(beamGeo, new THREE.ShaderMaterial({ uniforms: { uColor: { value: new THREE.Vector3(1, 1, 1) }, uLevel: { value: 0 } }, vertexShader: BEAM_VERT, fragmentShader: BEAM_FRAG, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide }));
    m.frustumCulled = false; scene.add(m); return m;
  });
  const glowGeo = new THREE.BufferGeometry(); glowGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(FIXTURES.flatMap(f => f.origin.toArray())), 3));
  glowGeo.setAttribute('aC', new THREE.BufferAttribute(new Float32Array(12), 3));
  const glow = new THREE.Points(glowGeo, new THREE.ShaderMaterial({
    vertexShader: `attribute vec3 aC; varying vec3 vC; void main(){ vC=aC; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); gl_PointSize=${mobile ? 14 : 20}.0; }`,
    fragmentShader: `precision highp float; varying vec3 vC; void main(){ float d=length(gl_PointCoord-0.5); float a=exp(-d*d*28.0); gl_FragColor=vec4(vC*a + vec3(0.35)*smoothstep(0.12,0.0,d), 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  }));
  glow.frustumCulled = false; scene.add(glow);

  // Tracked person: skeleton + smoothed detection box (synthetic)
  const bonePos = new Float32Array(BONES.length * 6), jointPos = new Float32Array(14 * 3);
  const boneGeo = new THREE.BufferGeometry(); boneGeo.setAttribute('position', new THREE.BufferAttribute(bonePos, 3));
  const bones = new THREE.LineSegments(boneGeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthTest: false }));
  const jointGeo = new THREE.BufferGeometry(); jointGeo.setAttribute('position', new THREE.BufferAttribute(jointPos, 3));
  const joints = new THREE.Points(jointGeo, new THREE.PointsMaterial({ color: 0xB8D8FF, size: mobile ? 4 : 5, sizeAttenuation: false, transparent: true, opacity: 0, depthTest: false }));
  const box = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthTest: false }));
  [bones, joints, box].forEach((m, i) => { m.renderOrder = 5 + i; m.frustumCulled = false; scene.add(m); });
  const boxS = { c: new THREE.Vector3(), s: new THREE.Vector3(.6, .6, 1.8), h: 0, init: false };

  // DOM labels
  const mk = (txt) => {
    const el = document.createElement('div');
    el.style.cssText = "position:absolute;left:0;top:0;display:flex;align-items:center;gap:8px;padding:4px 8px;white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:10.5px;line-height:1.3;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.92);background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.12);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);opacity:0;transition:opacity 220ms ease;will-change:transform";
    const a = document.createElement('span'); a.textContent = txt; const b = document.createElement('span'); b.style.color = '#A1A1A1';
    el.append(a, b); labelsLayer.appendChild(el); return { el, sub: b };
  };
  const personLabel = mk('A');
  const fixLabels = FIXTURES.map(f => mk(f.id));

  // Channel state (linear fade → 160 ms smoothing)
  const ch = () => ({ lin: 0, lvl: 0, cct: 2700 });
  const fx = FIXTURES.map(() => ({ cur: SOFA.clone(), from: SOFA.clone(), t0: -1, key: '', spot: ch(), down: ch(), rad: ch(), seg: new Array(6).fill(0).map(ch), name: '' }));
  let exposure = 0.038;
  const opts = { view: o.view || 'overview', beams: o.beams !== false, labels: o.labels !== false, still: !!o.still, frame: o.frame || 'hero' };
  const pointer = { x: 0, y: 0, sx: 0, sy: 0 };
  if (!matchMedia('(pointer: coarse)').matches) {
    const mm = e => { pointer.x = e.clientX / innerWidth * 2 - 1; pointer.y = e.clientY / innerHeight * 2 - 1; };
    addEventListener('mousemove', mm); cleanups.push(() => removeEventListener('mousemove', mm));
  }
  let W = 1, H = 1;
  const resize = () => { W = host.offsetWidth || innerWidth; H = host.offsetHeight || innerHeight; renderer.setSize(W, H, false); };
  resize(); const ro = new ResizeObserver(resize); ro.observe(host); cleanups.push(() => ro.disconnect());

  const tmp = new THREE.Vector3(), q = new THREE.Quaternion(), DOWNV = new THREE.Vector3(0, -1, 0), proj = new THREE.Vector3();
  const place = (L, v, dx, dy, show) => {
    proj.copy(v).project(camera);
    const ok = show && proj.z < 1;
    L.el.style.opacity = ok ? '1' : '0';
    if (ok) L.el.style.transform = `translate(${((proj.x + 1) / 2 * W + dx).toFixed(1)}px, ${((1 - proj.y) / 2 * H + dy).toFixed(1)}px)`;
  };

  function setCamera(time) {
    const aspect = W / H, portrait = aspect < 0.8;
    const el = (portrait ? 55 : opts.view === 'high' ? 60 : 35) * Math.PI / 180;
    const drift = opts.still ? 0 : Math.sin(time * 2 * Math.PI / LOOP) * 4;
    pointer.sx += (pointer.x - pointer.sx) * 0.03; pointer.sy += (pointer.y - pointer.sy) * 0.03;
    const az = (225 + drift + pointer.sx * 2.5) * Math.PI / 180, elv = el - pointer.sy * 0.025;
    const target = portrait ? new THREE.Vector3(5.25, 3.7, 0.6) : CENTER;
    const r = portrait ? 2.35 : 3.1;
    camera.fov = 35; camera.aspect = aspect;
    const vf = camera.fov * Math.PI / 180, hf = 2 * Math.atan(Math.tan(vf / 2) * aspect);
    const dist = r / Math.sin(Math.min(vf, hf) / 2) * (portrait ? 0.95 : 0.82);
    camera.position.set(target.x + dist * Math.cos(elv) * Math.cos(az), target.y + dist * Math.cos(elv) * Math.sin(az), target.z + dist * Math.sin(elv));
    camera.lookAt(target);
    if (opts.frame === 'background') camera.setViewOffset(W, H, portrait ? 0 : -W * 0.12, portrait ? -H * 0.06 : -H * 0.02, W, H);
    else if (!portrait && aspect > 1.2) camera.setViewOffset(W, H, -W * 0.05, H * 0.13, W, H); else if (portrait) camera.setViewOffset(W, H, 0, H * 0.1, W, H); else camera.clearViewOffset();
    camera.updateProjectionMatrix();
    uniforms.uScale.value = H * renderer.getPixelRatio() / (2 * Math.tan(vf / 2));
    // Display cutaway: drop the walls between the camera and the room.
    const cx = Math.cos(az), cy = Math.sin(az);
    walls.forEach((w, i) => uniforms.uCut.value[i].set(w.nx, w.ny, w.c, w.nx * cx + w.ny * cy < -0.3 ? 1 : 0));
  }

  const fade = (c, goal, rate, dt, still) => {
    c.lin = still ? goal : c.lin + Math.sign(goal - c.lin) * Math.min(Math.abs(goal - c.lin), rate * dt);
    const k = still ? 1 : 1 - Math.exp(-dt / 0.16);
    c.lvl += (c.lin - c.lvl) * k;
  };
  let lastNow = performance.now(), t0 = performance.now(), hudAt = 0;
  const STILL_T = story.T.readOn + 4;
  function step(now) {
    raf = 0;
    if (!alive) return;
    const dt = Math.min(0.1, (now - lastNow) / 1000); lastNow = now;
    const secs = Math.max(0, (now - t0) / 1000);
    const t = typeof window.__denT === 'number' ? window.__denT : opts.still ? STILL_T : secs % LOOP;
    const still = opts.still || typeof window.__denT === 'number';
    const p = personAt(story, t, secs);
    const plan = scenePlan(t, story.T, p);
    const settling = t >= story.T.gone;
    const chest = p ? p.joints[1].clone().add(tmp.set(0, 0, -.22)) : null;
    let flux = 0;
    plan.forEach((d, i) => {
      const s = fx[i], f = FIXTURES[i];
      // Spot: 650 ms ease-out-cubic endpoint sweep, direction from the fixed origin.
      const goal = d.spot.mode === 'follow' && chest ? chest : d.spot.mode === 'point' ? d.spot.target : s.cur;
      const key = d.spot.mode === 'off' ? s.key : d.spot.mode + (d.spot.name || '');
      if (key !== s.key) { s.key = key; s.from.copy(s.cur); s.t0 = now; }
      const u = still ? 1 : clamp01((now - s.t0) / 650);
      s.cur.lerpVectors(s.from, goal, 1 - (1 - u) ** 3);
      fade(s.spot, d.spot.level, settling ? 1 / 3 : 1 / 1.5, dt, still);
      fade(s.down, d.down.level, settling ? 1 / 3 : 1 / 2, dt, still);
      const kc = still ? 1 : 1 - Math.exp(-dt / 0.16);
      if (d.spot.mode !== 'off') { s.spot.cct += (d.spot.cct - s.spot.cct) * kc; s.name = d.spot.name; }
      if (d.down.level > 0) s.down.cct += (d.down.cct - s.down.cct) * kc;
      if (d.rad.level > 0) s.rad.cct += (d.rad.cct - s.rad.cct) * Math.min(1, kc * .5);
      // Radial segments weighted toward the scene's focus.
      let radSum = 0;
      s.seg.forEach((c, k) => {
        let g = d.rad.level;
        if (g > 0 && d.rad.focus) {
          const dx = d.rad.focus.x - f.origin.x, dy = d.rad.focus.y - f.origin.y, L = Math.hypot(dx, dy) || 1;
          const w = Math.max(0, SEG_DIRS[k].x * dx / L + SEG_DIRS[k].y * dy / L) / Math.hypot(SEG_DIRS[k].x, SEG_DIRS[k].y);
          g *= .55 + .45 * w;
        }
        fade(c, g, settling ? 1 / 3 : 1 / 2, dt, still);
        const flx = LM.radial * perceptual(c.lvl);
        uniforms.uRL.value[i * 6 + k] = flx * RAD_CD_PER_LM;
        radSum += c.lvl; flux += flx;
      });
      s.rad.lvl = radSum / 6;
      uniforms.uRC.value[i].copy(cctToLinear(s.rad.cct));
      const sf = LM.spot * perceptual(s.spot.lvl), df = LM.down * perceptual(s.down.lvl); flux += sf + df;
      const dir = tmp.subVectors(s.cur, f.origin).normalize();
      uniforms.uFD.value[i].copy(dir);
      const col = cctToLinear(s.spot.cct);
      uniforms.uFC.value[i].copy(col).multiplyScalar(sf * cdPerLm(SPOT_O, SPOT_I));
      uniforms.uDC.value[i].copy(cctToLinear(s.down.cct)).multiplyScalar(df * cdPerLm(DOWN_O, DOWN_I));
      const len = f.origin.distanceTo(s.cur), b = beams[i];
      b.visible = opts.beams && s.spot.lvl > 0.005;
      b.position.copy(f.origin); b.quaternion.copy(q.setFromUnitVectors(DOWNV, dir));
      b.scale.set(len * Math.tan(SPOT_O), len, len * Math.tan(SPOT_O));
      b.material.uniforms.uLevel.value = Math.min(1, s.spot.lvl * 1.4);
      b.material.uniforms.uColor.value.copy(col).normalize();
      const gl = Math.min(1, Math.max(s.spot.lvl, s.down.lvl, s.rad.lvl) * 1.6), gc = cctToLinear(s.spot.lvl > s.rad.lvl ? s.spot.cct : s.rad.cct).normalize().multiplyScalar(gl);
      glowGeo.attributes.aC.setXYZ(i, gc.x, gc.y, gc.z);
    });
    glowGeo.attributes.aC.needsUpdate = true;
    // Simple adaptive exposure: dim scenes open up, spot-lit scenes settle back to .038.
    const expGoal = 0.038 * Math.max(2.1, Math.min(5, Math.sqrt(2400 / (flux + 80))));
    exposure += (expGoal - exposure) * (still ? 1 : 1 - Math.exp(-dt / 1.2));
    uniforms.uExposure.value = exposure;

    // Person overlay
    const pa = p ? p.alpha : 0;
    const k = still ? 1 : 1 - Math.exp(-dt / 0.22);
    bones.material.opacity = 0; joints.material.opacity = 0;
    box.material.opacity += (pa * .85 - box.material.opacity) * k;
    if (p) {
      p.joints.forEach((j, n) => { jointPos[n * 3] = j.x; jointPos[n * 3 + 1] = j.y; jointPos[n * 3 + 2] = j.z; });
      BONES.forEach(([a, b], n) => { bonePos.set([p.joints[a].x, p.joints[a].y, p.joints[a].z, p.joints[b].x, p.joints[b].y, p.joints[b].z], n * 6); });
      boneGeo.attributes.position.needsUpdate = true; jointGeo.attributes.position.needsUpdate = true;
      // Detection box: oriented joint extents + padding, smoothed (no snapping between actions).
      const c = Math.cos(p.h), sn = Math.sin(p.h);
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, z1 = 0;
      for (const j of p.joints) { const dx = j.x - p.root[0], dy = j.y - p.root[1], lx = c * dx + sn * dy, ly = -sn * dx + c * dy; x0 = Math.min(x0, lx); x1 = Math.max(x1, lx); y0 = Math.min(y0, ly); y1 = Math.max(y1, ly); z1 = Math.max(z1, j.z); }
      const pad = .09, cxl = (x0 + x1) / 2, cyl = (y0 + y1) / 2;
      tmp.set(p.root[0] + c * cxl - sn * cyl, p.root[1] + sn * cxl + c * cyl, (z1 + .12) / 2);
      const size = new THREE.Vector3(x1 - x0 + pad * 2, y1 - y0 + pad * 2, z1 + .12);
      const kb = still || !boxS.init ? 1 : 1 - Math.exp(-dt / 0.2);
      boxS.c.lerp(tmp, kb); boxS.s.lerp(size, kb); boxS.h = angLerp(boxS.h, p.h, kb); boxS.init = true;
      box.position.copy(boxS.c); box.scale.copy(boxS.s); box.rotation.set(0, 0, boxS.h);
    } else if (pa === 0 && box.material.opacity < .01) boxS.init = false;
    [bones, joints, box].forEach(m => m.visible = m.material.opacity > 0.01);

    setCamera(secs);
    renderer.render(scene, camera);

    if (p) { personLabel.sub.textContent = p.label; place(personLabel, tmp.set(boxS.c.x, boxS.c.y, boxS.c.z + boxS.s.z / 2), 10, -26, opts.labels); }
    else personLabel.el.style.opacity = '0';
    fixLabels.forEach((L, i) => { L.sub.textContent = fx[i].spot.lvl > 0.02 ? Math.round(fx[i].spot.lvl * 100) + '%' : ''; place(L, FIXTURES[i].origin, 10, -10, opts.labels && !mobile); });

    if (o.onHud && now - hudAt > 250) {
      hudAt = now;
      const radAll = fx.reduce((a, s) => a + s.rad.lvl, 0) / 4;
      o.onHud({ t: Math.floor(t), loop: LOOP, beat: beatName(t, story.T),
        ambient: { level: Math.round(radAll * 100), cct: Math.round(fx.reduce((a, s) => a + s.rad.cct, 0) / 400) * 100 },
        fixtures: fx.map((s, i) => ({ id: FIXTURES[i].id, aim: s.spot.lvl > 0.02 ? s.name : '', spot: Math.round(s.spot.lvl * 100), down: Math.round(s.down.lvl * 100), rad: Math.round(s.rad.lvl * 100) })) });
    }
    if (visible && !document.hidden) raf = requestAnimationFrame(step);
  }
  const kick = () => { if (!raf && alive) { lastNow = performance.now(); raf = requestAnimationFrame(step); } };
  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) kick(); }, { threshold: 0 });
  io.observe(host);
  const vis = () => kick(); document.addEventListener('visibilitychange', vis); cleanups.push(() => document.removeEventListener('visibilitychange', vis));
  kick();

  return {
    set(next) { Object.assign(opts, next); kick(); },
    destroy() {
      alive = false; cancelAnimationFrame(raf); io.disconnect(); cleanups.forEach(f => f());
      personLabel.el.remove(); fixLabels.forEach(L => L.el.remove());
      scene.traverse(ob => { if (ob.geometry) ob.geometry.dispose(); if (ob.material) ob.material.dispose(); });
      renderer.dispose(); renderer.domElement.remove();
    },
  };
}
