from .main import windowManagerConsole
from .imports import QApplication,sys
def startWindowManagerConsole():
    app = QApplication(sys.argv)
    win = windowManagerConsole()
    win.show()
    sys.exit(app.exec())
