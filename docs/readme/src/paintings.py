"""The four paintings of the gallery, stylized: flat shapes in a 160 x 110
canvas, (0, 0) at the top left. Each function returns SVG markup; `uid`
keeps gradient ids unique when a painting appears more than once."""


def _rect(x, y, w, h, fill, rx=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{extra}/>'


def _path(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}"{extra}/>'


def _arch(x, y_base, w, h):
    """An arch opening: straight sides from y_base up to the springing line, a half circle on top."""
    r = w / 2
    top = y_base - h
    return f"M{x} {y_base}V{top + r}A{r} {r} 0 0 1 {x + w} {top + r}V{y_base}Z"


def socrates(uid):
    g = f"soc{uid}"
    return "".join([
        f'<defs><linearGradient id="{g}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2722"/><stop offset="1" stop-color="#4b4336"/></linearGradient>'
        f'<radialGradient id="{g}l" cx="0.42" cy="0.55" r="0.6"><stop offset="0" stop-color="#ffe9c2" stop-opacity="0.35"/><stop offset="1" stop-color="#ffe9c2" stop-opacity="0"/></radialGradient></defs>',
        _rect(0, 0, 160, 110, f"url(#{g}w)"),
        # the corridor on the left, lit, with its arch
        _path(_arch(8, 74, 26, 52), "#7d6e57"),
        _path(_arch(13, 74, 16, 38), "#a8977a"),
        # stone blocks of the back wall
        _rect(40, 18, 116, 1.2, "#5a5143"), _rect(40, 36, 116, 1.2, "#5a5143"),
        # floor
        _rect(0, 86, 160, 24, "#5d4c38"), _rect(0, 86, 160, 2, "#7a654a"),
        _rect(0, 0, 160, 110, f"url(#{g}l)"),
        # the bed
        _rect(22, 66, 92, 9, "#cdbd9b", 2), _rect(26, 75, 4, 12, "#8a7656"), _rect(106, 75, 4, 12, "#8a7656"),
        # Socrates in white, seated, an arm raised
        _path("M42 67C42 52 50 45 57 46C64 47 66 56 66 67Z", "#ece6d6"),
        _path("M56 47L53 30L56 29L60 46Z", "#e2d9c4"),
        _rect(53, 38, 7, 8, "#d8c6a6", 3.5),
        # the cup, held out by a disciple
        _path("M72 58L86 52L94 57L84 66Z", "#a8322a"), _rect(70, 55, 3, 3, "#d9b66a", 1),
        # disciples: red, ochre, blue, grey
        _path("M96 86C96 66 102 56 110 56C118 56 122 68 122 86Z", "#a63a2a"),
        _path("M120 86C121 70 126 62 133 62C140 62 143 72 143 86Z", "#c27a32"),
        _path("M138 86C139 72 143 66 149 66C155 66 157 74 157 86Z", "#3d5a80"),
        _path("M14 86C15 74 19 68 25 68C31 68 34 76 34 86Z", "#8f8a80"),
        _rect(106, 48, 8, 9, "#d8b48c", 4), _rect(128, 55, 7, 8, "#d8b48c", 3.5), _rect(145, 60, 6, 7, "#d8b48c", 3),
    ])


def horatii(uid):
    g = f"hor{uid}"
    arches = "".join(_path(_arch(x, 66, 36, 54), "#1e1d19") for x in (12, 62, 112))
    floor = "".join(
        _rect(i * 16 + (8 if j % 2 else 0), 80 + j * 8, 8, 8, "#8a7a62") for i in range(10) for j in range(4)
    )
    return "".join([
        f'<defs><linearGradient id="{g}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a33"/><stop offset="1" stop-color="#5a564a"/></linearGradient></defs>',
        _rect(0, 0, 160, 110, f"url(#{g}w)"),
        arches,
        _rect(0, 66, 160, 14, "#4a463c"),
        _rect(0, 80, 160, 30, "#6e604c"), floor,
        # the three brothers, arms out to the swords
        _path("M10 96L22 58L34 60L30 96Z", "#b0382a"),
        _path("M20 96L30 60L40 61L40 96Z", "#d9d1bf"),
        _path("M30 96L38 61L48 62L50 96Z", "#5a6a7a"),
        _path("M34 62L70 50L71 53L36 66Z", "#d0b48a"),
        _rect(22, 50, 8, 9, "#cfa983", 4), _rect(32, 52, 7, 8, "#cfa983", 3.5),
        # the father, red cloak, the swords raised
        _path("M66 96C66 72 72 56 80 56C88 56 92 72 92 96Z", "#9e2b22"),
        _rect(75, 46, 9, 10, "#cfa983", 4.5),
        _path("M70 50L76 26L77.5 26L72 50Z", "#e3cf8e"), _path("M78 48L80 24L81.5 24L80 48Z", "#e3cf8e"), _path("M86 50L86 26L87.5 26L88 50Z", "#e3cf8e"),
        # the women, grieving, on the right
        _path("M108 96C106 82 112 72 122 72C130 72 134 84 132 96Z", "#e8e2d2"),
        _path("M126 96C126 84 132 76 140 76C148 76 152 86 150 96Z", "#4e6a8a"),
        _path("M140 96C141 88 145 82 151 82C157 82 159 90 158 96Z", "#c9a25a"),
        _rect(116, 64, 8, 9, "#d8b48c", 4), _rect(136, 69, 7, 8, "#d8b48c", 3.5),
    ])


def pandemonium(uid):
    g = f"pan{uid}"
    cols = "".join(_rect(40 + i * 7.6, 44, 3.2, 22, "#ffd27a" if i % 2 else "#f2b04a") for i in range(15))
    ripples = "".join(_rect(8 + (i * 23) % 120, 80 + i * 3.4, 18 + (i * 7) % 22, 1, "#ffd08a", 0.5, ' opacity="0.7"') for i in range(8))
    return "".join([
        f'<defs><linearGradient id="{g}s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140806"/><stop offset="0.45" stop-color="#5e1f10"/><stop offset="0.72" stop-color="#d9742a"/><stop offset="1" stop-color="#ffb14d"/></linearGradient>'
        f'<linearGradient id="{g}l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb347"/><stop offset="0.5" stop-color="#c25420"/><stop offset="1" stop-color="#3a1208"/></linearGradient>'
        f'<radialGradient id="{g}g" cx="0.62" cy="0.62" r="0.45"><stop offset="0" stop-color="#ffe0a0" stop-opacity="0.75"/><stop offset="1" stop-color="#ffe0a0" stop-opacity="0"/></radialGradient></defs>',
        _rect(0, 0, 160, 110, f"url(#{g}s)"),
        _rect(0, 0, 160, 110, f"url(#{g}g)"),
        # the palace: stylobate, colonnade, entablature, a dome of fire behind
        _path("M70 40A30 16 0 0 1 130 40Z", "#ffcf7a", ' opacity="0.55"'),
        _rect(34, 38, 120, 6, "#c26a26"), _rect(30, 36, 128, 2.5, "#ffd890"),
        cols,
        _rect(32, 66, 124, 4, "#8a3a16"), _rect(28, 70, 132, 3, "#5a220e"),
        # the lake of fire
        _rect(0, 73, 160, 37, f"url(#{g}l)"), ripples,
        # the rock and the figure on it
        _path("M0 110V82C10 76 22 80 30 88C36 94 40 102 42 110Z", "#120806"),
        _path("M16 80L19 70L22 80Z", "#2a0f08"),
    ])


def athens(uid):
    g = f"ath{uid}"
    figures = []
    colours = ["#b23b2e", "#3f5f8f", "#d08b3a", "#e6dccb", "#5f7f4f", "#7a3f6a", "#c9a25a", "#3f5f8f", "#b23b2e", "#e6dccb", "#d08b3a", "#5f7f4f"]
    for i, c in enumerate(colours):
        x = 12 + i * 11.5 + (3 if i in (5, 6) else 0)
        h = 15 if i in (5, 6) else 11 + (i % 3) * 2
        y = 76 - h
        figures.append(_rect(x, y, 7, h, c, 3))
        figures.append(_rect(x + 1.5, y - 4.5, 4, 4.5, "#d8b48c", 2))
    return "".join([
        f'<defs><linearGradient id="{g}k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fc2e3"/><stop offset="1" stop-color="#e3eef5"/></linearGradient>'
        f'<linearGradient id="{g}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cdb791"/><stop offset="1" stop-color="#e4d5b5"/></linearGradient></defs>',
        _rect(0, 0, 160, 110, f"url(#{g}w)"),
        # receding vaults, from the great arch to the sky
        _path(_arch(14, 70, 132, 70), "#b59a6e"),
        _path(_arch(28, 66, 104, 58), "#c8b088"),
        _path(_arch(44, 62, 72, 46), "#a88d63"),
        _path(_arch(56, 60, 48, 36), f"url(#{g}k)"),
        # coffers on the great vault
        "".join(_rect(20 + i * 15, 14 + abs(4 - i) * 3, 6, 3, "#9c8158", 1) for i in range(9)),
        # statues in their niches
        _rect(4, 30, 9, 28, "#a88d63", 4), _rect(147, 30, 9, 28, "#a88d63", 4),
        _rect(6, 36, 5, 18, "#e2d6bc", 2.5), _rect(149, 36, 5, 18, "#e2d6bc", 2.5),
        # the steps and the floor
        _rect(0, 76, 160, 34, "#bba27a"), _rect(0, 76, 160, 1.5, "#e8dcc0"), _rect(0, 86, 160, 1.5, "#d9c9a6"), _rect(0, 96, 160, 1.5, "#cdb991"),
        "".join(figures),
        # two seated figures on the steps
        _rect(30, 86, 10, 8, "#5f7f4f", 3), _rect(112, 86, 12, 8, "#b23b2e", 3),
    ])


PAINTINGS = [
    ("socrates", "La Mort de Socrate", "David, 1787", socrates),
    ("horatii", "Le Serment des Horaces", "David, 1784", horatii),
    ("pandemonium", "Pandémonium", "John Martin, 1841", pandemonium),
    ("school-of-athens", "L’École d’Athènes", "Raphaël, 1511", athens),
]
