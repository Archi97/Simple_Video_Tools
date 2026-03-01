from __future__ import annotations
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, Callable

from core.ffmpeg_bin import ffmpeg_path

_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


@dataclass
class ProcessingTask:
    input_path: str
    output_path: str
    # Operations — None means disabled
    trim_start: Optional[float] = None       # seconds
    trim_end: Optional[float] = None         # seconds
    crop: Optional[tuple[int, int, int, int]] = None  # (x, y, w, h)
    fps: Optional[float] = None
    video_bitrate: Optional[int] = None      # bits/s
    output_format: Optional[str] = None      # container format name, e.g. "mp4"
    output_extension: Optional[str] = None   # file extension
    extract_audio_format: Optional[str] = None  # "mp3", "aac", etc.
    mute: bool = False
    resolution: Optional[tuple[int, int]] = None  # (width, height)
    speed: Optional[float] = None            # 1.0 = no change


def _atempo_chain(speed: float) -> list[str]:
    """Build atempo filter chain — atempo range is [0.5, 2.0]."""
    filters: list[str] = []
    s = speed
    while s > 2.0:
        filters.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        filters.append("atempo=0.5")
        s *= 2.0
    filters.append(f"atempo={s:.6f}")
    return filters


def _parse_time(s: str) -> float:
    """Parse HH:MM:SS.ms string to seconds."""
    m = re.match(r"(\d+):(\d+):(\d+\.?\d*)", s)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 0.0


def _run(
    cmd: list[str],
    total_duration: float,
    progress_cb: Optional[Callable[[int, str], None]],
    progress_msg: str = "Processing…",
) -> None:
    """Run an ffmpeg command, parsing stderr for progress."""
    proc = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        creationflags=_CREATE_NO_WINDOW,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )

    total = total_duration
    stderr_lines: list[str] = []

    for line in proc.stderr:  # type: ignore[union-attr]
        stderr_lines.append(line)

        # Pick up duration from ffmpeg header if not supplied
        if total <= 0:
            dm = re.search(r"Duration:\s*(\d+:\d+:\d+\.?\d*)", line)
            if dm:
                total = _parse_time(dm.group(1))

        # Progress
        if progress_cb:
            tm = re.search(r"time=(\d+:\d+:\d+\.?\d*)", line)
            if tm and total > 0:
                pct = min(98, int(_parse_time(tm.group(1)) / total * 98))
                progress_cb(pct, f"{progress_msg} {pct}%")

    proc.wait()
    if proc.returncode != 0:
        tail = "".join(stderr_lines[-10:]).strip()
        raise RuntimeError(f"ffmpeg error:\n{tail}")


def process_video(
    task: ProcessingTask,
    progress_cb: Optional[Callable[[int, str], None]] = None,
) -> None:
    def report(pct: int, msg: str = "") -> None:
        if progress_cb:
            progress_cb(pct, msg)

    report(0, "Building command…")

    cmd: list[str] = [ffmpeg_path(), "-y"]

    cmd += ["-i", task.input_path]

    # ── Trim (output options = frame-accurate, correct duration) ──────────────
    if task.trim_start and task.trim_start > 0:
        cmd += ["-ss", f"{task.trim_start:.6f}"]
    if task.trim_end is not None:
        cmd += ["-to", f"{task.trim_end:.6f}"]

    # ── Filter chains ─────────────────────────────────────────────────────────
    vf: list[str] = []
    af: list[str] = []

    if task.crop:
        x, y, w, h = task.crop
        vf.append(f"crop={w}:{h}:{x}:{y}")

    if task.resolution:
        w, h = task.resolution
        vf.append(f"scale={w}:{h}")

    if task.fps:
        vf.append(f"fps={task.fps}")

    if task.speed and task.speed != 1.0:
        vf.append(f"setpts={1.0 / task.speed:.6f}*PTS")
        if not task.mute:
            af.extend(_atempo_chain(task.speed))

    needs_video_transcode = bool(vf or task.video_bitrate)
    needs_audio_transcode = bool(af)

    # ── Extract audio only ────────────────────────────────────────────────────
    if task.extract_audio_format:
        cmd += ["-vn"]
        codec_map = {
            "mp3": "libmp3lame", "aac": "aac", "wav": "pcm_s16le",
            "flac": "flac", "ogg": "libvorbis",
        }
        cmd += ["-c:a", codec_map.get(task.extract_audio_format.lower(), "aac")]

    else:
        # ── Video ─────────────────────────────────────────────────────────────
        if vf:
            cmd += ["-vf", ",".join(vf)]

        if needs_video_transcode:
            cmd += ["-c:v", "libx264", "-preset", "fast", "-bf", "0"]
            if task.video_bitrate:
                cmd += ["-b:v", str(task.video_bitrate)]
            else:
                cmd += ["-crf", "18"]
        else:
            cmd += ["-c:v", "copy"]

        # ── Audio ─────────────────────────────────────────────────────────────
        if task.mute:
            cmd += ["-an"]
        else:
            if af:
                cmd += ["-af", ",".join(af)]
            cmd += ["-c:a", "aac" if needs_audio_transcode else "copy"]

    # ── Output format ─────────────────────────────────────────────────────────
    if task.output_format:
        cmd += ["-f", task.output_format]

    cmd.append(task.output_path)

    # ── Total duration for progress ───────────────────────────────────────────
    if task.trim_end is not None:
        total = task.trim_end - (task.trim_start or 0.0)
    else:
        total = 0.0  # parsed from ffmpeg header

    report(2, "Processing…")
    _run(cmd, total, progress_cb, "Processing…")
    report(100, "Done.")


def extract_audio(
    input_path: str,
    output_path: str,
    progress_cb: Optional[Callable[[int, str], None]] = None,
) -> None:
    ext = os.path.splitext(output_path)[1].lstrip(".").lower()
    codec_map = {
        "mp3": "libmp3lame", "aac": "aac", "wav": "pcm_s16le",
        "flac": "flac", "ogg": "libvorbis",
    }
    cmd = [
        ffmpeg_path(), "-y",
        "-i", input_path,
        "-vn",
        "-c:a", codec_map.get(ext, "aac"),
        output_path,
    ]
    if progress_cb:
        progress_cb(0, "Extracting audio…")
    _run(cmd, 0.0, progress_cb, "Extracting audio…")
    if progress_cb:
        progress_cb(100, "Done.")
