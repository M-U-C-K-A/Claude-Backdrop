Un tableau derrière Claude Desktop (macOS), et Ayu Dark partout ailleurs : le chat, la vue Claude Code, le terminal et les fichiers ouverts laissent voir l'image ; la barre latérale et les panneaux deviennent du verre dépoli.

### Installer

```bash
curl -fsSL https://github.com/M-U-C-K-A/claude-code/releases/latest/download/install.sh | bash
claude-backdrop        # puis « Installer »
```

Ou à la main : télécharge `claude-backdrop-macos.tar.gz` ci-dessous, puis

```bash
tar -xzf ~/Downloads/claude-backdrop-macos.tar.gz -C ~/Downloads
xattr -d com.apple.quarantine ~/Downloads/claude-backdrop   # fichier venu du navigateur
mv ~/Downloads/claude-backdrop /usr/local/bin/
```

Binaire universel (Apple Silicon et Intel), signé localement (ad-hoc). L'empreinte SHA-256 est dans `claude-backdrop-macos.tar.gz.sha256`. Tout le reste est dans le [README](https://github.com/M-U-C-K-A/claude-code#readme).

> **Non officiel.** L'outil modifie Claude.app et le re-signe localement ; les mises à jour automatiques de Claude échouent tant que le thème est posé (voir *Mises à jour* dans le README).
