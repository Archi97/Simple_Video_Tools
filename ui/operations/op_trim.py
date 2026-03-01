from __future__ import annotations
from typing import Any, Optional
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QWidget
)
from PySide6.QtCore import Qt
from .base import OperationWidget


class TimeInput(QWidget):
    """HH:MM:SS spinbox group."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setFixedWidth(38)
        lbl.setObjectName("labelMuted")
        layout.addWidget(lbl)

        self._h = QSpinBox()
        self._h.setRange(0, 99)
        self._h.setFixedWidth(46)
        self._h.setAlignment(Qt.AlignCenter)
        self._h.setToolTip("Hours")

        sep1 = QLabel(":")
        sep1.setFixedWidth(8)
        sep1.setAlignment(Qt.AlignCenter)
        sep1.setObjectName("labelMuted")

        self._m = QSpinBox()
        self._m.setRange(0, 59)
        self._m.setFixedWidth(46)
        self._m.setAlignment(Qt.AlignCenter)
        self._m.setToolTip("Minutes")

        sep2 = QLabel(":")
        sep2.setFixedWidth(8)
        sep2.setAlignment(Qt.AlignCenter)
        sep2.setObjectName("labelMuted")

        self._s = QSpinBox()
        self._s.setRange(0, 59)
        self._s.setFixedWidth(46)
        self._s.setAlignment(Qt.AlignCenter)
        self._s.setToolTip("Seconds")

        layout.addWidget(self._h)
        layout.addWidget(sep1)
        layout.addWidget(self._m)
        layout.addWidget(sep2)
        layout.addWidget(self._s)
        layout.addStretch()

    def set_seconds(self, total: float) -> None:
        t = int(total)
        self._h.setValue(t // 3600)
        self._m.setValue((t % 3600) // 60)
        self._s.setValue(t % 60)

    def to_seconds(self) -> float:
        return self._h.value() * 3600 + self._m.value() * 60 + self._s.value()

    def setEnabled(self, enabled: bool) -> None:
        self._h.setEnabled(enabled)
        self._m.setEnabled(enabled)
        self._s.setEnabled(enabled)


class TrimOperation(OperationWidget):
    TITLE = "Trim"
    BATCH_SUPPORTED = False

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._duration_label = QLabel("Duration: —")
        self._duration_label.setObjectName("labelMuted")
        layout.addWidget(self._duration_label)

        self._start = TimeInput("Start")
        layout.addWidget(self._start)

        self._end = TimeInput("End")
        layout.addWidget(self._end)

        hint = QLabel("Leave End at 00:00:00 to trim to end of file.")
        hint.setObjectName("labelMuted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def load_info(self, info) -> None:
        self._duration_label.setText(f"Duration: {info.duration_str}")
        self._end.set_seconds(info.duration)

    def get_config(self) -> dict[str, Any]:
        return {
            "trim_start": self._start.to_seconds(),
            "trim_end": self._end.to_seconds() or None,
        }

    def load_config(self, config: dict[str, Any]) -> None:
        if "trim_start" in config and config["trim_start"] is not None:
            self._start.set_seconds(config["trim_start"])
        if "trim_end" in config and config["trim_end"] is not None:
            self._end.set_seconds(config["trim_end"])
        self._toggle.setChecked(config.get("enabled", False))
