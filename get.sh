#!/usr/bin/env bash
set -euo pipefail

STABLE_REF="v0.2.0"

TMP_DIR=""
cleanup() { [[ -n "$TMP_DIR" ]] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT

main() {
  local repo="${REDRAGON_REPO:-jean-devbr/redragon-battery-monitor}"
  local ref="${REDRAGON_REF:-$STABLE_REF}"
  local url="${REDRAGON_TARBALL_URL:-https://github.com/${repo}/archive/${ref}.tar.gz}"

  if [[ $EUID -eq 0 ]]; then
    echo "[erro] Não rode como root (nem com sudo). O instalador pede sudo só quando precisar." >&2
    exit 1
  fi
  command -v tar >/dev/null || { echo "[erro] 'tar' não encontrado" >&2; exit 1; }

  TMP_DIR="$(mktemp -d)"
  local tmp="$TMP_DIR"

  echo "==> Redragon Battery Monitor ${ref}"
  echo "==> Baixando $url"
  if command -v curl >/dev/null; then
    curl -fsSL "$url" -o "$tmp/src.tar.gz" \
      || { echo "[erro] Falha ao baixar ${ref}. A versão existe no GitHub?" >&2; exit 1; }
  elif command -v wget >/dev/null; then
    wget -qO "$tmp/src.tar.gz" "$url" \
      || { echo "[erro] Falha ao baixar ${ref}. A versão existe no GitHub?" >&2; exit 1; }
  else
    echo "[erro] É necessário curl ou wget" >&2
    exit 1
  fi

  tar -xzf "$tmp/src.tar.gz" -C "$tmp"
  local src
  src="$(find "$tmp" -mindepth 1 -maxdepth 1 -type d | head -n1)"
  [[ -x "$src/install.sh" ]] || { echo "[erro] install.sh não encontrado no pacote baixado" >&2; exit 1; }

  if { : </dev/tty; } 2>/dev/null; then
    "$src/install.sh" "$@" </dev/tty
  else
    "$src/install.sh" "$@" </dev/null
  fi
}

main "$@"
