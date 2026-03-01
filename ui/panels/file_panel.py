from __future__ import annotations
import os
from typing import Callable, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QLineEdit, QFrame, QSizePolicy, QAbstractItemView,
    QStyledItemDelegate, QStyleOptionViewItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPainter, QColor


class _DragHandleDelegate(QStyledItemDelegate):
    """Draws a 2×3 dot drag handle on the left of each list item."""

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        opt.rect = option.rect.adjusted(18, 0, 0, 0)
        super().paint(painter, opt, index)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#505050"))
        painter.setPen(Qt.NoPen)
        x0 = option.rect.left() + 7
        yc = option.rect.center().y()
        for col in range(2):
            for row in range(3):
                cx = x0 + col * 5
                cy = yc - 5 + row * 5
                painter.drawEllipse(QRectF(cx - 1.5, cy - 1.5, 3, 3))
        painter.restore()


VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv",
    ".ts", ".m4v", ".wmv", ".ogv", ".3gp", ".m2ts", ".mts",
}


class FilePanel(QWidget):
    files_changed = Signal(list)          # list[str] of paths
    output_dir_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(10)

        # ── Title ──────────────────────────────────────────────────────────────
        title = QLabel("INPUT FILES")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # ── File list ─────────────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._list.setDragDropMode(QAbstractItemView.InternalMove)
        self._list.setDefaultDropAction(Qt.MoveAction)
        self._list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._list.setToolTip("Drag & drop video files here")
        self._list.setItemDelegate(_DragHandleDelegate(self._list))
        layout.addWidget(self._list)

        # Add / Remove buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._btn_add = QPushButton("+ Add Files")
        self._btn_add.setObjectName("btnSmall")
        self._btn_add.clicked.connect(self._browse_files)

        self._btn_remove = QPushButton("Remove")
        self._btn_remove.setObjectName("btnSmall")
        self._btn_remove.clicked.connect(self._remove_selected)
        self._btn_remove.setEnabled(False)

        self._btn_clear = QPushButton("Clear All")
        self._btn_clear.setObjectName("btnGhost")
        self._btn_clear.clicked.connect(self._clear_all)

        btn_row.addWidget(self._btn_add)
        btn_row.addWidget(self._btn_remove)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_clear)
        layout.addLayout(btn_row)

        self._list.itemSelectionChanged.connect(
            lambda: self._btn_remove.setEnabled(bool(self._list.selectedItems()))
        )
        self._list.model().rowsMoved.connect(
            lambda: self.files_changed.emit(self.get_files())
        )

        # ── Separator ─────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # ── Output folder ─────────────────────────────────────────────────────
        out_title = QLabel("OUTPUT FOLDER")
        out_title.setObjectName("sectionTitle")
        layout.addWidget(out_title)

        self._output_field = QLineEdit()
        self._output_field.setPlaceholderText("Select output folder…")
        self._output_field.setObjectName("outputField")
        self._output_field.setReadOnly(True)
        layout.addWidget(self._output_field)

        self._btn_output = QPushButton("Browse folder…")
        self._btn_output.setObjectName("btnBrowse")
        self._btn_output.clicked.connect(self._browse_output)
        layout.addWidget(self._btn_output)

    # ── File management ──────────────────────────────────────────────────────

    def _add_paths(self, paths: list[str]) -> None:
        existing = self.get_files()
        added = False
        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in VIDEO_EXTENSIONS and path not in existing:
                item = QListWidgetItem(os.path.basename(path))
                item.setData(Qt.UserRole, path)
                item.setToolTip(path)
                self._list.addItem(item)
                added = True
        if added:
            self.files_changed.emit(self.get_files())

    def _browse_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.ts *.m4v *.wmv *.ogv *.3gp *.m2ts *.mts);;All Files (*)",
        )
        if paths:
            self._add_paths(paths)

    def _remove_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))
        self.files_changed.emit(self.get_files())

    def _clear_all(self) -> None:
        self._list.clear()
        self.files_changed.emit([])

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder:
            self._output_field.setText(folder)
            self._output_field.setObjectName("outputField")
            self._output_field.style().unpolish(self._output_field)
            self._output_field.style().polish(self._output_field)
            self.output_dir_changed.emit(folder)

    # ── Drag & drop ──────────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        self._add_paths(paths)

    # ── Public API ───────────────────────────────────────────────────────────

    def get_files(self) -> list[str]:
        return [
            self._list.item(i).data(Qt.UserRole)
            for i in range(self._list.count())
        ]

    def get_output_dir(self) -> str:
        return self._output_field.text().strip()

    def mark_output_required(self) -> None:
        """Visually highlight the output field as required."""
        self._output_field.setObjectName("errorField")
        self._output_field.style().unpolish(self._output_field)
        self._output_field.style().polish(self._output_field)
        self._output_field.setPlaceholderText("⚠ Output folder is required")

    def flash_required(self) -> None:
        """Briefly flash the file list with a red border to prompt file selection."""
        self._list.setStyleSheet(
            "QListWidget { border: 2px solid #f45b5b; border-radius: 8px; }"
        )
        self._btn_add.setStyleSheet("QPushButton { border-color: #f45b5b; color: #f45b5b; }")
        QTimer.singleShot(1200, self._clear_flash)

    def _clear_flash(self) -> None:
        self._list.setStyleSheet("")
        self._btn_add.setStyleSheet("")
