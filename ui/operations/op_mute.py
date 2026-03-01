from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QLabel
from .base import OperationWidget


class MuteOperation(OperationWidget):
    TITLE = "Mute Audio"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        note = QLabel("Removes the audio track from the video entirely.")
        note.setObjectName("labelMuted")
        note.setWordWrap(True)
        layout.addWidget(note)

    def get_config(self) -> dict[str, Any]:
        return {"mute": True}

    def load_config(self, config: dict[str, Any]) -> None:
        self._toggle.setChecked(config.get("enabled", False))
