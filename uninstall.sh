#!/usr/bin/env bash
# Remove o Redragon Battery Monitor instalado por install.sh.
#
# Uso: ./uninstall.sh [--purge] [--keep-udev]
#   --purge      também apaga as preferências (~/.config/redragon-battery-monitor)
#   --keep-udev  mantém a regra udev
set -euo pipefail

APP_ID="redragon-battery-monitor"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
PREFIX="$DATA_HOME/$APP_ID"
VENV="$PREFIX/venv"
BIN_DIR="$HOME/.local/bin"
UDEV_DST="/etc/udev/rules.d/70-redragon-m719.rules"

PURGE=0
KEEP_UDEV=0
for arg in "$@"; do
  case "$arg" in
    --purge) PURGE=1 ;;
    --keep-udev) KEEP_UDEV=1 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "opção desconhecida: $arg" >&2; exit 1 ;;
  esac
done
[[ $EUID -ne 0 ]] || { echo "Não rode como root." >&2; exit 1; }

ok() { printf '\033[1;32m ✓\033[0m %s\n' "$*"; }

# encerra a GUI instalada, se estiver aberta
pkill -u "$USER" -f "$VENV/bin/" 2>/dev/null && ok "Programa em execução encerrado" || true

# só remove links que apontam para esta instalação
for cmd in redragon-battery redragon-battery-gui redragon-battery-uninstall; do
  link="$BIN_DIR/$cmd"
  if [[ -L "$link" && "$(readlink "$link")" == "$PREFIX/"* ]]; then
    rm -f "$link"
  fi
done
ok "Comandos removidos"

rm -f "$DATA_HOME/applications/$APP_ID.desktop" \
      "$DATA_HOME/icons/hicolor/256x256/apps/$APP_ID.png" \
      "$CONFIG_HOME/autostart/$APP_ID.desktop"
ok "Atalho, ícone e autostart removidos"

rm -rf "$PREFIX"
ok "Ambiente Python removido ($PREFIX)"

if [[ $PURGE -eq 1 ]]; then
  rm -rf "$CONFIG_HOME/$APP_ID"
  ok "Preferências removidas"
fi

if [[ $KEEP_UDEV -eq 0 && -f "$UDEV_DST" ]]; then
  echo "Removendo regra udev $UDEV_DST (pede senha do sudo)"
  sudo rm -f "$UDEV_DST"
  sudo udevadm control --reload-rules
  sudo udevadm trigger --subsystem-match=hidraw --action=change
  ok "Regra udev removida"
fi

echo "Desinstalação concluída. A pasta do código-fonte não foi alterada."
