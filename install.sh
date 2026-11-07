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

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[aviso]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[erro]\033[0m %s\n' "$*" >&2; exit 1; }

for arg in "$@"; do
  case "$arg" in
    --no-gui)  WITH_GUI=0 ;;
    --no-udev) WITH_UDEV=0 ;;
    -h|--help) echo "Uso: ./install.sh [--no-gui] [--no-udev]"; exit 0 ;;
    *) die "opção desconhecida: $arg" ;;
  esac
done

[[ $EUID -ne 0 ]] || die "Não rode como root. Rode como seu usuário; o sudo é pedido só quando necessário."
[[ -f "$SRC_DIR/pyproject.toml" ]] || die "pyproject.toml não encontrado em $SRC_DIR"
command -v python3 >/dev/null || die "python3 não encontrado"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "É necessário Python 3.10 ou mais novo"

is_installed() { dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"; }
need=()
if command -v dpkg-query >/dev/null; then
  is_installed python3-venv || need+=(python3-venv)
  command -v notify-send >/dev/null || need+=(libnotify-bin)
  if [[ $WITH_GUI -eq 1 ]]; then
    is_installed libxcb-cursor0 || need+=(libxcb-cursor0)
  fi
else
  warn "dpkg não encontrado (não é Ubuntu/Debian?): pulando verificação de pacotes do sistema"
fi
if ((${#need[@]})); then
  info "Instalando pacotes do sistema: ${need[*]} (pede senha do sudo)"
  sudo apt-get install -y "${need[@]}"
fi
ok "Dependências do sistema"

info "Preparando ambiente Python em $VENV"
mkdir -p "$PREFIX"
if [[ ! -x "$VENV/bin/python" ]] || ! "$VENV/bin/python" -c 'import sys' 2>/dev/null; then
  rm -rf "$VENV"
  python3 -m venv "$VENV"
fi
PIP=("$VENV/bin/pip" --disable-pip-version-check -q)
SPEC="$SRC_DIR"
[[ $WITH_GUI -eq 1 ]] && SPEC="$SRC_DIR[gui]"
if [[ $WITH_GUI -eq 1 ]] && ! "$VENV/bin/python" -c 'import PySide6' 2>/dev/null; then
  info "Baixando PySide6 (cerca de 270 MB na primeira vez)…"
fi
"${PIP[@]}" uninstall -y "$APP_ID" >/dev/null 2>&1 || true
"${PIP[@]}" install "$SPEC"
rm -rf "$SRC_DIR/build"
ok "Pacote instalado"

mkdir -p "$BIN_DIR"
ln -sf "$VENV/bin/redragon-battery" "$BIN_DIR/redragon-battery"
if [[ $WITH_GUI -eq 1 ]]; then
  ln -sf "$VENV/bin/redragon-battery-gui" "$BIN_DIR/redragon-battery-gui"
fi
ok "Comandos em $BIN_DIR"

install -m 755 "$SRC_DIR/uninstall.sh" "$PREFIX/uninstall.sh"
ln -sf "$PREFIX/uninstall.sh" "$BIN_DIR/redragon-battery-uninstall"

if [[ $WITH_GUI -eq 1 ]]; then
  QT_QPA_PLATFORM=offscreen "$VENV/bin/python" -m redragon_monitor.ui.icons "$ICON_FILE" 2>/dev/null \
    || warn "não foi possível gerar o ícone; o menu usará um ícone genérico"
  icon_name="$APP_ID"
  [[ -f "$ICON_FILE" ]] || icon_name="input-mouse"
  mkdir -p "$APPS_DIR"
  cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Redragon Battery Monitor
Comment=Bateria do mouse Redragon M719RGB-PRO
Exec="$VENV/bin/redragon-battery-gui"
Icon=$icon_name
Terminal=false
Categories=Utility;System;Monitor;
Keywords=mouse;bateria;battery;redragon;
StartupNotify=false
EOF
  ok "Atalho no menu de aplicativos"

  if [[ -f "$CONFIG_HOME/autostart/$APP_ID.desktop" ]]; then
    "$VENV/bin/python" -c 'from redragon_monitor.services import autostart; autostart.enable()'
    ok "Autostart atualizado para esta instalação"
  fi
fi

if [[ $WITH_UDEV -eq 1 ]]; then
  if [[ -f "$UDEV_DST" ]] && cmp -s "$UDEV_SRC" "$UDEV_DST"; then
    ok "Regra udev já instalada"
  else
    info "Instalando regra udev em $UDEV_DST (pede senha do sudo)"
    echo "    Libera ao usuário logado somente a interface 1 (bateria) de 3554:f5d5 e 3554:f55e."
    sudo install -m 644 "$UDEV_SRC" "$UDEV_DST"
    sudo udevadm control --reload-rules
    sudo udevadm trigger --subsystem-match=hidraw --action=change
    ok "Regra udev instalada"
  fi
else
  warn "Regra udev não instalada (--no-udev): o acesso ao mouse vai exigir sudo"
fi

echo
info "Teste de leitura:"
set +e
"$VENV/bin/redragon-battery"
rc=$?
set -e
case $rc in
  0) ok "Leitura da bateria funcionando" ;;
  2) warn "Mouse não respondeu (desligado ou em repouso). Mexa o mouse e rode: redragon-battery" ;;
  *) warn "Sem leitura agora. Se for permissão, desconecte e reconecte o receptor/cabo e rode: redragon-battery" ;;
esac

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR não está no PATH desta sessão. Faça logout/login ou use $VENV/bin/redragon-battery" ;;
esac

echo
ok "Instalação concluída: $("$VENV/bin/redragon-battery" --version)"
echo "    Terminal:  redragon-battery   (ou: redragon-battery --watch 30)"
[[ $WITH_GUI -eq 1 ]] && echo "    Interface: procure \"Redragon Battery Monitor\" no menu ou rode redragon-battery-gui"
echo "    Remover:   redragon-battery-uninstall"
