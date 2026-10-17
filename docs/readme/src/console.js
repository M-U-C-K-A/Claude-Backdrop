/**
 * Console: the settings of claude-backdrop as a small fader desk. Five
 * channels, each a slot with its scale of ticks, a channel lamp at the back
 * and a cap resting at its default: the veil, the brightness, the image blur,
 * the glass, the glass blur. The pointer picks the channel under it; that cap
 * lifts, takes the bright edge with its lamp, and slides along its slot to
 * where the pointer is. The read-out names the setting and its value. The
 * slider is how high a picked cap lifts.
 */
const {
  Cam, clamp, facing, fit, open, poly, proj, rings, prism, ringAt, rrect, unproj,
  spring, stepS, tdone, tset, tval, tween, disposer, mk, place, pointer, register, solid, put,
} = HL;

const W = 118, D = 86, H = 10, X0 = 15, DX = 22, Y0 = 16, Y1 = 72, CW = 6.5, CD = 4.5, CH = 6;
const CHANNELS = [
  { name: "voile", at: 0.55 / 0.95, say: (f) => `${Math.round(f * 95)} %` },
  { name: "luminosité", at: 0.7 / 1.3, say: (f) => `${Math.round(30 + f * 130)} %` },
  { name: "flou", at: 6 / 60, say: (f) => `${Math.round(f * 60)} px` },
  { name: "verre", at: 0.5, say: (f) => `${Math.round(f * 100)} %` },
  { name: "flou du verre", at: 22 / 80, say: (f) => `${Math.round(f * 80)} px` },
];
// a value runs from the front of the slot (0) to its back (1)
const yOf = (f) => Y1 - f * (Y1 - Y0);
const fOf = (y) => clamp((Y1 - y) / (Y1 - Y0), 0, 1);

function mount({ stage, svg, read }, value) {
  const bag = disposer();
  let lift = value;

  const C = Cam(45, 0.5, 1.95);
  fit(C, [[0, 0, 0], [W, D, 0], [W, 0, 0], [0, D, 0], [0, 0, H + CH + 18], [W, 0, H + CH + 18]], 200, 166);
  const P = proj(C), front = facing(C);
  const g = mk("g", {}, svg);

  // the desk
  const desk = solid(g);
  { const [ring, inner] = rings(0, 0, W, D, 9, 2); put(desk, prism(P, front, ring, inner, 0, H)); }
  const face = mk("g", {}, g);
  const slot = [], lamps = [];
  CHANNELS.forEach((ch, i) => {
    const x = X0 + i * DX;
    mk("path", { d: poly(ringAt(P, rrect(x - 1.6, Y0 - 3, x + 1.6, Y1 + 3, 1.6, 4), H)), class: "nf" }, face);
    let ticks = "";
    for (let k = 0; k <= 10; k++) {
      const y = yOf(k / 10), w = k % 5 ? 2.2 : 4;
      ticks += open([P(x + 4.5, y, H), P(x + 4.5 + w, y, H)]);
    }
    mk("path", { d: ticks, class: "nf lo" }, face);
    const lamp = mk("circle", { r: 1.35, class: "dot off" }, face);
    place(lamp, P(x, 7.5, H));
    lamps.push(lamp);
    slot.push(x);
  });
  // a seam along the front edge of the desk, where the hand rests
  mk("path", { d: open(ringAt(P, rrect(5, D - 9, W - 5, D - 5, 2, 4).filter((q) => q.v > D - 7), H)), class: "nf lo" }, face);

  // the caps, each on its own spring along its slot, and a lift tween
  const caps = CHANNELS.map((ch, i) => ({
    i, sd: solid(g), grip: mk("path", { class: "nf" }, g),
    y: spring(yOf(ch.at)), z: tween(0), last: "",
  }));
  for (const c of caps) c.grip.remove(), c.sd.g.appendChild(c.grip);

  function draw(c, now) {
    const y = c.y.x, z = tval(c.z, now), key = y.toFixed(3) + "|" + z.toFixed(3);
    if (key === c.last) return;
    c.last = key;
    const x = slot[c.i];
    const [ring, inner] = rings(x - CW, y - CD, x + CW, y + CD, 2.4, 1.1);
    put(c.sd, prism(P, front, ring, inner, H + z, H + z + CH));
    c.grip.setAttribute("d", open([P(x - CW + 2, y, H + z + CH), P(x + CW - 2, y, H + z + CH)]));
  }
  // paint the caps back to front, moving a group only when the order changes
  let order = "";
  function sort() {
    const s = caps.slice().sort((a, b) => slot[a.i] + a.y.x - (slot[b.i] + b.y.x));
    const key = s.map((c) => c.i).join();
    if (key !== order) { order = key; for (const c of s) g.appendChild(c.sd.g); }
  }

  const B = register(stage, (dt, now) => {
    let moving = false;
    for (const c of caps) {
      if (stepS(c.y, dt)) moving = true;
      if (!tdone(c.z, now)) moving = true;
      draw(c, now);
    }
    sort();
    return moving;
  });
  bag.add(B.unregister);

  // hit test on a fixed plane at the caps' tops, so a cap lands under the pointer
  let act = -1;
  function light(a) {
    caps.forEach((c) => c.sd.sil.classList.toggle("hi", c.i === (a < 0 ? 0 : a)));
    lamps.forEach((l, i) => { l.setAttribute("class", "dot" + (i === (a < 0 ? 0 : a) ? "" : " off")); });
  }
  function move(p) {
    const [x, y] = unproj(C, p[0], p[1], H + CH);
    const i = Math.round((x - X0) / DX);
    const inside = i >= 0 && i < caps.length && Math.abs(x - slot[i]) < DX / 2 && y > Y0 - 8 && y < Y1 + 8;
    const a = inside ? i : -1, now = performance.now();
    if (a !== act) {
      caps.forEach((c) => {
        tset(c.z, c.i === a ? lift : 0, now, 0);
        if (c.i !== a) c.y.t = yOf(CHANNELS[c.i].at);
      });
      act = a;
      light(a);
    }
    if (a >= 0) {
      caps[a].y.t = clamp(y, Y0, Y1);
      read.textContent = `${CHANNELS[a].name} ${CHANNELS[a].say(fOf(caps[a].y.t))}`;
    } else read.textContent = "rest";
    B.wake();
  }
  light(-1);
  read.textContent = "rest";

  bag.add(pointer(stage, { move, leave: () => move([-1e4, -1e4]) }));
  bag.add(() => svg.replaceChildren());

  return {
    set: (v) => { lift = v; if (act >= 0) { tset(caps[act].z, lift, performance.now(), 0); B.wake(); } },
    destroy: bag.dispose,
  };
}

hairline({
  name: "console",
  means: "The settings as a fader desk: the pointer picks a channel, and its cap lifts and slides to where the pointer is.",
  rules: [1, 3, 5, 8],
  range: [0, 9, 16],
  mount,
});
