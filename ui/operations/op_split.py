from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSpinBox, QPushButton
)
from .base import OperationWidget


class SplitOperation(OperationWidget):
    TITLE = "Split"
    BATCH_SUPPORTED = True

    def __init__(self, parent=None):
        self._src_w = 0
        self._src_h = 0
        super().__init__(parent)

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._src_label = QLabel("Source: —")
        self._src_label.setObjectName("labelMuted")
        layout.addWidget(self._src_label)

        hint = QLabel(
            "X splits left / right.\n"
            "Y splits bottom / top (measured from bottom).\n"
            "Set both for 4 outputs. Leave at 0 to skip that axis."
        )
        hint.setObjectName("labelMuted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # Grid: row 0 = labels+spinboxes, row 1 = half buttons
        # Col: 0=X label, 1=X spinbox, 2=gap, 3=Y label, 4=Y spinbox, 5=stretch
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(4)
        grid.setColumnMinimumWidth(2, 16)  # gap between X and Y
        grid.setColumnStretch(5, 1)

        grid.addWidget(QLabel("X:"), 0, 0)
        self._x = QSpinBox()
        self._x.setRange(0, 99999)
        self._x.setSpecialValueText("—")
        self._x.setSuffix(" px")
        self._x.setFixedWidth(120)
        grid.addWidget(self._x, 0, 1)

        grid.addWidget(QLabel("Y:"), 0, 3)
        self._y = QSpinBox()
        self._y.setRange(0, 99999)
        self._y.setSpecialValueText("—")
        self._y.setSuffix(" px")
        self._y.setFixedWidth(120)
        grid.addWidget(self._y, 0, 4)

        self._half_x_btn = QPushButton("Split by half")
        self._half_x_btn.setObjectName("btnSmall")
        self._half_x_btn.setCheckable(True)
        self._half_x_btn.setFixedWidth(120)
        self._half_x_btn.toggled.connect(self._on_half_x_toggled)
        grid.addWidget(self._half_x_btn, 1, 1)

        self._half_y_btn = QPushButton("Split by half")
        self._half_y_btn.setObjectName("btnSmall")
        self._half_y_btn.setCheckable(True)
        self._half_y_btn.setFixedWidth(120)
        self._half_y_btn.toggled.connect(self._on_half_y_toggled)
        grid.addWidget(self._half_y_btn, 1, 4)

        layout.addLayout(grid)

        self._result_label = QLabel("")
        self._result_label.setObjectName("labelMuted")
        layout.addWidget(self._result_label)

        self._x.valueChanged.connect(self._update_result)
        self._y.valueChanged.connect(self._update_result)

    def _on_half_x_toggled(self, checked: bool) -> None:
        self._x.setEnabled(not checked)
        self._update_result()

    def _on_half_y_toggled(self, checked: bool) -> None:
        self._y.setEnabled(not checked)
        self._update_result()

    def _has_x(self) -> bool:
        return self._half_x_btn.isChecked() or bool(self._x.value())

    def _has_y(self) -> bool:
        return self._half_y_btn.isChecked() or bool(self._y.value())

    def _update_result(self) -> None:
        x, y = self._has_x(), self._has_y()
        if x and y:
            self._result_label.setText(
                "Output: 4 videos — bottom_left, bottom_right, top_left, top_right"
            )
        elif x:
            self._result_label.setText("Output: 2 videos — left, right")
        elif y:
            self._result_label.setText("Output: 2 videos — bottom, top")
        else:
            self._result_label.setText("")

    def load_info(self, info) -> None:
        self._src_w = info.width
        self._src_h = info.height
        self._src_label.setText(f"Source: {info.width} × {info.height} px")
        self._x.setMaximum(info.width - 1)
        self._y.setMaximum(info.height - 1)

    def get_config(self) -> dict[str, Any]:
        half_x = self._half_x_btn.isChecked()
        half_y = self._half_y_btn.isChecked()
        return {
            "split_x": None if half_x else (self._x.value() or None),
            "split_y": None if half_y else (self._y.value() or None),
            "split_x_half": half_x,
            "split_y_half": half_y,
        }

    def load_config(self, config: dict[str, Any]) -> None:
        self._half_x_btn.setChecked(config.get("split_x_half", False))
        self._half_y_btn.setChecked(config.get("split_y_half", False))
        self._x.setValue(config.get("split_x") or 0)
        self._y.setValue(config.get("split_y") or 0)
        self._toggle.setChecked(config.get("enabled", False))
