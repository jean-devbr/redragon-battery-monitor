#!/usr/bin/env bash
set -euo pipefail

APP_ID="redragon-battery-monitor"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
PREFIX="$DATA_HOME/$APP_ID"
VENV="$PREFIX/venv"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$DATA_HOME/applications"
ICON_FILE="$DATA_HOME/icons/hicolor/256x256/apps/$APP_ID.png"
DESKTOP_FILE="$APPS_DIR/$APP_ID.desktop"
UDEV_SRC="$SRC_DIR/packaging/udev/70-redragon-m719.rules"
UDEV_DST="/etc/udev/rules.d/70-redragon-m719.rules"

WITH_GUI=1
WITH_UDEV=1

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

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[%s]\033[0m %s\n' "$(t aviso warning)" "$*" >&2; }
die()  { printf '\033[1;31m[%s]\033[0m %s\n' "$(t erro error)" "$*" >&2; exit 1; }

for arg in "$@"; do
  case "$arg" in
    --no-gui)  WITH_GUI=0 ;;
    --no-udev) WITH_UDEV=0 ;;
    -h|--help) echo "$(t Uso Usage): ./install.sh [--no-gui] [--no-udev]"; exit 0 ;;
    *) die "$(t "opção desconhecida" "unknown option"): $arg" ;;
  esac
done

[[ $EUID -ne 0 ]] || die "$(t "Não rode como root. Rode como seu usuário; o sudo é pedido só quando necessário." "Do not run as root. Run as your user; sudo is requested only when needed.")"
[[ -f "$SRC_DIR/pyproject.toml" ]] || die "$(t "pyproject.toml não encontrado em" "pyproject.toml not found in") $SRC_DIR"
command -v python3 >/dev/null || die "$(t "python3 não encontrado" "python3 not found")"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "$(t "É necessário Python 3.10 ou mais novo" "Python 3.10 or newer is required")"

is_installed() { dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"; }
need=()
if command -v dpkg-query >/dev/null; then
  is_installed python3-venv || need+=(python3-venv)
  command -v notify-send >/dev/null || need+=(libnotify-bin)
  if [[ $WITH_GUI -eq 1 ]]; then
    is_installed libxcb-cursor0 || need+=(libxcb-cursor0)
  fi
else
  warn "$(t "dpkg não encontrado (não é Ubuntu/Debian?): pulando verificação de pacotes do sistema" "dpkg not found (not Ubuntu/Debian?): skipping system package check")"
fi
if ((${#need[@]})); then
  info "$(t "Instalando pacotes do sistema" "Installing system packages"): ${need[*]} ($(t "pede senha do sudo" "asks for sudo password"))"
  sudo apt-get install -y "${need[@]}"
fi
ok "$(t "Dependências do sistema" "System dependencies")"

info "$(t "Preparando ambiente Python em" "Preparing Python environment in") $VENV"
mkdir -p "$PREFIX"
if [[ ! -x "$VENV/bin/python" ]] || ! "$VENV/bin/python" -c 'import sys' 2>/dev/null; then
  rm -rf "$VENV"
  python3 -m venv "$VENV"
fi
PIP=("$VENV/bin/pip" --disable-pip-version-check -q)
SPEC="$SRC_DIR"
[[ $WITH_GUI -eq 1 ]] && SPEC="$SRC_DIR[gui]"
if [[ $WITH_GUI -eq 1 ]] && ! "$VENV/bin/python" -c 'import PySide6' 2>/dev/null; then
  info "$(t "Baixando PySide6 (cerca de 270 MB na primeira vez)…" "Downloading PySide6 (about 270 MB the first time)…")"
fi
"${PIP[@]}" uninstall -y "$APP_ID" >/dev/null 2>&1 || true
"${PIP[@]}" install "$SPEC"
rm -rf "$SRC_DIR/build"
ok "$(t "Pacote instalado" "Package installed")"

mkdir -p "$BIN_DIR"
ln -sf "$VENV/bin/redragon-battery" "$BIN_DIR/redragon-battery"
if [[ $WITH_GUI -eq 1 ]]; then
  ln -sf "$VENV/bin/redragon-battery-gui" "$BIN_DIR/redragon-battery-gui"
fi
ok "$(t "Comandos em" "Commands in") $BIN_DIR"

install -m 755 "$SRC_DIR/uninstall.sh" "$PREFIX/uninstall.sh"
ln -sf "$PREFIX/uninstall.sh" "$BIN_DIR/redragon-battery-uninstall"

if [[ $WITH_GUI -eq 1 ]]; then
  QT_QPA_PLATFORM=offscreen "$VENV/bin/redragon-battery-gui" --export-icon "$ICON_FILE" 2>/dev/null \
    || warn "$(t "não foi possível gerar o ícone; o menu usará um ícone genérico" "could not create the icon; the menu will use a generic one")"
  icon_name="$APP_ID"
  [[ -f "$ICON_FILE" ]] || icon_name="input-mouse"
  mkdir -p "$APPS_DIR"
  cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Redragon Battery Monitor
Comment=Redragon M719RGB-PRO mouse battery
Comment[pt_BR]=Bateria do mouse Redragon M719RGB-PRO
Comment[pt]=Bateria do mouse Redragon M719RGB-PRO
Exec="$VENV/bin/redragon-battery-gui"
Icon=$icon_name
Terminal=false
Categories=Utility;System;Monitor;
Keywords=mouse;bateria;battery;redragon;
StartupNotify=false
EOF
  ok "$(t "Atalho no menu de aplicativos" "Application menu shortcut")"

  if [[ -f "$CONFIG_HOME/autostart/$APP_ID.desktop" ]]; then
    "$VENV/bin/python" -c 'from redragon_monitor.bootstrap.container import Container; Container().autostart().enable()'
    ok "$(t "Autostart atualizado para esta instalação" "Autostart updated for this installation")"
  fi
fi

if [[ $WITH_UDEV -eq 1 ]]; then
  if [[ -f "$UDEV_DST" ]] && cmp -s "$UDEV_SRC" "$UDEV_DST"; then
    ok "$(t "Regra udev já instalada" "udev rule already installed")"
  else
    info "$(t "Instalando regra udev em" "Installing udev rule in") $UDEV_DST ($(t "pede senha do sudo" "asks for sudo password"))"
    echo "    $(t "Libera ao usuário logado somente a interface 1 (bateria) de 3554:f5d5 e 3554:f55e." "Grants the logged-in user access only to interface 1 (battery) of 3554:f5d5 and 3554:f55e.")"
    sudo install -m 644 "$UDEV_SRC" "$UDEV_DST"
    sudo udevadm control --reload-rules
    sudo udevadm trigger --subsystem-match=hidraw --action=change
    ok "$(t "Regra udev instalada" "udev rule installed")"
  fi
else
  warn "$(t "Regra udev não instalada (--no-udev): o acesso ao mouse vai exigir sudo" "udev rule not installed (--no-udev): accessing the mouse will require sudo")"
fi

echo
info "$(t "Teste de leitura:" "Reading test:")"
set +e
"$VENV/bin/redragon-battery"
rc=$?
set -e
case $rc in
  0) ok "$(t "Leitura da bateria funcionando" "Battery reading works")" ;;
  2) warn "$(t "Mouse não respondeu (desligado ou em repouso). Mexa o mouse e rode: redragon-battery" "Mouse did not respond (off or asleep). Move the mouse and run: redragon-battery")" ;;
  *) warn "$(t "Sem leitura agora. Se for permissão, desconecte e reconecte o receptor/cabo e rode: redragon-battery" "No reading right now. If it is a permission issue, unplug and replug the receiver/cable and run: redragon-battery")" ;;
esac

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR $(t "não está no PATH desta sessão. Faça logout/login ou use" "is not in this session PATH. Log out and in again, or use") $VENV/bin/redragon-battery" ;;
esac

echo
ok "$(t "Instalação concluída" "Installation complete"): $("$VENV/bin/redragon-battery" --version)"
echo "    $(t "Terminal" "Terminal"):  redragon-battery   ($(t ou or): redragon-battery --watch 30)"
[[ $WITH_GUI -eq 1 ]] && echo "    $(t Interface Interface): $(t "procure \"Redragon Battery Monitor\" no menu ou rode" "look for \"Redragon Battery Monitor\" in the menu or run") redragon-battery-gui"
echo "    $(t Remover Remove):   redragon-battery-uninstall"
