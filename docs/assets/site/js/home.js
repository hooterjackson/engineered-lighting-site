// Home page glue: mounts the opening journey and the den scene, and keeps the
// loading hint and the den HUD in step with them. Ported from the Front Door
// prototype's page logic. three.js and the scans load after first paint, via
// the scene modules' dynamic imports.
const $ = sel => document.querySelector(sel);
const el = {
  section: $('#opening'), stage: $('.opening__stage'), backdrop: $('.opening__backdrop'),
  sceneWindow: $('.opening__scene'), canvasHost: $('.opening__canvas'), labelsLayer: $('.opening__labels'),
  overlayHost: $('.opening__overlay'), slot: $('.wordmark'), content: $('#overview'),
  hint: $('.opening__hint'), skip: $('.skip-pill'), note: $('.opening__note'),
  denHost: $('.den__scene'), denLabels: $('.den__labels'), hudBeat: $('.hud__beat'), hudClock: $('.hud__clock'),
};

const reducedMotion = () => { try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; } };
// Set by the inline script in index.html before first paint (?intro=0, reduced motion).
const introOn = () => document.documentElement.dataset.intro === 'on';

let assets;
const loadAssets = () => assets || (assets = fetch(new URL('../large-assets.json', import.meta.url))
  .then(r => (r.ok ? r.json() : {})).catch(() => ({})));

const mmss = n => String(Math.floor(n / 60)).padStart(2, '0') + ':' + String(n % 60).padStart(2, '0');

// ---- Opening hint ----
const setHint = s => {
  el.hint.textContent = s.status === 'error' ? 'Scan unavailable · scroll for the overview'
    : s.status === 'loading' ? 'Loading the apartment scan · ' + (s.pct || 0) + '%' : 'Scroll';
};

// ---- Den HUD: beat text, then the loop clock (or load progress / error) ----
const den = { status: 'loading', pct: 0, hud: null };
const renderHud = () => {
  el.hudBeat.textContent = den.hud ? den.hud.beat : 'Empty · dusk';
  el.hudClock.textContent = den.status === 'error' ? 'Scan unavailable'
    : den.status !== 'ready' ? den.pct + '%' : den.hud ? mmss(den.hud.t) : '';
};

let mobile = innerWidth < 720;
let journey = null, denScene = null, tok = 0, dtok = 0;

async function mountJourney() {
  const token = ++tok;
  if (journey) { journey.destroy(); journey = null; }
  const mod = await import('./opening-journey.js');
  if (token !== tok) return;
  if (!introOn()) { await mod.fillWordmark(el.slot); el.slot.style.opacity = '1'; return; }
  const a = await loadAssets();
  if (token !== tok) return;
  const j = await mod.mountOpening({
    section: el.section, stage: el.stage, backdrop: el.backdrop, sceneWindow: el.sceneWindow,
    canvasHost: el.canvasHost, labelsLayer: el.labelsLayer, overlayHost: el.overlayHost, slot: el.slot,
    content: el.content, hint: el.hint, skip: el.skip, note: el.note, pill: null,
    mobile, labels: true, clouds: a.clouds,
    onStatus: s => { if (token === tok) setHint(s); },
  });
  if (token !== tok) { j.destroy(); return; }
  journey = j;
}

async function mountDen() {
  const token = ++dtok;
  if (denScene) { denScene.destroy(); denScene = null; }
  const [mod, a] = await Promise.all([import('./den-hero.js'), loadAssets()]);
  if (token !== dtok) return;
  const d = await mod.mountDenHero({
    host: el.denHost, labelsLayer: el.denLabels, mobile,
    view: 'overview', beams: true, labels: false, frame: 'background', still: reducedMotion(),
    scan: a.den,
    onStatus: s => { if (token === dtok) { den.status = s.status; den.pct = s.pct || 0; renderHud(); } },
    onHud: hud => { if (token === dtok) { den.hud = hud; renderHud(); } },
  });
  if (token !== dtok) { d.destroy(); return; }
  denScene = d;
}

el.skip.addEventListener('click', e => { if (journey) { e.preventDefault(); journey.skip(); } });
el.slot.addEventListener('click', e => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'instant' }); });

// Phones get the mobile camera, lighter point counts and the mobile cloud.
addEventListener('resize', () => {
  const m = innerWidth < 720;
  if (m !== mobile) { mobile = m; mountJourney(); mountDen(); }
});

renderHud();
requestAnimationFrame(() => requestAnimationFrame(() => { mountJourney(); mountDen(); }));
