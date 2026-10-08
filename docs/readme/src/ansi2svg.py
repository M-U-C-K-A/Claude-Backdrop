"""Turns captured screens of the interface (lipgloss output, 24-bit SGR) into
one SVG: two terminal windows, one over the other, for GitHub's light or
dark theme. Transparent around the windows.

usage: python3 ansi2svg.py <theme> <out.svg> <back.ansi> <front.ansi>
"""
import re
import sys
from html import escape

SGR = re.compile(r"\x1b\[([0-9;]*)m")
CW, LH, FS = 8.45, 19, 14
MONO = "'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

THEME = {
    "dark": {"bg": "#0b0e14", "fg": "#bfbdb6", "bar": "#0f131a", "rim": "rgba(240,246,252,0.14)", "title": "#6c7380", "shadow": "rgba(0,0,0,0.6)"},
    "light": {"bg": "#fcfcfc", "fg": "#5c6166", "bar": "#f0f1f2", "rim": "rgba(31,35,40,0.14)", "title": "#8a9199", "shadow": "rgba(31,48,72,0.25)"},
}


def cells(text):
    """Lines of cells (char, fg, bg, bold)."""
    out = []
    for line in text.split("\n"):
        fg = bg = None
        bold = False
        row = []
        pos = 0
        for m in SGR.finditer(line + "\x1b[m"):
            for ch in line[pos:m.start()]:
                row.append((ch, fg, bg, bold))
            pos = m.end()
            codes = [int(c) if c else 0 for c in m.group(1).split(";")] if m.group(1) else [0]
            i = 0
            while i < len(codes):
                c = codes[i]
                if c == 0:
                    fg = bg = None
                    bold = False
                elif c == 1:
                    bold = True
                elif c == 22:
                    bold = False
                elif c in (38, 48) and i + 4 < len(codes) and codes[i + 1] == 2:
                    col = "#%02x%02x%02x" % tuple(codes[i + 2:i + 5])
                    if c == 38:
                        fg = col
                    else:
                        bg = col
                    i += 4
                elif c == 39:
                    fg = None
                elif c == 49:
                    bg = None
                i += 1
        out.append(row)
    # drop the padding lines lipgloss adds at the top and bottom
    while out and not "".join(ch for ch, *_ in out[0]).strip():
        out.pop(0)
    while out and not "".join(ch for ch, *_ in out[-1]).strip():
        out.pop()
    return out


def screen(rows, t, x0, y0):
    parts = []
    for r, row in enumerate(rows):
        y = y0 + r * LH
        # backgrounds and half blocks
        c = 0
        while c < len(row):
            ch, fg, bg, bold = row[c]
            if ch == "▀":
                parts.append(f'<rect x="{x0 + c * CW:.2f}" y="{y:.2f}" width="{CW + 0.3:.2f}" height="{LH / 2 + 0.3:.2f}" fill="{fg or t["fg"]}"/>')
                parts.append(f'<rect x="{x0 + c * CW:.2f}" y="{y + LH / 2:.2f}" width="{CW + 0.3:.2f}" height="{LH / 2:.2f}" fill="{bg or t["bg"]}"/>')
                c += 1
                continue
            if bg:
                end = c
                while end < len(row) and row[end][2] == bg and row[end][0] != "▀":
                    end += 1
                parts.append(f'<rect x="{x0 + c * CW:.2f}" y="{y:.2f}" width="{(end - c) * CW:.2f}" height="{LH}" fill="{bg}"/>')
                c = end
                continue
            c += 1
        # text runs: same colour and weight, spaces included, trimmed
        c = 0
        while c < len(row):
            ch, fg, bg, bold = row[c]
            if ch == " " or ch == "▀":
                c += 1
                continue
            end = c
            while end < len(row) and row[end][1] == fg and row[end][3] == bold and row[end][0] != "▀":
                end += 1
            run = "".join(x[0] for x in row[c:end]).rstrip()
            n = len(run)
            weight = ' font-weight="700"' if bold else ""
            parts.append(
                f'<text x="{x0 + c * CW:.2f}" y="{y + LH * 0.74:.2f}" fill="{fg or t["fg"]}"{weight} '
                f'textLength="{n * CW:.2f}" lengthAdjust="spacingAndGlyphs">{escape(run)}</text>'
            )
            c = end
    return "".join(parts)


def window(rows, t, x, y, title, cols):
    w = cols * CW + 36
    h = len(rows) * LH + 34 + 30
    out = [
        f'<g filter="url(#sh)"><rect x="{x}" y="{y + 6}" width="{w}" height="{h}" rx="12" fill="{t["shadow"]}"/></g>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["bg"]}"/>',
        f'<path d="M{x} {y + 34}V{y + 12}A12 12 0 0 1 {x + 12} {y}H{x + w - 12}A12 12 0 0 1 {x + w} {y + 12}V{y + 34}Z" fill="{t["bar"]}"/>',
    ]
    for k, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{x + 18 + k * 18}" cy="{y + 17}" r="5.5" fill="{col}"/>')
    out.append(f'<text x="{x + w / 2}" y="{y + 22}" font-family="{SANS}" font-size="13" text-anchor="middle" fill="{t["title"]}">{escape(title)}</text>')
    out.append(f'<g font-family="{MONO}" font-size="{FS}">{screen(rows, t, x + 18, y + 34 + 14)}</g>')
    out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{t["rim"]}"/>')
    return w, h, "".join(out)


def main(theme, out, back, front):
    t = THEME[theme]
    a = cells(open(back, encoding="utf-8").read())
    b = cells(open(front, encoding="utf-8").read())
    cols_a = max(len("".join(ch for ch, *_ in r).rstrip()) for r in a) + 1
    cols_b = max(len("".join(ch for ch, *_ in r).rstrip()) for r in b) + 1
    wa, ha, ga = window(a, t, 24, 20, "claude-backdrop", cols_a)
    wb, hb, gb = window(b, t, 24 + wa - 230, 20 + 120, "claude-backdrop — Réglages", cols_b)
    W = 24 + wa - 230 + wb + 30
    H = 20 + 120 + hb + 40
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img">'
        f"<title>L’interface de claude-backdrop dans le terminal</title>"
        f'<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter></defs>'
        f"{ga}{gb}</svg>\n"
    )
    open(out, "w", encoding="utf-8").write(svg)
    print(out, len(svg), "bytes")


if __name__ == "__main__":
    main(*sys.argv[1:5])
