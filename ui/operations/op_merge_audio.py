from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt
from .base import OperationWidget


class MergeAudioOperation(OperationWidget):
    TITLE = "Merge with Audio"
    BATCH_SUPPORTED = False

    def _build_content(self, layout: QVBoxLayout) -> None:
        note = QLabel("Replaces the video's audio with the selected file.\nVideo audio is discarded automatically.")
        note.setObjectName("labelMuted")
        note.setWordWrap(True)
        layout.addWidget(note)

        row = QHBoxLayout()
        row.setSpacing(8)

        btn = QPushButton("Browse…")
        btn.setObjectName("btnSmall")
        btn.setFixedWidth(72)
        btn.clicked.connect(self._browse)
        row.addWidget(btn)

        self._path_label = QLabel("No file selected")
        self._path_label.setObjectName("labelMuted")
        self._path_label.setWordWrap(False)
        self._path_label.setMinimumWidth(0)
        row.addWidget(self._path_label, stretch=1)

        layout.addLayout(row)
        self._audio_path: str = ""

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "",
            "Audio Files (*.mp3 *.aac *.wav *.flac *.ogg *.m4a);;All Files (*)"
        )
        if path:
            self._audio_path = path
            import os
            self._path_label.setText(os.path.basename(path))
            self._path_label.setObjectName("")
            self._path_label.style().unpolish(self._path_label)
            self._path_label.style().polish(self._path_label)

    def get_config(self) -> dict[str, Any]:
        return {"merge_audio_path": self._audio_path}

    def load_config(self, config: dict[str, Any]) -> None:
        path = config.get("merge_audio_path", "")
        if path:
            self._audio_path = path
            import os
            self._path_label.setText(os.path.basename(path))
        self._toggle.setChecked(config.get("enabled", False))
