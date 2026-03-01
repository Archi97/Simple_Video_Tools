from __future__ import annotations
from PySide6.QtWidgets import QAbstractButton
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, Property, QRectF, QSize
)
from PySide6.QtGui import QPainter, QColor


class ToggleSwitch(QAbstractButton):
    """
    Pill toggle switch with animated knob.
    Uses a custom _active flag instead of Qt's disabled state so that
    mouse events are always received — allowing clicked_while_disabled to fire.
    """

    clicked_while_disabled = Signal()

    COLOR_OFF  = QColor("#3a3a3a")
    COLOR_ON   = QColor("#5b8af4")
    COLOR_KNOB = QColor("#ffffff")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(46, 26)
        self.setToolTip("Click to enable / disable")

        self._active: bool = False   # custom active flag — NOT Qt's enabled state
        self._position: float = 0.0
        self._anim = QPropertyAnimation(self, b"position", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.toggled.connect(self._start_anim)

    # ── Custom active state ───────────────────────────────────────────────────

    def set_active(self, active: bool) -> None:
        self._active = active
        if not active:
            # Force off without emitting toggled (block signals briefly)
            self.blockSignals(True)
            self.setChecked(False)
            self.blockSignals(False)
            self._position = 0.0
        self.update()

    def is_active(self) -> bool:
        return self._active

    # ── Animation property ────────────────────────────────────────────────────

    def _get_position(self) -> float:
        return self._position

    def _set_position(self, pos: float) -> None:
        self._position = pos
        self.update()

    position = Property(float, _get_position, _set_position)

    def _start_anim(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._position)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    # ── Mouse ─────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:
        if not self._active:
            self.clicked_while_disabled.emit()
            return
        super().mousePressEvent(event)

    # ── Painting ──────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        if not self._active:
            p.setOpacity(0.30)

        w, h = self.width(), self.height()
        r = h / 2

        bg = QColor(
            int(self.COLOR_OFF.red()   + (self.COLOR_ON.red()   - self.COLOR_OFF.red())   * self._position),
            int(self.COLOR_OFF.green() + (self.COLOR_ON.green() - self.COLOR_OFF.green()) * self._position),
            int(self.COLOR_OFF.blue()  + (self.COLOR_ON.blue()  - self.COLOR_OFF.blue())  * self._position),
        )

        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        margin = 3
        knob_d = h - margin * 2
        travel = w - knob_d - margin * 2
        knob_x = margin + travel * self._position

        p.setBrush(self.COLOR_KNOB)
        p.drawEllipse(QRectF(knob_x, margin, knob_d, knob_d))
        p.end()

    def sizeHint(self) -> QSize:
        return QSize(46, 26)
