<h1><img src="Git_medias/icon.png" width="40" align="absmiddle"/> Simple Video Tools</h1>

A free, simple desktop video editor. No subscriptions, no cloud, no special software needed.

Built with Python + PySide6 + ffmpeg.

## Download

| Version | Link |
|---------|------|
| Portable `.exe` | [Download](https://drive.google.com/file/d/1xEKaE4Q4jv0NhOcTZ0BzS3sK-dzEUpwj/view?usp=sharing) |
| Installer | Coming soon |

If you find it useful, a ⭐ star or a coffee would mean a lot!

<a href="https://www.buymeacoffee.com/tyombo"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" height="40"/></a>

---

## Screenshot

![Screenshot](Git_medias/Interface.png)

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
- Dark theme

---

---

## For Developers (running from source)

### Requirements

- Python 3.10+
- ffmpeg & ffprobe binaries (see Setup)

### Setup

**1. Clone the repo**
```
git clone <repo-url>
cd Simple_Video_Tool
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
- Presets are stored in `%APPDATA%\SimpleVideoTools\presets.json`
