# Les illustrations du README

Chaque figure existe en deux versions, `-light.svg` et `-dark.svg`, sans fond :
le README choisit la bonne selon le thème de GitHub (`<picture>`). Les tableaux,
eux, sont les vraies images, servies par Wikimedia Commons.

| Figures | Fabriquées par |
|---|---|
| `layers`, `gallery`, `settings` (trait) | [Hairline](https://lucasmarkes.com/lab/hairline) : `calques.js`, `galerie.js` et `console.js` sont trois figures, montées sur le banc de Hairline puis exportées au repos par `node export-hairline.mjs hairline-<figure>.html ../<nom> "<titre>"` (avec `playwright-core`) |
| `tui` (capture du terminal) | `CAPTURE_OUT=<dossier> go test ./internal/tui -run TestCaptureScreens` à la racine du dépôt, puis `python3 ansi2svg.py <light\|dark> ../tui-<light\|dark>.svg <dossier>/home-<thème>.ansi <dossier>/settings-<thème>.ansi` |
