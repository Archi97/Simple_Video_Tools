from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSlider, QDoubleSpinBox
from PySide6.QtCore import Qt
from .base import OperationWidget

MIN_SPEED = 0.1
MAX_SPEED = 8.0
SLIDER_SCALE = 100  # slider integer = speed * SLIDER_SCALE


class SpeedOperation(OperationWidget):
    TITLE = "Speed Change"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        # Value display
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Speed"))
        self._value_label = QLabel("1.00×")
        self._value_label.setObjectName("labelAccent")
        top_row.addStretch()
        top_row.addWidget(self._value_label)
        layout.addLayout(top_row)

        # Slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(
            int(MIN_SPEED * SLIDER_SCALE),
            int(MAX_SPEED * SLIDER_SCALE),
        )
        self._slider.setValue(SLIDER_SCALE)  # 1.0x
        self._slider.setTickInterval(SLIDER_SCALE)
        self._slider.valueChanged.connect(self._on_slider)
        layout.addWidget(self._slider)

        # Range labels
        range_row = QHBoxLayout()
        lbl_min = QLabel(f"{MIN_SPEED}×")
        lbl_min.setObjectName("labelMuted")
        lbl_max = QLabel(f"{MAX_SPEED}×")
        lbl_max.setObjectName("labelMuted")
        lbl_max.setAlignment(Qt.AlignRight)
        range_row.addWidget(lbl_min)
        range_row.addStretch()
        range_row.addWidget(lbl_max)
        layout.addLayout(range_row)

        note = QLabel("Audio pitch is corrected automatically.")
        note.setObjectName("labelMuted")
        layout.addWidget(note)

    def _on_slider(self, value: int) -> None:
        speed = value / SLIDER_SCALE
        self._value_label.setText(f"{speed:.2f}×")

    def _get_speed(self) -> float:
        return self._slider.value() / SLIDER_SCALE

    def get_config(self) -> dict[str, Any]:
        return {"speed": self._get_speed()}

    def load_config(self, config: dict[str, Any]) -> None:
        if "speed" in config:
            self._slider.setValue(int(config["speed"] * SLIDER_SCALE))
        self._toggle.setChecked(config.get("enabled", False))
