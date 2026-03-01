from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from .base import OperationWidget

AUDIO_FORMATS = ["mp3", "aac", "wav", "flac", "ogg"]


class ExtractAudioOperation(OperationWidget):
    TITLE = "Extract Audio"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._codec_label = QLabel("Audio codec: —")
        self._codec_label.setObjectName("labelMuted")
        layout.addWidget(self._codec_label)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(QLabel("Output format"))
        self._combo = QComboBox()
        for fmt in AUDIO_FORMATS:
            self._combo.addItem(fmt.upper(), fmt)
        row.addWidget(self._combo)
        row.addStretch()
        layout.addLayout(row)

        note = QLabel(
            "Audio is extracted from the original source file, "
            "not the trimmed or processed output."
        )
        note.setObjectName("labelMuted")
        note.setWordWrap(True)
        layout.addWidget(note)

    def load_info(self, info) -> None:
        codec = info.audio_codec or "none"
        self._codec_label.setText(f"Audio codec: {codec}")

    def get_config(self) -> dict[str, Any]:
        return {"extract_audio_format": self._combo.currentData()}

    def load_config(self, config: dict[str, Any]) -> None:
        if "extract_audio_format" in config:
            idx = self._combo.findData(config["extract_audio_format"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._toggle.setChecked(config.get("enabled", False))
