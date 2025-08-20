from .main import WindowManagerApp
from .imports import QApplication,sys
def start_window_info_gui():
    app = QApplication(sys.argv)
    win = WindowManagerApp()
    win.show()
    sys.exit(app.exec())
