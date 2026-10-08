"""Colored, animated isometric illustrations for the README of claude-backdrop.

Writes <name>-light.svg and <name>-dark.svg for each figure: transparent
background, the app drawn as it really is (Ayu Dark), only the edges, shadows
and captions changing with GitHub's theme.

usage: python3 gen.py <out-dir>
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paintings import PAINTINGS, athens, pandemonium  # noqa: E402

C = math.cos(math.radians(45))
COS30 = math.cos(math.radians(30))
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

AYU = {
    "bg": "#0b0e14", "panel": "#0d1017", "line": "#11151c", "fg": "#bfbdb6", "dim": "#acb6bf", "muted": "#6c7380",
    "gold": "#e6b450", "orange": "#ff8f40", "blue": "#59c2ff", "green": "#aad94c", "purple": "#d2a6ff", "red": "#f07178",
}

THEMES = {
    "light": {"edge": "rgba(31,35,40,0.16)", "rim": "rgba(255,255,255,0.10)", "shadow": "rgba(31,48,72,0.22)",
              "title": "#1f2328", "text": "#59636e", "faint": "#818b98", "side": "#1b1f27", "track": "#d1d9e0",
              "ink": "#5c6166", "sheet": "rgba(11,14,20,0.07)"},
    "dark": {"edge": "rgba(240,246,252,0.14)", "rim": "rgba(255,255,255,0.12)", "shadow": "rgba(0,0,0,0.55)",
             "title": "#f0f6fc", "text": "#9198a1", "faint": "#6e7681", "side": "#151a22", "track": "#3d444d",
             "ink": "#bfbdb6", "sheet": "rgba(255,255,255,0.025)"},
}


class Iso:
    """The 2:1 isometric view of the Hairline figures: +x runs down to the right, +y down to the left."""

    def __init__(self, S, cx, cy):
        self.S, self.cx, self.cy = S, cx, cy

    def p(self, x, y, z=0):
        return (self.cx + (x - y) * C * self.S, self.cy + (x + y) * C * 0.5 * self.S - z * COS30 * self.S)

    def plane(self, z):
        a, b = C * self.S, C * 0.5 * self.S
        return f"matrix({a:.4f} {b:.4f} {-a:.4f} {b:.4f} {self.cx:.2f} {self.cy - z * COS30 * self.S:.2f})"


def wall(iso, y, z_top):
    """The plane y = const, as a matrix: u runs along +x, v runs down from z_top."""
    a, b, d = C * iso.S, C * 0.5 * iso.S, COS30 * iso.S
    sx, sy = iso.p(0, y, z_top)
    return f"matrix({a:.4f} {b:.4f} 0 {d:.4f} {sx:.2f} {sy:.2f})"


def canvas(iso, x0, y0, z_top, w, h, r, depth, side, edge, inner):
    """A canvas standing in the plane y = y0, facing +y, `depth` thick behind it."""
    rg = ring(0, 0, w, h, r)
    pts = [iso.p(x0 + u, y, z_top - v) for u, v in rg for y in (y0, y0 - depth)]
    out = f'<path d="{poly(hull(pts))}" fill="{side}" stroke="{edge}" stroke-width="1"/>'
    m = wall(iso, y0, z_top).replace("matrix(", "")
    a, b, c, d, e, f = (float(t) for t in m.rstrip(")").split())
    e += x0 * a
    f += x0 * b
    out += f'<g transform="matrix({a:.4f} {b:.4f} {c:.4f} {d:.4f} {e:.2f} {f:.2f})">{inner}'
    out += f'<rect x="0" y="0" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{edge}" stroke-width="1" vector-effect="non-scaling-stroke"/></g>'
    return out


def ring(u0, v0, u1, v1, r, n=6):
    r = min(r, (u1 - u0) / 2, (v1 - v0) / 2)
    pts = []
    for cu, cv, a0 in ((u1 - r, v0 + r, -90), (u1 - r, v1 - r, 0), (u0 + r, v1 - r, 90), (u0 + r, v0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def hull(points):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return lower[:-1] + upper[:-1]


def poly(points):
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in points) + "Z"


def slab(iso, box, z0, z1, side, top, edge, inner="", top_extra="", side_extra=""):
    """A rounded slab from z0 to z1: its sides (the hull of both rings), then its top face, with `inner` drawn on it."""
    u0, v0, u1, v1, r = box
    rg = ring(u0, v0, u1, v1, r)
    sides = hull([iso.p(u, v, z0) for u, v in rg] + [iso.p(u, v, z1) for u, v in rg])
    out = f'<path d="{poly(sides)}" fill="{side}" stroke="{edge}" stroke-width="1"{side_extra}/>'
    out += f'<g transform="{iso.plane(z1)}">'
    out += f'<rect x="{u0}" y="{v0}" width="{u1 - u0}" height="{v1 - v0}" rx="{r}" fill="{top}"{top_extra}/>'
    out += inner
    out += f'<rect x="{u0}" y="{v0}" width="{u1 - u0}" height="{v1 - v0}" rx="{r}" fill="none" stroke="{edge}" stroke-width="1" vector-effect="non-scaling-stroke"/>'
    out += "</g>"
    return out


def shadow(iso, box, z, colour, blur_id):
    u0, v0, u1, v1, r = box
    return f'<g filter="url(#{blur_id})"><path d="{poly([iso.p(u, v, z) for u, v in ring(u0, v0, u1, v1, r)])}" fill="{colour}"/></g>'


def bar(u, v, w, h, fill, opacity=1.0):
    return f'<rect x="{u}" y="{v}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}" opacity="{opacity}"/>'


def painting_fill(fn, uid, w, h, clip):
    """A painting scaled to cover a w x h box, centred, clipped to the box's rounded rect."""
    s = max(w / 160, h / 110)
    dx, dy = (w - 160 * s) / 2, (h - 110 * s) / 2
    return f'<g clip-path="url(#{clip})"><g class="pan"><g transform="translate({dx:.2f} {dy:.2f}) scale({s:.4f})">{fn(uid)}</g></g></g>'


def svg(w, h, title, body, css=""):
    style = (
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}"
        "@keyframes bob2{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}"
        "@keyframes pan{0%,100%{transform:translateX(-6px)}50%{transform:translateX(6px)}}"
        ".pan{animation:pan 18s ease-in-out infinite}"
        + css +
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" fill="none">'
        f"<title>{title}</title><style>{style}</style>{body}</svg>\n"
    )


def blur_def(fid, sd):
    return f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{sd}"/></filter>'


# ---------------------------------------------------------------- the window

WIN = (0, 0, 340, 200, 14)


def window_layers(iso, t, z, uid, painting=pandemonium, veil=0.42, glass=0.6, flat=False):
    """The four layers of a Claude window, painted bottom to top. With flat=True they lie on one plate."""
    out = {}
    u0, v0, u1, v1, r = WIN
    defs = f'<clipPath id="win{uid}"><rect x="{u0}" y="{v0}" width="{u1}" height="{v1}" rx="{r}"/></clipPath>'
    # 0 · the painting
    art = painting_fill(painting, uid, u1, v1, f"win{uid}")
    out["painting"] = slab(iso, WIN, z[0] - 7, z[0], t["side"], "#000", t["edge"], inner=art)
    # 1 · the veil
    out["veil"] = (
        f'<g transform="{iso.plane(z[1])}"><rect class="veil{uid}" x="{u0}" y="{v0}" width="{u1}" height="{v1}" rx="{r}" '
        f'fill="{AYU["bg"]}" fill-opacity="{veil}" stroke="{t["rim"]}" stroke-width="1" vector-effect="non-scaling-stroke"/></g>'
    )
    # 2 · the glass: sidebar and side pane, frosted
    chats = "".join(bar(10, v, w, h, col, op) for v, w, h, col, op in (
        (28, 62, 8, AYU["gold"], 0.25), (42, 54, 5, AYU["fg"], 0.6), (54, 60, 5, AYU["fg"], 0.45),
        (66, 46, 5, AYU["fg"], 0.45), (78, 56, 5, AYU["fg"], 0.45), (90, 40, 5, AYU["fg"], 0.45)))
    code = ""
    for k in range(10):
        w = (34, 50, 42, 58, 28, 46, 52, 36, 44, 30)[k]
        col = (AYU["orange"], AYU["blue"], AYU["fg"], AYU["green"], AYU["purple"], AYU["fg"], AYU["blue"], AYU["orange"], AYU["fg"], AYU["green"])[k]
        code += bar(266 + (k % 3) * 4, 26 + k * 11, w, 4, col, 0.85)
    glass_g = ""
    for box, text in (((0, 0, 84, 200, 14), chats), ((256, 0, 340, 200, 14), code)):
        b0, b1, b2, b3, br = box
        hi = (
            f'<rect x="{b0}" y="{b1}" width="{b2 - b0}" height="{b3 - b1}" rx="{br}" fill="url(#frost{uid})"/>' + text
        )
        if flat:
            glass_g += (
                f'<g transform="{iso.plane(z[2])}"><rect class="glass{uid}" x="{b0}" y="{b1}" width="{b2 - b0}" height="{b3 - b1}" rx="{br}" '
                f'fill="{AYU["panel"]}" fill-opacity="{glass}"/>{hi}</g>'
            )
        else:
            glass_g += slab(iso, box, z[2] - 3, z[2], f"rgba(13,16,23,{glass + 0.15})", f"rgba(13,16,23,{glass})", t["rim"], inner=hi)
    defs += (
        f'<linearGradient id="frost{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.16"/>'
        f'<stop offset="0.5" stop-color="#fff" stop-opacity="0.04"/><stop offset="1" stop-color="#fff" stop-opacity="0.0"/></linearGradient>'
    )
    out["glass"] = glass_g
    # 3 · the content, floating: title bar, chat list, conversation, composer, the file in the pane
    zc = z[3]
    c = ""
    c += slab(iso, (0, 0, 340, 16, 8), zc - 2, zc, "#07090d", AYU["bg"], t["rim"],
              inner="".join(f'<circle cx="{10 + 9 * k}" cy="8" r="3" fill="{col}"/>' for k, col in enumerate(("#ff5f57", "#febc2e", "#28c840")))
              + f'<rect x="320" y="3.5" width="12" height="9" rx="2.5" fill="{AYU["gold"]}"/>')
    # a faint sheet: the layer the text lies on, in the exploded view
    flat_items = "" if flat else (
        f'<rect x="{u0}" y="{v0}" width="{u1}" height="{v1}" rx="{r}" fill="{t["sheet"]}" stroke="{t["rim"]}" '
        f'stroke-width="1" vector-effect="non-scaling-stroke"/>')
    # conversation: a user bubble, the answer, a code block
    flat_items += f'<rect x="164" y="28" width="78" height="22" rx="8" fill="{AYU["line"]}" opacity="0.92"/>' + bar(172, 34, 56, 4, AYU["fg"], 0.8) + bar(172, 42, 38, 4, AYU["fg"], 0.8)
    for k, w in enumerate((140, 128, 146, 96)):
        flat_items += bar(98, 62 + k * 9, w, 4.5, AYU["fg"] if flat else t["ink"], 0.85)
    flat_items += f'<rect x="98" y="102" width="146" height="40" rx="6" fill="{AYU["bg"]}" opacity="0.94"/>'
    for k, toks in enumerate(((AYU["orange"], 18), (AYU["blue"], 30), (AYU["green"], 40)), start=0):
        col, w = toks
        flat_items += bar(106, 109 + k * 10, 14, 4, AYU["purple"], 0.9) + bar(124, 109 + k * 10, w, 4, col, 0.9) + bar(128 + w, 109 + k * 10, 22, 4, AYU["fg"], 0.6)
    c += f'<g transform="{iso.plane(zc)}">{flat_items}</g>'
    # the composer, a slab of its own
    c += slab(iso, (96, 158, 246, 188, 10), zc - 4, zc, "#07090d", AYU["panel"], t["rim"],
              inner=bar(108, 170, 70, 5, AYU["muted"], 0.9) + f'<circle cx="232" cy="173" r="7" fill="{AYU["gold"]}"/>')
    out["content"] = c
    return defs, out


# ---------------------------------------------------------------- figures

def hero(t):
    W, H = 1200, 560
    iso = Iso(1.62, 785, 172)
    z = [0, 34, 68, 102]
    defs, L = window_layers(iso, t, z, "h")
    defs += blur_def("hs", 14)
    body = f"<defs>{defs}</defs>"
    body += shadow(iso, (8, 14, 344, 214, 14), -24, t["shadow"], "hs")
    body += f'<g class="l0">{L["painting"]}</g>'
    body += f'<g class="l1">{L["veil"]}</g>'
    body += f'<g class="l2">{L["glass"]}</g>'
    body += f'<g class="l3">{L["content"]}</g>'
    # the title, on the left
    body += (
        f'<g font-family="{FONT}">'
        f'<rect x="40" y="186" width="56" height="6" rx="3" fill="{AYU["gold"]}"/>'
        f'<text x="38" y="262" font-size="60" font-weight="700" letter-spacing="-1.5" fill="{t["title"]}">Claude</text>'
        f'<text x="38" y="326" font-size="60" font-weight="700" letter-spacing="-1.5" fill="{t["title"]}">Backdrop</text>'
        f'<text x="40" y="374" font-size="21" fill="{t["text"]}">Un tableau derrière Claude Desktop,</text>'
        f'<text x="40" y="402" font-size="21" fill="{t["text"]}">Ayu Dark partout ailleurs.</text>'
        f'<text x="40" y="446" font-size="14" letter-spacing="0.6" fill="{t["faint"]}">macOS · Claude Code compris · réglé en direct</text>'
        "</g>"
    )
    css = (
        ".l1{animation:bob 7s ease-in-out infinite;animation-delay:-1s}"
        ".l2{animation:bob 7s ease-in-out infinite;animation-delay:-2s}"
        ".l3{animation:bob2 7s ease-in-out infinite;animation-delay:-3s}"
    )
    return svg(W, H, "Claude Backdrop : un tableau derrière Claude Desktop", body, css)


def gallery(t):
    W, H = 1180, 400
    S, w, h = 1.52, 170, 116
    body_defs = blur_def("gs", 8)
    body, css = "", ""
    for k, (key, title, author, fn) in enumerate(PAINTINGS):
        cx = 148 + k * 295
        # the canvas centre sits at cx; its foot at screen height 250
        iso = Iso(S, 0, 0)
        mx, my = iso.p(w / 2, 0, 0)
        iso = Iso(S, cx - mx, 262 - my)
        uid = f"g{k}"
        body_defs += f'<clipPath id="c{uid}"><rect x="0" y="0" width="{w}" height="{h}" rx="6"/></clipPath>'
        art = painting_fill(fn, uid, w, h, f"c{uid}")
        frame = (f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="5" fill="none" stroke="#d9b45a" '
                 f'stroke-opacity="0.6" stroke-width="1.3" vector-effect="non-scaling-stroke"/>')
        # the floor shadow, then the canvas floating above it
        floor = [iso.p(x, y, 0) for x, y in ((4, -10), (w + 2, -10), (w + 2, 8), (4, 8))]
        body += f'<g filter="url(#gs)"><path d="{poly(floor)}" fill="{t["shadow"]}"/></g>'
        body += f'<g class="t{k}">{canvas(iso, 0, 0, h + 14, w, h, 6, 7, "#3a2a17", t["edge"], art + frame)}</g>'
        fx, fy = iso.p(w / 2, 0, 0)
        body += (
            f'<g font-family="{FONT}" text-anchor="middle">'
            f'<text x="{fx:.1f}" y="{fy + 58:.1f}" font-size="18" font-weight="600" fill="{t["title"]}">{title}</text>'
            f'<text x="{fx:.1f}" y="{fy + 82:.1f}" font-size="14" fill="{t["text"]}">{author}</text></g>'
        )
        css += f".t{k}{{animation:bob 6s ease-in-out infinite;animation-delay:-{k * 1.1:.1f}s}}"
    return svg(W, H, "Les quatre tableaux de la galerie", f"<defs>{body_defs}</defs>" + body, css)


def settings(t):
    W, H = 1180, 400
    body_defs = blur_def("ss", 9)
    body = ""
    css = (
        "@keyframes veil{0%,100%{fill-opacity:.12}50%{fill-opacity:.78}}"
        "@keyframes glass{0%,100%{fill-opacity:.12}50%{fill-opacity:.92}}"
        "@keyframes knob{0%,100%{transform:translateX(0)}50%{transform:translateX(150px)}}"
        ".veils0{animation:veil 6s ease-in-out infinite}"
        ".glasss2,.glasss2b{animation:glass 6s ease-in-out infinite}"
        ".knob{animation:knob 6s ease-in-out infinite}"
    )
    labels = [("Voile", "dim · 0 → 0,95"), ("Flou de l’image", "imageBlur · 0 → 60 px"), ("Verre", "glass · 0 → 1")]
    for k in range(3):
        cx = 200 + k * 390
        S = 0.98
        iso = Iso(S, cx - (340 - 200) / 2 * C * S, 34)
        uid = f"s{k}"
        defs, L = window_layers(iso, t, [0, 0.1, 0.2, 0.3], uid, painting=athens,
                                veil=0.42 if k != 0 else 0.4, glass=0.55, flat=True)
        if k == 1:
            # the image blur, breathing
            defs += (
                f'<filter id="bl{uid}" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0">'
                f'<animate attributeName="stdDeviation" values="0;3.2;0" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                f"</feGaussianBlur></filter>"
            )
            L["painting"] = L["painting"].replace('<g class="pan">', f'<g filter="url(#bl{uid})">', 1)
        if k == 2:
            L["glass"] = L["glass"].replace(f'class="glass{uid}"', f'class="glasss2"')
        body_defs += defs
        body += shadow(iso, (6, 10, 346, 210, 14), -26, t["shadow"], "ss")
        body += L["painting"] + L["veil"] + L["glass"] + L["content"]
        # caption and a slider
        bx, by = iso.p(340, 200, -26)
        label, key = labels[k]
        x0 = bx - 85
        body += (
            f'<g font-family="{FONT}" text-anchor="middle">'
            f'<text x="{bx:.1f}" y="{by + 40:.1f}" font-size="17" font-weight="600" fill="{t["title"]}">{label}</text>'
            f'<text x="{bx:.1f}" y="{by + 62:.1f}" font-size="13" fill="{t["text"]}">{key}</text></g>'
            f'<rect x="{x0:.1f}" y="{by + 78:.1f}" width="170" height="4" rx="2" fill="{t["track"]}"/>'
            f'<g class="knob"><rect x="{x0:.1f}" y="{by + 78:.1f}" width="20" height="4" rx="2" fill="{AYU["gold"]}"/>'
            f'<circle cx="{x0 + 10:.1f}" cy="{by + 80:.1f}" r="7" fill="{AYU["gold"]}"/></g>'
        )
    body = f"<defs>{body_defs}</defs>" + body
    return svg(W, H, "Trois réglages : le voile, le flou de l’image, le verre", body, css)


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, fn in (("hero", hero), ("paintings", gallery), ("settings", settings)):
        for theme, t in THEMES.items():
            path = os.path.join(out, f"{name}-{theme}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fn(t))
            print(path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
