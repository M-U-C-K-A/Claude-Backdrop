/**
 * Calques: a Claude window taken apart into the four layers claude-backdrop
 * paints. At the bottom the painting, a plate with three arches on it; above
 * it the veil, a gauze outline with its mesh; then the glass, the sidebar and
 * the side pane, two frosted slabs with the chat column open between them;
 * on top the content: title bar, chat list, bubbles and the composer, floating.
 * The pointer's height picks a layer: it takes the bright edge and the layers
 * above it lift away, staggered outwards. The slider is the gap between layers.
 */
const {
  Cam, clamp, facing, fit, open, poly, proj, rings, prism, ringAt, rrect, run, seg,
  tdone, tset, tval, tween, disposer, mk, place, pointer, register, solid, put,
} = HL;

const W = 124, D = 86, T = 2.6, LIFT = 14;
const NAMES = ["tableau", "voile", "verre", "fenêtre"];
// the content layer, as [x0, y0, x1, y1, r, height]: title bar, chat list, bubbles, composer
const CONTENT = [
  [0, 0, W, 9, 3, 2.2],
  [5, 16, 26, 21, 2, 1.6], [5, 25, 22, 30, 2, 1.6], [5, 34, 24, 39, 2, 1.6], [5, 43, 20, 48, 2, 1.6],
  [62, 16, 94, 27, 3, 2], [36, 32, 72, 45, 3, 2], [66, 50, 94, 58, 3, 2],
  [36, 66, 94, 79, 4, 3],
  [104, 16, 120, 20, 1.6, 1.4], [104, 25, 116, 29, 1.6, 1.4], [104, 34, 119, 38, 1.6, 1.4],
];
const GLASS = [[0, 0, 30, D, 5, 3.4], [100, 0, W, D, 5, 3.4]];

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let gap = value;

  const C = Cam(45, 0.5, 1.36);
  const top = 3 * 34 + LIFT + 6;
  fit(C, [[0, 0, 0], [W, D, 0], [W, 0, 0], [0, D, 0], [0, 0, top], [W, 0, top], [0, D, top]], 200, 166);
  const P = proj(C), front = facing(C);

  const g = mk("g", {}, svg);
  const layers = [];

  // 0 · the painting: an opaque plate, its frame, a floor and three arches in relief
  const plate = solid(g);
  const frame = mk("path", { class: "nf lo" }, g);
  const art = mk("path", { class: "nf" }, g);
  layers.push({
    parts: [plate.sil],
    draw(z) {
      const [ring, inner] = rings(0, 0, W, D, 6, 1.6);
      put(plate, prism(P, front, ring, inner, z, z + T));
      const zt = z + T, at = (x, y) => P(x, y, zt);
      frame.setAttribute("d", poly(ringAt(P, rrect(6, 6, W - 6, D - 6, 3, 4), zt)));
      let d = seg(at(12, 70), at(W - 12, 70)) + seg(at(18, 76), at(W - 18, 76));
      for (const cx of [36, 62, 88]) {
        const arch = [at(cx - 10, 70), at(cx - 10, 40)];
        for (let k = 0; k <= 8; k++) {
          const a = Math.PI - (k / 8) * Math.PI;
          arch.push(at(cx + 10 * Math.cos(a), 40 - 10 * Math.sin(a)));
        }
        arch.push(at(cx + 10, 70));
        d += open(arch);
      }
      art.setAttribute("d", d);
    },
  });

  // 1 · the veil: gauze, so a dashed outline and a mesh of dim dots, no plate
  const veil = mk("path", { class: "nf dash" }, g);
  const veilEdge = mk("path", { class: "nf sil" }, g);
  const mesh = [];
  for (let i = 0; i < 6; i++) for (let j = 0; j < 4; j++) mesh.push([14 + i * 19.2, 14 + j * 19.4, mk("circle", { r: 0.9, class: "dot off" }, g)]);
  layers.push({
    parts: [veilEdge],
    draw(z) {
      const ring = rrect(0, 0, W, D, 6, 4);
      veil.setAttribute("d", poly(ringAt(P, ring, z)));
      veilEdge.setAttribute("d", open(ringAt(P, run(ring, front), z)));
      for (const [x, y, el] of mesh) place(el, P(x, y, z));
    },
  });

  // 2 · the glass: sidebar and side pane, the chat column open between them
  const slabs = GLASS.map(() => solid(g));
  layers.push({
    parts: slabs.map((s) => s.sil),
    draw(z) {
      GLASS.forEach(([x0, y0, x1, y1, r, h], k) => {
        const [ring, inner] = rings(x0, y0, x1, y1, r, 1.4);
        put(slabs[k], prism(P, front, ring, inner, z, z + h));
      });
    },
  });

  // 3 · the content, floating, painted back to front; three window dots on the title bar
  const items = CONTENT.map((c) => [c, solid(g)]).sort((a, b) => a[0][0] + a[0][1] - (b[0][0] + b[0][1]));
  const lights = [0, 1, 2].map(() => mk("circle", { r: 1.25, class: "dot m" }, g));
  layers.push({
    parts: items.map((it) => it[1].sil),
    draw(z) {
      for (const [[x0, y0, x1, y1, r, h], sd] of items) {
        const [ring, inner] = rings(x0, y0, x1, y1, r, Math.min(1.2, (y1 - y0) / 3));
        put(sd, prism(P, front, ring, inner, z, z + h));
      }
      lights.forEach((el, k) => place(el, P(6 + k * 5, 4.5, z + 2.2)));
    },
  });

  // the content's own paint order: the window dots after the title bar
  items.forEach(([, sd]) => g.appendChild(sd.g));
  lights.forEach((el) => g.appendChild(el));

  const lift = layers.map(() => tween(0));
  const zOf = (i, now) => i * gap + tval(lift[i], now);
  const last = layers.map(() => NaN);

  const B = register(stage, (_dt, now) => {
    let moving = false;
    layers.forEach((L, i) => {
      const z = zOf(i, now);
      if (z !== last[i]) { L.draw(z); last[i] = z; }
      if (!tdone(lift[i], now)) moving = true;
    });
    return moving;
  });
  bag.add(B.unregister);

  // hit test on the rest pose: the layer whose resting middle is nearest the pointer's height
  const restY = (i) => P(W / 2, D / 2, i * gap)[1];
  const left = P(0, D, 0)[0], right = P(W, 0, 0)[0];
  function hit([x, y]) {
    if (x < left || x > right) return -1;
    let best = -1, dist = Infinity;
    layers.forEach((_, i) => { const d = Math.abs(y - restY(i)); if (d < dist) { dist = d; best = i; } });
    return dist < gap * 1.2 + 30 ? best : -1;
  }

  let act = -1;
  function paint(a) {
    layers.forEach((L, i) => L.parts.forEach((el) => el.classList.toggle("hi", a < 0 ? i === 0 : i === a)));
  }
  function setActive(a) {
    if (a === act) return;
    const now = performance.now(), from = a >= 0 ? a : act;
    act = a;
    layers.forEach((_, i) => tset(lift[i], a >= 0 && i > a ? LIFT : 0, now, Math.abs(i - from) * 45));
    paint(a);
    read.textContent = a < 0 ? "rest" : NAMES[a];
    B.wake();
  }
  paint(-1);

  bag.add(pointer(stage, { move: (p) => setActive(hit(p)), leave: () => setActive(-1) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { gap = clamp(v, 14, 34); last.fill(NaN); B.wake(); },
    destroy: bag.dispose,
  };
}

hairline({
  name: "calques",
  means: "A Claude window in four layers: the painting, the veil, the glass panels, the content. The pointer picks one.",
  rules: [1, 2, 5, 6],
  range: [14, 24, 34],
  mount,
});
