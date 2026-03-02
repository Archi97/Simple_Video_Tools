from __future__ import annotations
from typing import Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QComboBox, QInputDialog, QMessageBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from core.presets import load_presets, save_preset, delete_preset
from ui.operations.base import OperationWidget
from ui.operations.op_trim import TrimOperation
from ui.operations.op_crop import CropOperation
from ui.operations.op_fps import FpsOperation
from ui.operations.op_bitrate import BitrateOperation
from ui.operations.op_format import FormatOperation
from ui.operations.op_extract_audio import ExtractAudioOperation
from ui.operations.op_mute import MuteOperation
from ui.operations.op_resolution import ResolutionOperation
from ui.operations.op_speed import SpeedOperation
from ui.operations.op_split import SplitOperation
from ui.operations.op_merge_audio import MergeAudioOperation


class OperationsPanel(QWidget):
    config_changed = Signal()

    needs_file = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self._operations: list[OperationWidget] = []
        self._setup_ui()
        self._load_preset_list()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 16, 12, 12)
        root.setSpacing(10)

        # ── Presets bar ───────────────────────────────────────────────────────
        preset_row = QHBoxLayout()
        preset_row.setSpacing(8)

        preset_lbl = QLabel("PRESET")
        preset_lbl.setObjectName("sectionTitle")
        preset_lbl.setFixedWidth(52)
        preset_row.addWidget(preset_lbl)

        self._preset_combo = QComboBox()
        self._preset_combo.setMinimumWidth(140)
        self._preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        preset_row.addWidget(self._preset_combo)

        self._btn_save_preset = QPushButton("Save")
        self._btn_save_preset.setObjectName("btnSmall")
        self._btn_save_preset.clicked.connect(self._save_preset)
        preset_row.addWidget(self._btn_save_preset)

        self._btn_del_preset = QPushButton("Delete")
        self._btn_del_preset.setObjectName("btnDanger")
        self._btn_del_preset.clicked.connect(self._delete_preset)
        preset_row.addWidget(self._btn_del_preset)
        preset_row.addStretch()
        root.addLayout(preset_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        root.addWidget(sep)

        # ── Operations scroll area ────────────────────────────────────────────
        ops_label = QLabel("OPERATIONS")
        ops_label.setObjectName("sectionTitle")
        root.addWidget(ops_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        self._ops_layout = QVBoxLayout(scroll_content)
        self._ops_layout.setContentsMargins(0, 0, 6, 0)
        self._ops_layout.setSpacing(2)
        self._ops_layout.addStretch()

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, stretch=1)

        # Build operations
        op_classes = [
            MuteOperation,
            ExtractAudioOperation,
            FormatOperation,
            FpsOperation,
            BitrateOperation,
            SpeedOperation,
            TrimOperation,
            CropOperation,
            ResolutionOperation,
            SplitOperation,
            MergeAudioOperation,
        ]
        for cls in op_classes:
            op = cls()
            op.expanded.connect(self._on_op_expanded)
            op.needs_file.connect(self.needs_file.emit)
            op._toggle.toggled.connect(lambda _: self.config_changed.emit())
            self._ops_layout.insertWidget(self._ops_layout.count() - 1, op)
            self._operations.append(op)


    # ── Accordion behaviour ───────────────────────────────────────────────────

    def _on_op_expanded(self, clicked_op: OperationWidget) -> None:
        for op in self._operations:
            op.set_open(op is clicked_op and not clicked_op._is_open)

    # ── Preset management ─────────────────────────────────────────────────────

    def _load_preset_list(self) -> None:
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItem("— no preset —", None)
        for name in load_presets():
            self._preset_combo.addItem(name, name)
        self._preset_combo.blockSignals(False)

    def _on_preset_selected(self, index: int) -> None:
        name = self._preset_combo.currentData()
        if not name:
            return
        presets = load_presets()
        if name in presets:
            self.load_all_config(presets[name])

    def _save_preset(self) -> None:
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name.strip():
            save_preset(name.strip(), self.get_all_config())
            self._load_preset_list()
            # Select the saved preset
            idx = self._preset_combo.findData(name.strip())
            if idx >= 0:
                self._preset_combo.setCurrentIndex(idx)

    def _delete_preset(self) -> None:
        name = self._preset_combo.currentData()
        if not name:
            return
        reply = QMessageBox.question(
            self, "Delete Preset", f"Delete preset \"{name}\"?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            delete_preset(name)
            self._load_preset_list()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_active(self, active: bool) -> None:
        for op in self._operations:
            op.set_active(active)

    def set_batch_mode(self, batch: bool) -> None:
        for op in self._operations:
            op.set_batch_mode(batch)

    def load_video_info(self, info) -> None:
        for op in self._operations:
            op.load_info(info)

    def get_all_config(self) -> dict[str, Any]:
        """Return a merged config dict of all enabled operations."""
        config = {}
        for op in self._operations:
            if op.is_enabled():
                config.update(op.get_config())
                config[f"_enabled_{op.TITLE}"] = True
        return config

    def get_enabled_ops(self) -> list[OperationWidget]:
        return [op for op in self._operations if op.is_enabled()]

    def load_all_config(self, config: dict[str, Any]) -> None:
        for op in self._operations:
            enabled_key = f"_enabled_{op.TITLE}"
            op_config = {**config, "enabled": config.get(enabled_key, False)}
            op.load_config(op_config)
