from __future__ import annotations
from typing import Any, Optional
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QWidget, QGridLayout
)
from PySide6.QtCore import Qt
from .base import OperationWidget

ASPECT_RATIOS = [
    ("16:9",  16, 9),
    ("4:3",   4,  3),
    ("1:1",   1,  1),
    ("9:16",  9,  16),
    ("21:9",  21, 9),
    ("3:2",   3,  2),
]


class CropOperation(OperationWidget):
    TITLE = "Crop"
    BATCH_SUPPORTED = False

    def __init__(self, parent=None):
        self._src_w = 0
        self._src_h = 0
        super().__init__(parent)

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._res_label = QLabel("Source: —")
        self._res_label.setObjectName("labelMuted")
        layout.addWidget(self._res_label)

        # Aspect ratio presets
        preset_label = QLabel("Aspect ratio presets")
        preset_label.setObjectName("sectionTitle")
        layout.addWidget(preset_label)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)
        self._preset_btns: list[QPushButton] = []
        for label, rw, rh in ASPECT_RATIOS:
            btn = QPushButton(label)
            btn.setObjectName("btnSmall")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, w=rw, h=rh: self._apply_preset(w, h))
            preset_row.addWidget(btn)
            self._preset_btns.append(btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        # Coordinate inputs
        coord_label = QLabel("Crop area")
        coord_label.setObjectName("sectionTitle")
        layout.addWidget(coord_label)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        grid.addWidget(QLabel("Top-left X"), 0, 0)
        self._x1 = QSpinBox()
        self._x1.setRange(0, 9999)
        grid.addWidget(self._x1, 0, 1)

        grid.addWidget(QLabel("Top-left Y"), 0, 2)
        self._y1 = QSpinBox()
        self._y1.setRange(0, 9999)
        grid.addWidget(self._y1, 0, 3)

        grid.addWidget(QLabel("Bottom-right X"), 1, 0)
        self._x2 = QSpinBox()
        self._x2.setRange(0, 9999)
        grid.addWidget(self._x2, 1, 1)

        grid.addWidget(QLabel("Bottom-right Y"), 1, 2)
        self._y2 = QSpinBox()
        self._y2.setRange(0, 9999)
        grid.addWidget(self._y2, 1, 3)

        layout.addLayout(grid)

        # Result size indicator
        self._result_label = QLabel("Output: —")
        self._result_label.setObjectName("labelAccent")
        layout.addWidget(self._result_label)

        for sp in (self._x1, self._y1, self._x2, self._y2):
            sp.valueChanged.connect(self._update_result_label)

    def _apply_preset(self, ratio_w: int, ratio_h: int) -> None:
        if not self._src_w or not self._src_h:
            return
        src_ratio = self._src_w / self._src_h
        target_ratio = ratio_w / ratio_h

        if src_ratio > target_ratio:
            # Letterbox on sides
            new_h = self._src_h
            new_w = int(new_h * target_ratio)
        else:
            new_w = self._src_w
            new_h = int(new_w / target_ratio)

        # Make even
        new_w -= new_w % 2
        new_h -= new_h % 2

        x = (self._src_w - new_w) // 2
        y = (self._src_h - new_h) // 2

        for sp in (self._x1, self._y1, self._x2, self._y2):
            sp.blockSignals(True)
        self._x1.setValue(x)
        self._y1.setValue(y)
        self._x2.setValue(x + new_w)
        self._y2.setValue(y + new_h)
        for sp in (self._x1, self._y1, self._x2, self._y2):
            sp.blockSignals(False)
        self._update_result_label()

    def _update_result_label(self) -> None:
        x1, y1 = self._x1.value(), self._y1.value()
        x2, y2 = self._x2.value(), self._y2.value()
        w, h = x2 - x1, y2 - y1
        invalid = (
            w <= 0 or h <= 0
            or (self._src_w and x2 > self._src_w)
            or (self._src_h and y2 > self._src_h)
        )
        if invalid:
            self._result_label.setObjectName("labelDanger")
            self._result_label.setText(f"Output: {w} × {h} px — invalid crop area")
        else:
            self._result_label.setObjectName("labelAccent")
            self._result_label.setText(f"Output: {w} × {h} px")
        self._result_label.style().unpolish(self._result_label)
        self._result_label.style().polish(self._result_label)

    def load_info(self, info) -> None:
        self._src_w = info.width
        self._src_h = info.height
        self._res_label.setText(f"Source: {info.width} × {info.height} px")
        for sp in (self._x1, self._y1):
            sp.setValue(0)
        self._x2.setValue(info.width)
        self._y2.setValue(info.height)
        for sp in (self._x1, self._x2):
            sp.setMaximum(info.width)
        for sp in (self._y1, self._y2):
            sp.setMaximum(info.height)
        self._update_result_label()

    def get_config(self) -> dict[str, Any]:
        x = self._x1.value()
        y = self._y1.value()
        w = self._x2.value() - x
        h = self._y2.value() - y
        return {"crop": (x, y, w, h)}

    def load_config(self, config: dict[str, Any]) -> None:
        if "crop" in config:
            x, y, w, h = config["crop"]
            self._x1.setValue(x)
            self._y1.setValue(y)
            self._x2.setValue(x + w)
            self._y2.setValue(y + h)
        self._toggle.setChecked(config.get("enabled", False))
