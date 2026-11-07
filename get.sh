#!/usr/bin/env bash
set -euo pipefail

STABLE_REF="v0.5.1"

detect_lang() {
  local value
  for value in "${REDRAGON_LANG:-}" "${LANGUAGE:-}" "${LC_ALL:-}" "${LC_MESSAGES:-}" "${LANG:-}"; do
    [[ -n "$value" ]] || continue
    [[ "$value" == pt* ]] && { echo pt; return; }
    echo en
    return
  done
  echo en
}
UI_LANG="$(detect_lang)"
t() { if [[ "$UI_LANG" == pt ]]; then printf '%s' "$1"; else printf '%s' "$2"; fi; }

TMP_DIR=""
cleanup() { [[ -n "$TMP_DIR" ]] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT

main() {
  local repo="${REDRAGON_REPO:-jean-devbr/redragon-battery-monitor}"
  local ref="${REDRAGON_REF:-$STABLE_REF}"
  local url="${REDRAGON_TARBALL_URL:-https://github.com/${repo}/archive/${ref}.tar.gz}"

  if [[ $EUID -eq 0 ]]; then
    echo "[$(t erro error)] $(t "Não rode como root (nem com sudo). O instalador pede sudo só quando precisar." "Do not run as root (or with sudo). The installer asks for sudo only when needed.")" >&2
    exit 1
  fi
  command -v tar >/dev/null || { echo "[$(t erro error)] 'tar' $(t "não encontrado" "not found")" >&2; exit 1; }

  TMP_DIR="$(mktemp -d)"
  local tmp="$TMP_DIR"

  echo "==> Redragon Battery Monitor ${ref}"
  echo "==> $(t Baixando Downloading) $url"
  if command -v curl >/dev/null; then
    curl -fsSL "$url" -o "$tmp/src.tar.gz" \
      || { echo "[$(t erro error)] $(t "Falha ao baixar" "Failed to download") ${ref}. $(t "A versão existe no GitHub?" "Does this version exist on GitHub?")" >&2; exit 1; }
  elif command -v wget >/dev/null; then
    wget -qO "$tmp/src.tar.gz" "$url" \
      || { echo "[$(t erro error)] $(t "Falha ao baixar" "Failed to download") ${ref}. $(t "A versão existe no GitHub?" "Does this version exist on GitHub?")" >&2; exit 1; }
  else
    echo "[$(t erro error)] $(t "É necessário curl ou wget" "curl or wget is required")" >&2
    exit 1
  fi

  tar -xzf "$tmp/src.tar.gz" -C "$tmp"
  local src
  src="$(find "$tmp" -mindepth 1 -maxdepth 1 -type d | head -n1)"
  [[ -x "$src/install.sh" ]] || { echo "[$(t erro error)] $(t "install.sh não encontrado no pacote baixado" "install.sh not found in the downloaded package")" >&2; exit 1; }

  if { : </dev/tty; } 2>/dev/null; then
    "$src/install.sh" "$@" </dev/tty
  else
    "$src/install.sh" "$@" </dev/null
  fi
}

main "$@"
