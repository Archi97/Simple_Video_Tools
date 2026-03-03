# Video Editor

A free, simple desktop video editor. No subscriptions, no cloud, no special software needed.

Built with Python + PySide6 + ffmpeg.

---

## Features

- Trim
- Crop
- Change Resolution
- Change FPS `+batch`
- Change Bitrate `+batch`
- Change Speed `+batch`
- Change Format / Convert `+batch`
- Volume (0 = mute, up to 3× amplify) `+batch`
- Extract Audio `+batch`
- Split (horizontal / vertical) `+batch`
- Merge with Audio

- Drag-and-drop file reordering
- Save / load operation presets
- Batch mode — process multiple files at once
- Dark theme with custom title bar

---

## Requirements

- Python 3.10+
- ffmpeg & ffprobe binaries (see Setup)

---

## Setup

**1. Clone the repo**
```
git clone <repo-url>
cd Simple_video_tool
```

**2. Add ffmpeg binaries**

Download a static ffmpeg build from https://ffmpeg.org/download.html
and place the binaries in the `bin/` folder:
```
bin/
  ffmpeg.exe
  ffprobe.exe
```

**3. Create a virtual environment and install dependencies**
```
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**4. Run**
```
venv\Scripts\python.exe main.py
```

---

## Building

See `BUILD.md` for instructions on building a portable `.exe` or a Windows installer.

---

## Notes

- Windows only for now
- Output files are saved to a folder you choose
- Presets are stored in `%APPDATA%\VideoEditor\presets.json`
