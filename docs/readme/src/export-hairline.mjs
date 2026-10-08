// Exports the rest pose of a built Hairline page as two standalone SVGs, one
// for GitHub's light theme and one for its dark theme. No background: plates
// are filled with the page colour of each theme, so they still hide what is
// behind them.
// usage: node export-hairline.mjs <hairline-x.html> <out-prefix> <title>
import { writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

import { chromium } from "playwright-core";

const [page, out, title] = process.argv.slice(2);
const THEMES = {
  light: { plate: "#ffffff", hi: "#24292f", edge: "#9a9aa3", mid: "#bdbdc4", lo: "#dcdce1" },
  dark: { plate: "#0d1117", hi: "#d0d6e0", edge: "#5f6670", mid: "#3d434d", lo: "#2a2f37" },
};

const style = (c) =>
  `path,polygon,ellipse,line{fill:${c.plate};stroke:${c.mid};stroke-width:1.1;vector-effect:non-scaling-stroke;stroke-linejoin:round;stroke-linecap:round}` +
  `.nf{fill:none}.fo{stroke:none}.sil{stroke:${c.edge}}.hi{stroke:${c.hi}}.lo{stroke:${c.lo}}.dash{stroke-dasharray:1.5 3}` +
  `.dot{stroke:none;fill:${c.hi}}.dot.m{fill:${c.edge}}.dot.off{fill:${c.lo}}.ghost path{fill:none;stroke:${c.mid}}`;

const browser = await chromium.launch();
const tab = await browser.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 1 });
await tab.goto(pathToFileURL(page).href);
await tab.waitForTimeout(1800);
const { inner, box } = await tab.evaluate(() => {
  const svg = document.querySelector("#stage svg");
  // the union of what is drawn, outside masks and defs, in viewBox units
  const m = svg.getScreenCTM().inverse();
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const el of svg.querySelectorAll("path, circle, ellipse, line, polygon")) {
    if (el.closest("mask, defs, clipPath")) continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    for (const [px, py] of [[r.left, r.top], [r.right, r.bottom]]) {
      const q = new DOMPoint(px, py).matrixTransform(m);
      x0 = Math.min(x0, q.x); y0 = Math.min(y0, q.y); x1 = Math.max(x1, q.x); y1 = Math.max(y1, q.y);
    }
  }
  return { inner: svg.innerHTML, box: [x0, y0, x1 - x0, y1 - y0] };
});
await browser.close();

const pad = 6;
const [x, y, w, h] = [box[0] - pad, box[1] - pad, box[2] + 2 * pad, box[3] + 2 * pad].map((v) => Math.round(v * 10) / 10);
const scale = 1.7;
for (const [name, colours] of Object.entries(THEMES)) {
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x} ${y} ${w} ${h}" width="${Math.round(w * scale)}" height="${Math.round(h * scale)}" role="img">` +
    `<title>${title}</title><style>${style(colours)}</style>${inner}</svg>\n`;
  writeFileSync(`${out}-${name}.svg`, svg);
  console.log(`${out}-${name}.svg`, svg.length, "bytes");
}
