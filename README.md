# Video Editor

A simple desktop video editor built with Python and PySide6.

## Features

- Trim, Crop, Change Resolution
- Change FPS, Bitrate, Speed
- Change output format, Extract audio, Mute
- Presets — save and load operation configs
- Batch mode — process multiple files at once

## Requirements

- Python 3.10+
- ffmpeg & ffprobe binaries

## Setup

**1. Clone the repo**
```
git clone <repo-url>
cd video-editor
```

**2. Add ffmpeg binaries**

Download a static ffmpeg build from https://ffmpeg.org/download.html and place the binaries in the `bin/` folder:
```
bin/
  ffmpeg.exe
  ffprobe.exe
```

**3. Create a virtual environment and install dependencies**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**4. Run**
```
venv\Scripts\python main.py
```

## Notes

- Windows only for now (macOS/Linux support planned)
- Output files are saved as `<original_name>_edited.<ext>` in a folder you choose
