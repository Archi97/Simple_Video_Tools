from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from .base import OperationWidget

PRESETS = [
    ("8K",    7680, 4320),
    ("4K",    3840, 2160),
    ("2K",    2560, 1440),
    ("1080p", 1920, 1080),
    ("720p",  1280, 720),
    ("480p",  854,  480),
    ("360p",  640,  360),
]


class ResolutionOperation(OperationWidget):
    TITLE = "Change Resolution"
    BATCH_SUPPORTED = False

    def __init__(self, parent=None):
        self._selected: tuple[int, int] | None = None
        super().__init__(parent)

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._current_label = QLabel("Current: —")
        self._current_label.setObjectName("labelMuted")
        layout.addWidget(self._current_label)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)
        self._preset_btns: list[tuple[QPushButton, int, int]] = []
        for name, pw, ph in PRESETS:
            btn = QPushButton(name)
            btn.setObjectName("btnSmall")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, w=pw, h=ph: self._select(w, h))
            preset_row.addWidget(btn)
            self._preset_btns.append((btn, pw, ph))
        preset_row.addStretch()
        layout.addLayout(preset_row)

        self._output_label = QLabel("No preset selected — will be skipped")
        self._output_label.setObjectName("labelMuted")
        layout.addWidget(self._output_label)

    def _select(self, w: int, h: int) -> None:
        self._selected = (w, h)
        self._output_label.setObjectName("labelAccent")
        self._output_label.setText(f"Output: {w} × {h} px")
        self._output_label.style().unpolish(self._output_label)
        self._output_label.style().polish(self._output_label)

    def load_info(self, info) -> None:
        self._current_label.setText(f"Current: {info.width} × {info.height} px")
        self._selected = None
        self._output_label.setObjectName("labelMuted")
        self._output_label.setText("No preset selected — will be skipped")
        self._output_label.style().unpolish(self._output_label)
        self._output_label.style().polish(self._output_label)
        for btn, pw, ph in self._preset_btns:
            too_big = pw > info.width or ph > info.height
            btn.setEnabled(not too_big)
            btn.setToolTip("Upscaling not supported" if too_big else "")

    def get_config(self) -> dict[str, Any]:
        return {"resolution": self._selected}

    def load_config(self, config: dict[str, Any]) -> None:
        if "resolution" in config:
            self._selected = config["resolution"]
            if self._selected:
                for btn, pw, ph in self._preset_btns:
                    btn.setChecked((pw, ph) == self._selected)
        self._toggle.setChecked(config.get("enabled", False))
