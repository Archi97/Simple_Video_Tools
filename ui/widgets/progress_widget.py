from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from version import VERSION


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottomBar")
        self.setFixedHeight(56)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 8)
        layout.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        self._status = QLabel("Ready.")
        self._status.setObjectName("labelMuted")
        self._status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_row.addWidget(self._status, stretch=1)

        self._credit = QLabel(
            f'v{VERSION} · by Tyombo &nbsp;·&nbsp; '
            f'<a href="https://www.buymeacoffee.com/tyombo" '
            f'style="color:#f5a623; text-decoration:none;">☕ Buy me a coffee</a>'
        )
        self._credit.setOpenExternalLinks(True)
        self._credit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top_row.addWidget(self._credit)

        layout.addLayout(top_row)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(6)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar)

        self._hue = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._cycle_color)
        self._timer.start(40)

    def _cycle_color(self) -> None:
        self._hue = (self._hue + 0.012) % 1.0
        color = QColor.fromHsvF(self._hue, 0.85, 1.0)
        self._credit.setStyleSheet(f"color: {color.name()}; font-weight: 600; font-size: 11px;")

    def set_progress(self, value: int, message: str = "") -> None:
        self._bar.setValue(value)
        if message:
            self._status.setText(message)

    def reset(self) -> None:
        self._bar.setValue(0)
        self._status.setText("Ready.")
