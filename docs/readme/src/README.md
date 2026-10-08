# Les illustrations du README

Chaque figure existe en deux versions, `-light.svg` et `-dark.svg`, sans fond :
le README choisit la bonne selon le thème de GitHub (`<picture>`).

| Figures | Fabriquées par |
|---|---|
| `hero`, `paintings`, `settings` (couleur, animées) | `python3 gen.py ..` — vue isométrique, tableaux stylisés de `paintings.py` |
| `layers`, `gallery` (trait) | [Hairline](https://lucasmarkes.com/lab/hairline) : `calques.js` et `galerie.js` sont deux figures, montées sur le banc de Hairline puis exportées au repos par `node export-hairline.mjs hairline-<figure>.html ../<nom> "<titre>"` (avec `playwright-core`) |
| `tui` (capture du terminal) | `CAPTURE_OUT=<dossier> go test ./internal/tui -run TestCaptureScreens` à la racine du dépôt, puis `python3 ansi2svg.py <light\|dark> ../tui-<light\|dark>.svg <dossier>/home-<thème>.ansi <dossier>/settings-<thème>.ansi` |

Les couleurs de l'app sont celles du thème (Ayu Dark) dans les deux versions :
seuls les contours, les ombres et les légendes suivent le thème de GitHub.
