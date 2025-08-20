from PyQt6.QtWidgets import QApplication
import traceback,sys
def startFinderConsole(console):
    try:
        app = QApplication(sys.argv)
        win = console()
        win.show()
        sys.exit(app.exec())
    except Exception:
        print(traceback.format_exc())
