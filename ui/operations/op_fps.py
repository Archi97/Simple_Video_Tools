from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox
from .base import OperationWidget


class FpsOperation(OperationWidget):
    TITLE = "Change FPS"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._current_label = QLabel("Current FPS: —")
        self._current_label.setObjectName("labelMuted")
        layout.addWidget(self._current_label)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(QLabel("New FPS"))
        self._input = QDoubleSpinBox()
        self._input.setRange(1.0, 240.0)
        self._input.setDecimals(3)
        self._input.setSingleStep(1.0)
        self._input.setValue(30.0)
        self._input.setFixedWidth(100)
        row.addWidget(self._input)
        row.addStretch()
        layout.addLayout(row)

    def load_info(self, info) -> None:
        self._current_label.setText(f"Current FPS: {info.fps:.3f}")
        self._input.setValue(info.fps)

    def get_config(self) -> dict[str, Any]:
        return {"fps": self._input.value()}

    def load_config(self, config: dict[str, Any]) -> None:
        if "fps" in config:
            self._input.setValue(config["fps"])
        self._toggle.setChecked(config.get("enabled", False))
