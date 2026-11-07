"""Ícone de bateria desenhado em tempo real (não depende do tema de ícones)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QIcon, QPainter, QPainterPath, QPen, QPixmap

GREEN = QColor("#2e9d4f")
AMBER = QColor("#d98a00")
RED = QColor("#d0342c")
GREY = QColor("#8a8a8a")
OUTLINE = QColor("#f2f2f2")
CHARGING = QColor("#ffd400")
TEXT_SHADOW = QColor(0, 0, 0, 200)


def level_color(percent: int, threshold: int = 20) -> QColor:
    if percent <= threshold:
        return RED
    if percent <= 50:
        return AMBER
    return GREEN


def battery_pixmap(
    percent: Optional[int],
    charging: bool = False,
    threshold: int = 20,
    size: int = 64,
    show_text: bool = True,
) -> QPixmap:
    """percent=None => estado desconhecido (cinza, '?'). Nunca desenha um nível inventado."""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)

    s = size / 64.0
    compact = size <= 24  # bandeja: corpo mais alto para o número caber legível
    if compact:
        body = QRectF(1 * s, 6 * s, 56 * s, 52 * s)
        nub = QRectF(57 * s, 22 * s, 6 * s, 20 * s)
    else:
        body = QRectF(2 * s, 14 * s, 54 * s, 36 * s)
        nub = QRectF(56 * s, 25 * s, 6 * s, 14 * s)
    # contorno amarelo = carregando (visível mesmo no tamanho da bandeja)
    outline = GREY if percent is None else (CHARGING if charging else OUTLINE)
    pen = QPen(outline, 4 * s)
    p.setPen(pen)
    p.setBrush(QColor(0, 0, 0, 90))
    p.drawRoundedRect(body, 6 * s, 6 * s)
    p.setPen(Qt.NoPen)
    p.setBrush(pen.color())
    p.drawRoundedRect(nub, 2 * s, 2 * s)

    pad = 4 * s if compact else 5 * s
    inner = body.adjusted(pad, pad, -pad, -pad)
    if percent is not None:
        fill = QRectF(inner)
        fill.setWidth(max(2 * s, inner.width() * percent / 100.0))
        p.setBrush(level_color(percent, threshold))
        p.drawRoundedRect(fill, 3 * s, 3 * s)

    if not show_text:
        p.end()
        return pm

    # texto: número (ou '?') com contorno escuro para ser legível sobre qualquer cor
    label = "?" if percent is None else str(percent)
    font = QFont()
    font.setBold(True)
    if compact:
        font.setPixelSize(max(8, int((40 if len(label) < 3 else 30) * s)))
    else:
        font.setPixelSize(int((26 if len(label) < 3 else 21) * s))
    path = QPainterPath()
    fm = QFontMetricsF(font)
    w = fm.horizontalAdvance(label)
    baseline = QPointF(body.center().x() - w / 2, body.center().y() + fm.capHeight() / 2)
    path.addText(baseline, font, label)
    p.setPen(QPen(TEXT_SHADOW, (2.5 if compact else 4) * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(path)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("white"))
    p.drawPath(path)

    if charging and percent is not None and size >= 32:
        bolt = QPainterPath()
        pts = [(40, 0), (26, 22), (36, 22), (30, 40), (48, 14), (37, 14), (44, 0)]
        bolt.moveTo(pts[0][0] * s, pts[0][1] * s)
        for x, y in pts[1:]:
            bolt.lineTo(x * s, y * s)
        bolt.closeSubpath()
        bolt.translate(10 * s, 0)
        p.setPen(QPen(TEXT_SHADOW, 2 * s))
        p.setBrush(CHARGING)
        p.drawPath(bolt)

    p.end()
    return pm


def battery_icon(percent: Optional[int], charging: bool = False, threshold: int = 20) -> QIcon:
    icon = QIcon()
    for size in (16, 22, 24, 32, 48, 64, 128):
        icon.addPixmap(battery_pixmap(percent, charging, threshold, size))
    return icon


def app_icon() -> QIcon:
    """Ícone do aplicativo (bateria cheia, sem número — não representa uma leitura)."""
    icon = QIcon()
    for size in (32, 48, 64, 128, 256):
        icon.addPixmap(battery_pixmap(100, size=size, show_text=False))
    return icon


def save_app_icon(path: str, size: int = 256) -> None:
    from PySide6.QtGui import QGuiApplication

    _app = QGuiApplication.instance() or QGuiApplication([])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not battery_pixmap(100, size=size, show_text=False).save(path, "PNG"):
        raise OSError(f"não foi possível salvar {path}")


if __name__ == "__main__":
    save_app_icon(sys.argv[1])
