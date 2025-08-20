from .imports import *
from .initFuncs import initFuncs
# -----------------------------------------------------------------------------
#  main application ------------------------------------------------------------
# -----------------------------------------------------------------------------


class WindowManagerApp(QMainWindow):
    COLS = ["Window ID", "Title", "PID", "Monitor", "Type"]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Window Manager")
        self.resize(980, 640)
        self.monitors: List[Tuple[str, int, int, int, int]] = []
        self.windows: List[Tuple[str, str, str, str, str]] = []  # incl. type
        self._build_ui()
        self.refresh()

WindowManagerApp = initFuncs(WindowManagerApp)
