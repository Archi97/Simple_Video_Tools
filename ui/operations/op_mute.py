from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt
from .base import OperationWidget


class MuteOperation(OperationWidget):
    TITLE = "Volume"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        note = QLabel("0 = mute · 1 = original · up to 3× amplification")
        note.setObjectName("labelMuted")
        layout.addWidget(note)

        row = QHBoxLayout()
        row.setSpacing(10)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 300)
        self._slider.setValue(100)
        self._slider.setSingleStep(1)
        self._slider.valueChanged.connect(self._on_value_changed)
        row.addWidget(self._slider, stretch=1)

        self._value_label = QLabel("1.00×")
        self._value_label.setFixedWidth(44)
        self._value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(self._value_label)

        layout.addLayout(row)

    def _on_value_changed(self, raw: int) -> None:
        self._value_label.setText(f"{raw / 100:.2f}×")

    def get_config(self) -> dict[str, Any]:
        return {"volume": self._slider.value() / 100}

    def load_config(self, config: dict[str, Any]) -> None:
        if "volume" in config:
            self._slider.setValue(int(config["volume"] * 100))
        self._toggle.setChecked(config.get("enabled", False))
