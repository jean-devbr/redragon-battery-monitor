from __future__ import annotations

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
BODY_BACKGROUND = QColor(0, 0, 0, 90)
WHITE = QColor("white")

BASE_SIZE = 64.0
COMPACT_MAX_SIZE = 24
BOLT_MIN_SIZE = 32
AMBER_LIMIT = 50
DEFAULT_THRESHOLD = 20
TRAY_SIZES = (16, 22, 24, 32, 48, 64, 128)
APP_SIZES = (32, 48, 64, 128, 256)
BOLT_POINTS = [(40, 0), (26, 22), (36, 22), (30, 40), (48, 14), (37, 14), (44, 0)]


class BatteryIconPainter:
    def pixmap(
        self,
        percent: Optional[int],
        charging: bool = False,
        threshold: int = DEFAULT_THRESHOLD,
        size: int = 64,
        show_text: bool = True,
    ) -> QPixmap:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        scale = size / BASE_SIZE
        compact = size <= COMPACT_MAX_SIZE
        body = self._draw_body(painter, percent, charging, scale, compact)
        self._draw_fill(painter, body, percent, threshold, scale, compact)
        if show_text:
            self._draw_label(painter, body, percent, scale, compact)
        if show_text and charging and percent is not None and size >= BOLT_MIN_SIZE:
            self._draw_bolt(painter, scale)
        painter.end()
        return pixmap

    def icon(self, percent: Optional[int], charging: bool = False, threshold: int = DEFAULT_THRESHOLD) -> QIcon:
        icon = QIcon()
        for size in TRAY_SIZES:
            icon.addPixmap(self.pixmap(percent, charging, threshold, size))
        return icon

    def app_icon(self) -> QIcon:
        icon = QIcon()
        for size in APP_SIZES:
            icon.addPixmap(self.pixmap(100, size=size, show_text=False))
        return icon

    def save_app_icon(self, path: str, size: int = 256) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if not self.pixmap(100, size=size, show_text=False).save(path, "PNG"):
            raise OSError(f"não foi possível salvar {path}")

    @staticmethod
    def level_color(percent: int, threshold: int = DEFAULT_THRESHOLD) -> QColor:
        if percent <= threshold:
            return RED
        if percent <= AMBER_LIMIT:
            return AMBER
        return GREEN

    @staticmethod
    def _outline_color(percent: Optional[int], charging: bool) -> QColor:
        if percent is None:
            return GREY
        return CHARGING if charging else OUTLINE

    def _draw_body(self, painter: QPainter, percent: Optional[int], charging: bool, s: float, compact: bool) -> QRectF:
        body = QRectF(1 * s, 6 * s, 56 * s, 52 * s) if compact else QRectF(2 * s, 14 * s, 54 * s, 36 * s)
        nub = QRectF(57 * s, 22 * s, 6 * s, 20 * s) if compact else QRectF(56 * s, 25 * s, 6 * s, 14 * s)
        pen = QPen(self._outline_color(percent, charging), 4 * s)
        painter.setPen(pen)
        painter.setBrush(BODY_BACKGROUND)
        painter.drawRoundedRect(body, 6 * s, 6 * s)
        painter.setPen(Qt.NoPen)
        painter.setBrush(pen.color())
        painter.drawRoundedRect(nub, 2 * s, 2 * s)
        return body

    def _draw_fill(
        self, painter: QPainter, body: QRectF, percent: Optional[int], threshold: int, s: float, compact: bool
    ) -> None:
        if percent is None:
            return
        pad = (4 if compact else 5) * s
        inner = body.adjusted(pad, pad, -pad, -pad)
        fill = QRectF(inner)
        fill.setWidth(max(2 * s, inner.width() * percent / 100.0))
        painter.setBrush(self.level_color(percent, threshold))
        painter.drawRoundedRect(fill, 3 * s, 3 * s)

    @staticmethod
    def _draw_label(painter: QPainter, body: QRectF, percent: Optional[int], s: float, compact: bool) -> None:
        label = "?" if percent is None else str(percent)
        short = len(label) < 3
        font = QFont()
        font.setBold(True)
        compact_size = max(8, int((40 if short else 30) * s))
        regular_size = int((26 if short else 21) * s)
        font.setPixelSize(compact_size if compact else regular_size)
        metrics = QFontMetricsF(font)
        baseline = QPointF(
            body.center().x() - metrics.horizontalAdvance(label) / 2,
            body.center().y() + metrics.capHeight() / 2,
        )
        path = QPainterPath()
        path.addText(baseline, font, label)
        painter.setPen(QPen(TEXT_SHADOW, (2.5 if compact else 4) * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        painter.setPen(Qt.NoPen)
        painter.setBrush(WHITE)
        painter.drawPath(path)

    @staticmethod
    def _draw_bolt(painter: QPainter, s: float) -> None:
        bolt = QPainterPath()
        first_x, first_y = BOLT_POINTS[0]
        bolt.moveTo(first_x * s, first_y * s)
        for x, y in BOLT_POINTS[1:]:
            bolt.lineTo(x * s, y * s)
        bolt.closeSubpath()
        bolt.translate(10 * s, 0)
        painter.setPen(QPen(TEXT_SHADOW, 2 * s))
        painter.setBrush(CHARGING)
        painter.drawPath(bolt)
