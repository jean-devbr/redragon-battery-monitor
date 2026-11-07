#!/usr/bin/env bash
set -euo pipefail

APP_ID="redragon-battery-monitor"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
PREFIX="$DATA_HOME/$APP_ID"
VENV="$PREFIX/venv"
BIN_DIR="$HOME/.local/bin"
UDEV_DST="/etc/udev/rules.d/70-redragon-m719.rules"

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

PURGE=0
KEEP_UDEV=0
for arg in "$@"; do
  case "$arg" in
    --purge) PURGE=1 ;;
    --keep-udev) KEEP_UDEV=1 ;;
    -h|--help)
      echo "$(t Uso Usage): redragon-battery-uninstall [--purge] [--keep-udev]"
      echo "  --purge      $(t "também apaga as preferências" "also removes preferences")"
      echo "  --keep-udev  $(t "mantém a regra udev" "keeps the udev rule")"
      exit 0 ;;
    *) echo "$(t "opção desconhecida" "unknown option"): $arg" >&2; exit 1 ;;
  esac
done
[[ $EUID -ne 0 ]] || { echo "$(t "Não rode como root." "Do not run as root.")" >&2; exit 1; }

ok() { printf '\033[1;32m ✓\033[0m %s\n' "$*"; }

pkill -u "$USER" -f "$VENV/bin/" 2>/dev/null && ok "$(t "Programa em execução encerrado" "Running program closed")" || true

for cmd in redragon-battery redragon-battery-gui redragon-battery-uninstall; do
  link="$BIN_DIR/$cmd"
  if [[ -L "$link" && "$(readlink "$link")" == "$PREFIX/"* ]]; then
    rm -f "$link"
  fi
done
ok "$(t "Comandos removidos" "Commands removed")"

rm -f "$DATA_HOME/applications/$APP_ID.desktop" \
      "$DATA_HOME/icons/hicolor/256x256/apps/$APP_ID.png" \
      "$CONFIG_HOME/autostart/$APP_ID.desktop"
ok "$(t "Atalho, ícone e autostart removidos" "Shortcut, icon and autostart removed")"

rm -rf "$PREFIX"
ok "$(t "Ambiente Python removido" "Python environment removed") ($PREFIX)"

if [[ $PURGE -eq 1 ]]; then
  rm -rf "$CONFIG_HOME/$APP_ID"
  ok "$(t "Preferências removidas" "Preferences removed")"
fi

if [[ $KEEP_UDEV -eq 0 && -f "$UDEV_DST" ]]; then
  echo "$(t "Removendo regra udev" "Removing udev rule") $UDEV_DST ($(t "pede senha do sudo" "asks for sudo password"))"
  sudo rm -f "$UDEV_DST"
  sudo udevadm control --reload-rules
  sudo udevadm trigger --subsystem-match=hidraw --action=change
  ok "$(t "Regra udev removida" "udev rule removed")"
fi

echo "$(t "Desinstalação concluída." "Uninstall complete.")"
