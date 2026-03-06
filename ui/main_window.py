from __future__ import annotations
import os
import traceback
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSizePolicy, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont

from version import VERSION
from core.video_info import get_video_info, VideoInfo
from core.processor import process_video, extract_audio, split_video, ProcessingTask
from ui.panels.file_panel import FilePanel
from ui.panels.operations_panel import OperationsPanel
from ui.widgets.progress_widget import ProgressWidget


# ── Worker ────────────────────────────────────────────────────────────────────

class Worker(QObject):
    progress = Signal(int, str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, tasks: list[tuple]):
        super().__init__()
        self._tasks = tasks   # list of (callable, args)
        self._stopped = False

    def run(self) -> None:
        try:
            for i, (fn, args, kwargs) in enumerate(self._tasks):
                if self._stopped:
                    break
                fn(*args, **kwargs)
            self.finished.emit()
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))

    def stop(self) -> None:
        self._stopped = True


# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Simple Video Tools v{VERSION}")
        self.setMinimumSize(1000, 640)
        self.resize(1200, 720)
        self._video_info: Optional[VideoInfo] = None
        self._worker: Optional[Worker] = None
        self._thread: Optional[QThread] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QWidget()
        root.setObjectName("rootWidget")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Main content area (left + right) ──────────────────────────────────
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left panel
        self._file_panel = FilePanel()
        self._file_panel.setFixedWidth(280)
        self._file_panel.files_changed.connect(self._on_files_changed)
        self._file_panel.output_dir_changed.connect(lambda _: None)
        content_layout.addWidget(self._file_panel)

        # Right panel + run button
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._ops_panel = OperationsPanel()
        self._ops_panel.needs_file.connect(self._file_panel.flash_required)
        self._ops_panel.config_changed.connect(self._update_run_btn)
        right_layout.addWidget(self._ops_panel, stretch=1)

        # Run row
        run_row = QWidget()
        run_row.setObjectName("bottomBar")
        run_row_layout = QHBoxLayout(run_row)
        run_row_layout.setContentsMargins(16, 10, 16, 10)
        run_row_layout.setSpacing(12)

        self._no_files_label = QLabel("Add video files to get started.")
        self._no_files_label.setObjectName("labelMuted")
        run_row_layout.addWidget(self._no_files_label)
        run_row_layout.addStretch()

        self._btn_run = QPushButton("RUN")
        self._btn_run.setObjectName("btnPrimary")
        self._btn_run.setFixedWidth(140)
        self._btn_run.clicked.connect(self._on_run)
        self._btn_run.setEnabled(False)
        run_row_layout.addWidget(self._btn_run)

        right_layout.addWidget(run_row)
        content_layout.addWidget(right_container, stretch=1)

        outer.addWidget(content, stretch=1)

        # ── Progress bar ──────────────────────────────────────────────────────
        self._progress = ProgressWidget()
        outer.addWidget(self._progress)

    # ── File change handling ──────────────────────────────────────────────────

    def _update_run_btn(self) -> None:
        has_files = bool(self._file_panel.get_files())
        has_ops = bool(self._ops_panel.get_enabled_ops())
        self._btn_run.setEnabled(has_files and has_ops)

    def _on_files_changed(self, paths: list[str]) -> None:
        has_files = bool(paths)
        self._no_files_label.setVisible(not has_files)
        self._update_run_btn()

        self._ops_panel.set_active(has_files)

        batch = len(paths) > 1
        self._ops_panel.set_batch_mode(batch)

        # Load info from first file
        if paths:
            try:
                info = get_video_info(paths[0])
                self._video_info = info
                self._ops_panel.load_video_info(info)
            except Exception as e:
                self._progress.set_progress(0, f"Could not read file: {e}")

    # ── Run ───────────────────────────────────────────────────────────────────

    def _on_run(self) -> None:
        files = self._file_panel.get_files()
        output_dir = self._file_panel.get_output_dir()

        if not files:
            return

        if not output_dir or not os.path.isdir(output_dir):
            self._file_panel.mark_output_required()
            self._progress.set_progress(0, "Please select an output folder first.")
            return

        config = self._ops_panel.get_all_config()
        self._btn_run.setEnabled(False)
        self._progress.set_progress(0, "Starting…")
        self._start_worker(files, output_dir, config)

    def _build_tasks(self, files: list[str], output_dir: str, config: dict) -> list:
        """Build a flat list of (callable, args, kwargs) for the worker."""
        tasks = []
        total = len(files)

        extract_fmt = config.get("extract_audio_format") if config.get("_enabled_Extract Audio") else None
        has_video_ops = any(
            config.get(f"_enabled_{title}")
            for title in ["Trim", "Crop", "Change FPS", "Change Bitrate",
                          "Change Format", "Volume", "Change Resolution", "Speed Change",
                          "Merge with Audio"]
        )
        _split_on = config.get("_enabled_Split", False)
        split_x = config.get("split_x") if _split_on else None
        split_y = config.get("split_y") if _split_on else None
        split_x_half = bool(config.get("split_x_half")) if _split_on else False
        split_y_half = bool(config.get("split_y_half")) if _split_on else False
        split_enabled = split_x_half or split_y_half or bool(split_x or split_y)

        for idx, path in enumerate(files):
            base = os.path.splitext(os.path.basename(path))[0]

            # Determine output extension
            if config.get("_enabled_Change Format") and config.get("output_extension"):
                ext = config["output_extension"]
            else:
                ext = os.path.splitext(path)[1].lstrip(".")

            file_label = f"[{idx + 1}/{total}] {os.path.basename(path)}"

            if has_video_ops:
                # When split: process to temp, split, delete temp
                # Otherwise: process directly to final output
                if split_enabled:
                    video_out = os.path.join(output_dir, f"{base}__split_tmp.{ext}")
                else:
                    video_out = os.path.join(output_dir, f"{base}_edited.{ext}")

                task = ProcessingTask(
                    input_path=path,
                    output_path=video_out,
                    trim_start=config.get("trim_start") if config.get("_enabled_Trim") else None,
                    trim_end=config.get("trim_end") if config.get("_enabled_Trim") else None,
                    crop=config.get("crop") if config.get("_enabled_Crop") else None,
                    fps=config.get("fps") if config.get("_enabled_Change FPS") else None,
                    video_bitrate=config.get("video_bitrate") if config.get("_enabled_Change Bitrate") else None,
                    output_format=config.get("output_format") if config.get("_enabled_Change Format") else None,
                    output_extension=config.get("output_extension") if config.get("_enabled_Change Format") else None,
                    volume=config.get("volume") if config.get("_enabled_Volume") else None,
                    resolution=config.get("resolution") if config.get("_enabled_Change Resolution") else None,
                    speed=config.get("speed") if config.get("_enabled_Speed Change") else None,
                    merge_audio=config.get("merge_audio_path") if config.get("_enabled_Merge with Audio") else None,
                )
                tasks.append((
                    process_video,
                    [task],
                    {"progress_cb": lambda pct, msg, lbl=file_label: self._worker.progress.emit(pct, f"{lbl} — {msg}")},
                ))

                if split_enabled:
                    tmp = video_out
                    tasks.append((
                        split_video,
                        [tmp, output_dir, base, ext, split_x, split_y],
                        {"half_x": split_x_half, "half_y": split_y_half,
                         "progress_cb": lambda pct, msg, lbl=file_label: self._worker.progress.emit(pct, f"{lbl} (split) — {msg}")},
                    ))
                    tasks.append((os.remove, [tmp], {}))

            elif split_enabled:
                tasks.append((
                    split_video,
                    [path, output_dir, base, ext, split_x, split_y],
                    {"half_x": split_x_half, "half_y": split_y_half,
                     "progress_cb": lambda pct, msg, lbl=file_label: self._worker.progress.emit(pct, f"{lbl} (split) — {msg}")},
                ))

            if extract_fmt:
                audio_out = os.path.join(output_dir, f"{base}_audio.{extract_fmt}")
                tasks.append((
                    extract_audio,
                    [path, audio_out],
                    {"progress_cb": lambda pct, msg, lbl=file_label: self._worker.progress.emit(pct, f"{lbl} (audio) — {msg}")},
                ))

        return tasks

    def _start_worker(self, files: list, output_dir: str, config: dict) -> None:
        self._thread = QThread()
        self._worker = Worker([])
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        tasks = self._build_tasks(files, output_dir, config)
        if not tasks:
            self._btn_run.setEnabled(True)
            self._progress.set_progress(0, "")
            return
        self._worker._tasks = tasks
        self._thread.start()

    def _on_progress(self, pct: int, msg: str) -> None:
        self._progress.set_progress(pct, msg)

    def _on_finished(self) -> None:
        self._progress.set_progress(100, "All done!")
        self._btn_run.setEnabled(True)
        self._cleanup_thread()

    def _on_error(self, message: str) -> None:
        self._progress.set_progress(0, f"Error: {message}")
        self._btn_run.setEnabled(True)
        QMessageBox.critical(self, "Processing Error", message)
        self._cleanup_thread()

    def _cleanup_thread(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
            self._worker = None
