from __future__ import annotations
import json
import os
import platform
from typing import Any


def _presets_path() -> str:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    folder = os.path.join(base, "VideoEditor")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "presets.json")


def load_presets() -> dict[str, Any]:
    path = _presets_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_preset(name: str, config: dict[str, Any]) -> None:
    presets = load_presets()
    presets[name] = config
    with open(_presets_path(), "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2)


def delete_preset(name: str) -> None:
    presets = load_presets()
    presets.pop(name, None)
    with open(_presets_path(), "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2)
