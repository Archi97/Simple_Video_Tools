import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow


def _base_dir() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def load_stylesheet(app: QApplication) -> None:
    qss_path = os.path.join(_base_dir(), "styles", "dark.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def _set_app_user_model_id() -> None:
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SimpleVideoTools.App")
    except Exception:
        pass


def main() -> None:
    _set_app_user_model_id()
    # Enable HiDPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Simple Video Tools")
    app.setOrganizationName("SimpleVideoTools")

    icon_path = os.path.join(_base_dir(), "icon.ico")
    icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    app.setWindowIcon(icon)

    load_stylesheet(app)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    # Force taskbar icon via Win32 API (Qt alone is not enough on Windows)
    if os.path.exists(icon_path):
        try:
            hwnd = int(window.winId())
            WM_SETICON = 0x0080
            hicon_big = ctypes.windll.user32.LoadImageW(
                None, icon_path, 1, 0, 0, 0x0010 | 0x0040
            )
            if hicon_big:
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_big)
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_big)
        except Exception:
            pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
