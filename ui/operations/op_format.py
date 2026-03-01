from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from .base import OperationWidget

FORMATS = [
    ("MP4",  "mp4",     "mp4"),
    ("MKV",  "matroska","mkv"),
    ("AVI",  "avi",     "avi"),
    ("MOV",  "mov",     "mov"),
    ("FLV",  "flv",     "flv"),
    ("TS",   "mpegts",  "ts"),
    ("M4V",  "mp4",     "m4v"),
    ("WMV",  "asf",     "wmv"),
    ("3GP",  "3gp",     "3gp"),
    # TODO: WebM (webm/webm) and OGV (ogg/ogv) require VP8/VP9 + Vorbis — incompatible with libx264/aac.
    # To add: detect these formats → force needs_transcode=True → use libvpx + libvorbis.
    # VP8 options: out_video.options = {"b": "1500k", "crf": "10", "deadline": "realtime", "cpu-used": "4"}
    # GIF also needs special handling: codec="gif", pix_fmt="rgb8", no audio stream.
]


class FormatOperation(OperationWidget):
    TITLE = "Change Format"
    BATCH_SUPPORTED = True

    def _build_content(self, layout: QVBoxLayout) -> None:
        self._current_label = QLabel("Current format: —")
        self._current_label.setObjectName("labelMuted")
        layout.addWidget(self._current_label)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(QLabel("Convert to"))
        self._combo = QComboBox()
        for label, fmt, ext in FORMATS:
            self._combo.addItem(label, (fmt, ext))
        row.addWidget(self._combo)
        row.addStretch()
        layout.addLayout(row)

    def set_batch_mode(self, batch: bool) -> None:
        super().set_batch_mode(batch)
        self._current_label.setVisible(not batch)

    def load_info(self, info) -> None:
        self._current_label.setText(f"Current format: {info.format_name.upper()}")
        # Pre-select a different format from current
        for i, (label, fmt, ext) in enumerate(FORMATS):
            if ext != info.format_name and fmt != info.format_name:
                self._combo.setCurrentIndex(i)
                break

    def get_config(self) -> dict[str, Any]:
        fmt, ext = self._combo.currentData()
        return {"output_format": fmt, "output_extension": ext}

    def load_config(self, config: dict[str, Any]) -> None:
        if "output_extension" in config:
            for i in range(self._combo.count()):
                _, ext = self._combo.itemData(i)
                if ext == config["output_extension"]:
                    self._combo.setCurrentIndex(i)
                    break
        self._toggle.setChecked(config.get("enabled", False))
