from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
from PySide6.QtCore import Qt
from .base import OperationWidget


class BitrateOperation(OperationWidget):
    TITLE = "Change Bitrate"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._current_label = QLabel("Current: —")
        self._current_label.setObjectName("labelMuted")
        layout.addWidget(self._current_label)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(QLabel("New bitrate"))

        self._input = QSpinBox()
        self._input.setRange(100_000, 100_000_000)
        self._input.setSingleStep(100_000)
        self._input.setValue(5_000_000)
        self._input.setFixedWidth(120)
        self._input.valueChanged.connect(self._update_kbps)
        row.addWidget(self._input)

        self._kbps_label = QLabel("= 5000 Kbps")
        self._kbps_label.setObjectName("labelAccent")
        row.addWidget(self._kbps_label)
        row.addStretch()
        layout.addLayout(row)

    def _update_kbps(self, value: int) -> None:
        self._kbps_label.setText(f"= {value // 1000} Kbps")

    def load_info(self, info) -> None:
        kbps = info.video_bitrate // 1000 if info.video_bitrate else 0
        self._current_label.setText(
            f"Current: {info.video_bitrate:,} bps  ({kbps} Kbps)"
        )
        if info.video_bitrate:
            self._input.setValue(info.video_bitrate)
            self._update_kbps(info.video_bitrate)

    def get_config(self) -> dict[str, Any]:
        return {"video_bitrate": self._input.value()}

    def load_config(self, config: dict[str, Any]) -> None:
        if "video_bitrate" in config:
            self._input.setValue(config["video_bitrate"])
        self._toggle.setChecked(config.get("enabled", False))
