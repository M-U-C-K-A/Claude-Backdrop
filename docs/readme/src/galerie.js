/**
 * Galerie: the gallery panel of claude-backdrop as a rack of five framed
 * canvases on edge. Each canvas says which painting it is by its composition:
 * Socrates' bed under a high wall, the three arches of the Horatii, the
 * palace colonnade of Pandemonium, the receding vaults of the School of
 * Athens, and a bare canvas for a picture of your own. The canvas under the
 * pointer stands up and lifts; the others lean away, staggered outwards from
 * it. The slider is the stagger, in ms.
 */
const {
  Cam, clamp, facing, fit, hull, open, poly, proj, rad, ringAt, rrect, run, seg,
  tdone, tset, tval, tween, disposer, mk, pointer, reflect, register,
} = HL;

const N = 5, W = 86, H = 60, G = 17, TK = 2.2, IN = 6;
const REST = -14, BACK = -26, FWD = 22, LIFT = 15, CURRENT = 2, RISE = 6;
const X0 = -6, X1 = W + 6, Y0 = -10, Y1 = (N - 1) * G + 10, WH = 16, WR = 6, WT = 2.4;
const NAMES = ["socrate", "horaces", "pandémonium", "athènes", "la tienne"];
// back to front: your own canvas, Socrates, Athens (the one on screen), the Horatii, Pandemonium
const ORDER = [4, 0, 3, 1, 2];

const LR = (pts) => (pts[0][0] <= pts[pts.length - 1][0] ? pts : pts.slice().reverse());

/** The rack, which never moves: `far` is painted before the canvases, `near` after them. */
function rack(P, front, outer, inner) {
  const far = [
    [poly(hull(ringAt(P, outer, 0).concat(ringAt(P, outer, WH)))), "sil"],
    [poly(ringAt(P, inner, WH)), "nf"],
    [open(ringAt(P, run(inner, (q) => !front(q)), 2.5)), "nf lo"],
  ];
  const iF = LR(ringAt(P, run(inner, front), WH)), oT = LR(ringAt(P, run(outer, front), WH)), oB = LR(ringAt(P, run(outer, front), 0));
  const near = [
    [poly([...iF, oT[oT.length - 1], ...oB.slice().reverse(), oT[0]]), "fo"],
    [open(oT), "nf lo"],
    [open(iF), "nf"],
    [open([oT[0], ...oB, oT[oT.length - 1]]), "nf sil"],
  ];
  return { far, near };
}

/** The composition of painting k, as polylines in the canvas plane (u across, v up). */
function motif(k) {
  const L = IN + 3, R = W - IN - 3, B = IN + 3, T = H - IN - 3;
  const arch = (cx, w, v0, v1) => {
    const pts = [[cx - w, v0], [cx - w, v1]];
    for (let s = 1; s < 8; s++) { const a = Math.PI - (s / 8) * Math.PI; pts.push([cx + w * Math.cos(a), v1 + w * Math.sin(a)]); }
    return pts.concat([[cx + w, v1], [cx + w, v0]]);
  };
  if (k === 0) return [[[L, 20], [R - 18, 20]], [[L + 6, 20], [L + 6, 27], [R - 24, 27], [R - 24, 20]], [[R - 12, B], [R - 12, 36]], [[L, 40], [R, 40]]];
  if (k === 1) return [arch(26, 9, B, 30), arch(43, 9, B, 30), arch(60, 9, B, 30)];
  if (k === 2) {
    const cols = [];
    for (let i = 0; i < 7; i++) cols.push([[L + 8 + i * 9.5, 20], [L + 8 + i * 9.5, 33]]);
    return [[[L, 20], [R, 20]], [[L + 4, 33], [R - 4, 33]], [[L + 10, 37], [W / 2, 43], [R - 10, 37]], ...cols];
  }
  if (k === 3) return [arch(W / 2, 26, B, 22), arch(W / 2, 17, B + 4, 24), arch(W / 2, 9, B + 8, 26)];
  return [];
}

/** Canvas i leaning th degrees (negative leans back), lifted by `lift`. */
function pose(P, i, th, lift) {
  const yb = i * G, s = Math.sin(rad(th)), c = Math.cos(rad(th));
  const w = (u, v) => P(u, yb + v * s, v * c + lift);
  const wb = (u, v) => P(u, yb + v * s - TK * c, v * c + TK * s + lift);
  const outer = rrect(0, 0, W, H, 3, 4), inner = rrect(IN, IN, W - IN, H - IN, 1.4, 3);
  return {
    back: poly(outer.map((q) => wb(q.u, q.v))),
    face: poly(outer.map((q) => w(q.u, q.v))),
    picture: poly(inner.map((q) => w(q.u, q.v))),
    motif: motif(ORDER[i]).map((line) => open(line.map(([u, v]) => w(u, v)))).join(""),
  };
}

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let stag = value;

  const C = Cam(45, 0.5, 1.58);
  fit(C, [[X0, Y0, 0], [X1, Y1, -8], [X1, Y0, 0], [X0, Y1, 0], [X0, Y0, H], [X1, Y0, H + LIFT]], 200, 166);
  const P = proj(C), front = facing(C);
  const outer = rrect(X0, Y0, X1, Y1, WR, 6), inner = rrect(X0 + WT, Y0 + WT, X1 - WT, Y1 - WT, WR - WT, 6);
  const paths = rack(P, front, outer, inner);

  const g = mk("g", {}, svg);
  reflect(svg, g, P, front, outer, 0, 14);
  for (const [d, cls] of paths.far) mk("path", { d, class: cls }, g);

  const cards = [];
  for (let i = 0; i < N; i++) {
    const grp = mk("g", {}, g);
    const back = mk("path", { class: "lo" }, grp), face = mk("path", { class: "sil" }, grp);
    const picture = mk("path", { class: "nf lo" }, grp), art = mk("path", { class: "nf" }, grp);
    // at rest the painting on screen stands half up, the others lean away from it
    const th = i < CURRENT ? BACK : i > CURRENT ? FWD : 0;
    cards.push({ back, face, picture, art, a: tween(th), z: tween(i === CURRENT ? RISE : 0), last: "" });
  }
  for (const [d, cls] of paths.near) mk("path", { d, class: cls }, g);

  // hit bands along the RESTING top edges: they never move, and nothing draws them
  const top = (i) => P(W / 2, i * G + H * Math.sin(rad(REST)), H * Math.cos(rad(REST)));
  const c0 = top(0), c1 = top(1), d = [c1[0] - c0[0], c1[1] - c0[1]];
  const px0 = P(0, 0, 0), px1 = P(1, 0, 0), ex = [px1[0] - px0[0], px1[1] - px0[1]];
  const HALF = W / 2 + 6, det = d[0] * ex[1] - d[1] * ex[0];
  function hit([x, y]) {
    const qx = x - c0[0], qy = y - c0[1];
    const s = (qx * ex[1] - qy * ex[0]) / det, r = (d[0] * qy - d[1] * qx) / det;
    if (Math.abs(r) > HALF || s < -0.5 || s > N + 1) return -1;
    return clamp(Math.round(s), 0, N - 1);
  }

  function draw(i, th, lift) {
    const cd = cards[i], key = th.toFixed(3) + "|" + lift.toFixed(3);
    if (key === cd.last) return;
    cd.last = key;
    const q = pose(P, i, th, lift);
    cd.back.setAttribute("d", q.back);
    cd.face.setAttribute("d", q.face);
    cd.picture.setAttribute("d", q.picture);
    cd.art.setAttribute("d", q.motif || "M0 0");
  }

  const B = register(stage, (_dt, now) => {
    let moving = false;
    cards.forEach((cd, i) => { draw(i, tval(cd.a, now), tval(cd.z, now)); if (!tdone(cd.a, now) || !tdone(cd.z, now)) moving = true; });
    return moving;
  });
  bag.add(B.unregister);

  let act = -1;
  // at rest the painting on screen keeps the bright edge; the pointer's choice takes it
  const light = (a) => cards.forEach((cd, i) => cd.face.classList.toggle("hi", i === (a < 0 ? CURRENT : a)));
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    const pick = a < 0 ? CURRENT : a;
    cards.forEach((cd, i) => {
      const delay = Math.abs(i - from) * stag;
      const th = i < pick ? BACK : i > pick ? FWD : 0;
      tset(cd.a, th, now, delay); tset(cd.z, i !== pick ? 0 : a < 0 ? RISE : LIFT, now, delay);
    });
    light(a);
    read.textContent = a < 0 ? "rest" : NAMES[ORDER[a]];
    B.wake();
  }
  light(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { stag = v; },
    destroy: bag.dispose,
  };
}

hairline({
  name: "galerie",
  means: "The gallery panel as a rack of five canvases: the one under the pointer stands up, the others lean away in turn.",
  rules: [1, 2, 8, 10],
  range: [0, 40, 90],
  mount,
});
