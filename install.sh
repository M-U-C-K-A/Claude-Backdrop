#!/usr/bin/env bash
# claude-backdrop — installe la dernière version (macOS), sans cloner le dépôt :
#
#   curl -fsSL https://github.com/M-U-C-K-A/claude-code/releases/latest/download/install.sh | bash
#
# Télécharge le binaire de la release (universel : Apple Silicon et Intel),
# vérifie son empreinte SHA-256 et le pose dans un dossier du PATH. Relancer
# le script met l'outil à jour.
#   CLAUDE_BACKDROP_VERSION=v1.0.0   une version précise plutôt que la dernière
#   CLAUDE_BACKDROP_BIN=<dossier>    où poser la commande
set -euo pipefail

repo="M-U-C-K-A/claude-code"
asset="claude-backdrop-macos.tar.gz"

say() { printf '\033[1;33m›\033[0m %s\n' "$*"; }
ok() { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(uname -s)" = "Darwin" ] || fail "claude-backdrop ne fonctionne que sur macOS."

version="${CLAUDE_BACKDROP_VERSION:-latest}"
if [ "$version" = "latest" ]; then
  base="https://github.com/$repo/releases/latest/download"
else
  base="https://github.com/$repo/releases/download/$version"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

say "Téléchargement de claude-backdrop ($version)…"
curl -fsSL "$base/$asset" -o "$tmp/$asset" || fail "téléchargement impossible : $base/$asset"
curl -fsSL "$base/$asset.sha256" -o "$tmp/$asset.sha256" || fail "empreinte introuvable : $base/$asset.sha256"
(cd "$tmp" && shasum -a 256 -c "$asset.sha256" >/dev/null 2>&1) || fail "l'archive ne correspond pas à son empreinte SHA-256"
tar -xzf "$tmp/$asset" -C "$tmp"

dest="${CLAUDE_BACKDROP_BIN:-}"
if [ -z "$dest" ]; then
  if [ -d /usr/local/bin ] && [ -w /usr/local/bin ]; then
    dest=/usr/local/bin
  elif [ -d /opt/homebrew/bin ] && [ -w /opt/homebrew/bin ]; then
    dest=/opt/homebrew/bin
  else
    dest="$HOME/.local/bin"
  fi
fi
mkdir -p "$dest"
install -m 0755 "$tmp/claude-backdrop" "$dest/claude-backdrop"
# curl ne met pas d'attribut de quarantaine, mais un ancien binaire en a peut-être un
xattr -d com.apple.quarantine "$dest/claude-backdrop" 2>/dev/null || true

ok "$("$dest/claude-backdrop" version) installé dans $dest"
case ":$PATH:" in
  *":$dest:"*) ;;
  *)
    echo "  $dest n'est pas encore dans ton PATH. Ajoute-le, puis ouvre un nouveau terminal :"
    echo "    echo 'export PATH=\"$dest:\$PATH\"' >> ~/.zshrc"
    ;;
esac
echo "  Lance « claude-backdrop » puis choisis Installer."
