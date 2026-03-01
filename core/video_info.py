from __future__ import annotations
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

from core.ffmpeg_bin import ffprobe_path

_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


@dataclass
class VideoInfo:
    path: str
    duration: float          # seconds
    fps: float
    width: int
    height: int
    video_codec: str
    audio_codec: Optional[str]
    video_bitrate: int       # bits/s
    audio_bitrate: Optional[int]
    format_name: str
    file_size: int           # bytes

    @property
    def resolution_label(self) -> str:
        h = self.height
        labels = {2160: "4K", 1440: "2K", 1080: "1080p", 720: "720p", 480: "480p", 360: "360p"}
        return labels.get(h, f"{self.width}×{self.height}")

    @property
    def duration_str(self) -> str:
        total = int(self.duration)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @property
    def video_bitrate_kbps(self) -> int:
        return self.video_bitrate // 1000

    @property
    def file_size_mb(self) -> float:
        return self.file_size / (1024 * 1024)


def _pick_format_name(path: str, format_name: str) -> str:
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    names = format_name.split(",")
    return ext if ext in names else names[0]


def _parse_rate(rate_str: str) -> float:
    try:
        num, den = rate_str.split("/")
        d = int(den)
        return int(num) / d if d else 0.0
    except Exception:
        return 0.0


def get_video_info(path: str) -> VideoInfo:
    cmd = [
        ffprobe_path(),
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        path,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        creationflags=_CREATE_NO_WINDOW,
    )
    if result.returncode != 0:
        raise ValueError(f"ffprobe failed: {result.stderr.strip()}")

    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    fmt = data.get("format", {})

    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if not video:
        raise ValueError(f"No video stream found in: {path}")

    duration = float(fmt.get("duration") or video.get("duration") or 0)

    fps = 0.0
    for key in ("avg_frame_rate", "r_frame_rate"):
        val = video.get(key, "0/1")
        if val and val != "0/0":
            fps = _parse_rate(val)
            if fps > 0:
                break

    video_bitrate = int(video.get("bit_rate") or 0)
    if not video_bitrate:
        video_bitrate = int(fmt.get("bit_rate") or 0)

    audio_codec = audio["codec_name"] if audio else None
    audio_bitrate = int(audio.get("bit_rate") or 0) if audio else None

    return VideoInfo(
        path=path,
        duration=duration,
        fps=round(fps, 3),
        width=int(video["width"]),
        height=int(video["height"]),
        video_codec=video["codec_name"],
        audio_codec=audio_codec,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        format_name=_pick_format_name(path, fmt.get("format_name", "")),
        file_size=os.path.getsize(path),
    )
