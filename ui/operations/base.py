from __future__ import annotations
from typing import Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.widgets.toggle import ToggleSwitch


class OperationWidget(QWidget):
    """
    Base class for all operation accordion items.
    Each subclass implements get_config() and load_info().
    """
    toggled = Signal(bool)        # emitted when enabled/disabled
    expanded = Signal(object)     # emitted when header clicked, passes self
    needs_file = Signal()         # emitted when toggle clicked with no file loaded

    # Subclasses override these
    TITLE: str = "Operation"
    BATCH_SUPPORTED: bool = True  # False = disabled in batch mode

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._is_open = False
        self._batch_mode = False
        self._files_loaded = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 4)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        self._header = QWidget()
        self._header.setObjectName("accordionHeader")
        self._header.setCursor(Qt.PointingHandCursor)
        self._header.setFixedHeight(46)

        h_layout = QHBoxLayout(self._header)
        h_layout.setContentsMargins(12, 0, 12, 0)
        h_layout.setSpacing(10)

        # Toggle switch
        self._toggle = ToggleSwitch()
        self._toggle.toggled.connect(self._on_toggle_changed)
        self._toggle.clicked_while_disabled.connect(self.needs_file.emit)

        # Title
        self._title_label = QLabel(self.TITLE)
        font = QFont()
        font.setWeight(QFont.Weight.Medium)
        self._title_label.setFont(font)

        # Batch badge
        self._batch_badge = QLabel("batch only")
        self._batch_badge.setObjectName("labelMuted")
        self._batch_badge.setVisible(False)
        self._batch_badge.setFont(QFont("Segoe UI", 10))

        # Chevron
        self._chevron = QLabel("›")
        self._chevron.setObjectName("labelMuted")
        self._chevron.setFixedWidth(16)
        self._chevron.setAlignment(Qt.AlignCenter)
        font2 = QFont()
        font2.setPointSize(14)
        self._chevron.setFont(font2)

        h_layout.addWidget(self._toggle)
        h_layout.addWidget(self._title_label)
        h_layout.addWidget(self._batch_badge)
        h_layout.addStretch()
        h_layout.addWidget(self._chevron)

        self._header.mousePressEvent = self._header_clicked

        # ── Body ──────────────────────────────────────────────────────────────
        self._body = QWidget()
        self._body.setObjectName("accordionBody")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(14, 12, 14, 14)
        self._body_layout.setSpacing(10)
        self._body.setVisible(False)

        # Batch mode overlay
        self._batch_overlay = QLabel(
            "Not available in batch mode.\nThis operation requires identical source dimensions."
        )
        self._batch_overlay.setObjectName("labelDanger")
        self._batch_overlay.setAlignment(Qt.AlignCenter)
        self._batch_overlay.setWordWrap(True)
        self._batch_overlay.setVisible(False)
        self._body_layout.addWidget(self._batch_overlay)

        # Content widget (subclass fills this) — disabled until toggle is on
        self._content = QWidget()
        self._content.setEnabled(False)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._body_layout.addWidget(self._content)

        root.addWidget(self._header)
        root.addWidget(self._body)

        # Let subclass populate content
        self._build_content(self._content_layout)

        # Apply initial state (no files loaded → toggle disabled)
        self._update_toggle_state()

    def _build_content(self, layout: QVBoxLayout) -> None:
        """Subclasses override this to add their widgets."""
        pass

    def _header_clicked(self, event) -> None:
        if self.is_enabled():
            return  # enabled ops stay open, can't fold by clicking
        self.expanded.emit(self)

    def _on_toggle_changed(self, enabled: bool) -> None:
        self._content.setEnabled(enabled)
        self.toggled.emit(enabled)
        self.set_open(enabled)  # expand on enable, fold on disable

    # ── Public API ────────────────────────────────────────────────────────────

    def set_open(self, open: bool) -> None:
        self._is_open = open
        self._body.setVisible(open)
        self._chevron.setText("⌄" if open else "›")
        self._header.setObjectName("accordionHeaderOpen" if open else "accordionHeader")
        self._header.style().unpolish(self._header)
        self._header.style().polish(self._header)

    def is_enabled(self) -> bool:
        return self._toggle.is_active() and self._toggle.isChecked()

    def set_active(self, active: bool) -> None:
        """Called when files are loaded (True) or cleared (False)."""
        self._files_loaded = active
        self._update_toggle_state()

    def set_batch_mode(self, batch: bool) -> None:
        self._batch_mode = batch
        not_supported = batch and not self.BATCH_SUPPORTED
        self._batch_overlay.setVisible(not_supported)
        self._content.setVisible(not not_supported)
        if not_supported:
            self._toggle.setChecked(False)
        self._update_toggle_state()

    def _update_toggle_state(self) -> None:
        batch_blocked = self._batch_mode and not self.BATCH_SUPPORTED
        can_toggle = self._files_loaded and not batch_blocked
        self._toggle.set_active(can_toggle)

    def get_config(self) -> dict[str, Any]:
        """Return operation config dict. Subclasses override."""
        return {}

    def load_config(self, config: dict[str, Any]) -> None:
        """Restore settings from a preset dict. Subclasses override."""
        pass

    def load_info(self, info) -> None:
        """Populate current-value labels from VideoInfo. Subclasses override."""
        pass
