from __future__ import annotations
import os
import sys


def _base_dir() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ffmpeg_path() -> str:
    return os.path.join(_base_dir(), "bin", "ffmpeg.exe")


def ffprobe_path() -> str:
    return os.path.join(_base_dir(), "bin", "ffprobe.exe")
