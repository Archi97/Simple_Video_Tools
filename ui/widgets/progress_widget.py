from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottomBar")
        self.setFixedHeight(56)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 8)
        layout.setSpacing(4)

        self._status = QLabel("Ready.")
        self._status.setObjectName("labelMuted")
        self._status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._status)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(6)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar)

    def set_progress(self, value: int, message: str = "") -> None:
        self._bar.setValue(value)
        if message:
            self._status.setText(message)

    def reset(self) -> None:
        self._bar.setValue(0)
        self._status.setText("Ready.")
