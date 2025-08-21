from PyQt6.QtWidgets import QApplication,QTextEdit
from PyQt6 import QtWidgets, QtGui, QtCore, QtGui, QtWidgets
from pathlib import Path
import traceback, sys, logging, os
from logging.handlers import RotatingFileHandler
logger = logging
import threading

# Setup robust logging
LOG_DIR = os.path.join(os.path.expanduser("~"), ".cache", "abstract_finder")
LOG_FILE = os.path.join(LOG_DIR, "finder.log")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# robustLogger/logHandler.py
from abstract_gui.QT6 import *
import logging, os

class QtLogEmitter(QObject):
    new_log = pyqtSignal(str)

class QtLogHandler(logging.Handler):
    def __init__(self, emitter: QtLogEmitter):
        super().__init__()
        self.emitter = emitter
    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.emitter.new_log.emit(msg + "\n")

class CompactFormatter(logging.Formatter):
    def format(self, record):
        return f"{self.formatTime(record)} [{record.levelname}] {record.getMessage()}"

# ---- singletons ----
_emitter: QtLogEmitter | None = None
_handler: QtLogHandler | None = None

def get_log_emitter() -> QtLogEmitter:
    global _emitter
    if _emitter is None:
        _emitter = QtLogEmitter()
    return _emitter

def ensure_qt_log_handler_attached() -> QtLogHandler:
    """Attach one QtLogHandler to the root logger (idempotent)."""
    global _handler
    if _handler is None:
        _handler = QtLogHandler(get_log_emitter())
        _handler.setLevel(logging.DEBUG)
        _handler.setFormatter(CompactFormatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(_handler)
    return _handler
def set_self_log(self):
    self.log = QTextEdit()
    self.log.setReadOnly(True)
    self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap,)
def logoutput():
    self.filter_row = QHBoxLayout()
    self.filter_row.addWidget(QLabel("Log Output:")); filter_row.addStretch(1)
    self.filter_row.addWidget(self.rb_all); filter_row.addWidget(self.rb_err); filter_row.addWidget(self.rb_wrn)
    self.filter_row.addWidget(self.cb_try_alt_ext)
    layout.addLayout(self.filter_row)

def setup_logging():
    # File: rotating, safe for long sessions
    f = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    f.setLevel(logging.DEBUG)
    f.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    ))
    logger.addHandler(f)

    # Console (stderr) for dev runs
    c = logging.StreamHandler(sys.stderr)
    c.setLevel(logging.INFO)
    c.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(c)

setup_logging()

# Crash handlers
def _format_exc(exctype, value, tb):
    return "".join(traceback.format_exception(exctype, value, tb))

def excepthook(exctype, value, tb):
    msg = _format_exc(exctype, value, tb)
    logger.critical("UNCAUGHT EXCEPTION:\n%s", msg)

sys.excepthook = excepthook

def threading_excepthook(args):
    msg = _format_exc(args.exc_type, args.exc_value, args.exc_traceback)
    logger.critical("THREAD EXCEPTION:\n%s", msg)

threading.excepthook = threading_excepthook

# Qt message handler
def qt_message_handler(mode, ctx, message):
    level = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }.get(mode, logging.INFO)
    logger.log(level, "Qt: %s (%s:%d)", message, ctx.file or "unknown", ctx.line or 0)

QtCore.qInstallMessageHandler(qt_message_handler)

# Log file path access
def get_log_file_path():
    return LOG_FILE

# Live log display in QTextEdit
class QtLogEmitter(QtCore.QObject):
    new_log = QtCore.pyqtSignal(str)

class QtLogHandler(logging.Handler):
    def __init__(self, emitter: QtLogEmitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.emitter.new_log.emit(msg + "\n")

class CompactFormatter(logging.Formatter):
    def format(self, record):
        return f"{self.formatTime(record)} [{record.levelname}] {record.getMessage()}"

_emitter = None
_handler = None

def get_log_emitter() -> QtLogEmitter:
    global _emitter
    if _emitter is None:
        _emitter = QtLogEmitter()
    return _emitter

def ensure_qt_log_handler_attached() -> QtLogHandler:
    global _handler
    if _handler is None:
        _handler = QtLogHandler(get_log_emitter())
        _handler.setLevel(logging.DEBUG)
        _handler.setFormatter(CompactFormatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(_handler)
    return _handler

def attach_textedit_to_logs(textedit: QTextEdit, tail_file: str | None = None):
    ensure_qt_log_handler_attached()
    emitter = get_log_emitter()
    emitter.new_log.connect(textedit.append)

    if tail_file:
        textedit._tail_pos = 0
        timer = QTimer(textedit)
        timer.setInterval(500)
        def _poll():
            try:
                with open(tail_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(getattr(textedit, "_tail_pos", 0))
                    chunk = f.read()
                    textedit._tail_pos = f.tell()
                    if chunk:
                        textedit.moveCursor(QtGui.QTextCursor.MoveOperation.End)
                        textedit.insertPlainText(chunk)
            except FileNotFoundError:
                pass
        timer.timeout.connect(_poll)
        timer.start()
        textedit._tail_timer = timer
# --- start a scan (note: QThread has NO parent; we manage lifetime)
def _start_dir_scan(self, folder: Path):
    # cancel old workers before starting new
    for w in list(self._active_workers):
        w.cancel()
    for t in list(self._threads):
        if t.isRunning():
            t.requestInterruption()
            t.quit()
            t.wait(5000)

    th = QtCore.QThread()  # <- no parent
    th.setObjectName(f"DirScan::{folder}")

    worker = DirScanWorker(folder, self.EXTS)
    worker.moveToThread(th)

    # wire signals
    th.started.connect(worker.run)
    worker.progress.connect(self._on_scan_progress)
    worker.done.connect(self._on_scan_done)
    worker.error.connect(self._on_scan_error)

    # cleanup and list maintenance
    def _cleanup_refs():
        try:
            worker.deleteLater()
        except Exception:
            pass
        if th in self._threads: self._threads.remove(th)
        if worker in self._active_workers: self._active_workers.remove(worker)
        th.deleteLater()

    worker.done.connect(lambda *_: th.quit())
    worker.error.connect(lambda *_: th.quit())
    th.finished.connect(_cleanup_refs)

    self._threads.append(th)
    self._active_workers.append(worker)
    th.start()
class ScanTask(QtCore.QRunnable):
    def __init__(self, folder, exts, chunk_cb, done_cb, error_cb):
        super().__init__()
        self.setAutoDelete(True)
        self.folder, self.exts = Path(folder), {e.lower() for e in exts}
        self.chunk_cb, self.done_cb, self.error_cb = chunk_cb, done_cb, error_cb
    def run(self):
        try:
            batch, all_paths = [], []
            for p in sorted(self.folder.iterdir()):
                if p.is_file() and p.suffix.lower() in self.exts:
                    s = str(p); batch.append(s); all_paths.append(s)
                    if len(batch) >= 256:
                        QtCore.QMetaObject.invokeMethod(
                            self.chunk_cb, "emit",
                            QtCore.Qt.ConnectionType.QueuedConnection,
                            QtCore.Q_ARG(list, batch)
                        )
                        batch = []
            if batch:
                QtCore.QMetaObject.invokeMethod(self.chunk_cb, "emit",
                    QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(list, batch))
            QtCore.QMetaObject.invokeMethod(self.done_cb, "emit",
                QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(list, all_paths))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self.error_cb, "emit",
                QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, str(e)))
@QtCore.pyqtSlot(list)
def _on_scan_progress(self, chunk: list[str]):
    for path in chunk:
        lbl = QtWidgets.QLabel()
        lbl.setFixedSize(self.expanded_thumb_size, self.expanded_thumb_size)
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("border:1px solid #ccc; background:#eee;")
        icon = QtGui.QIcon(path)
        pm = icon.pixmap(self.expanded_thumb_size, self.expanded_thumb_size)
        if not pm.isNull():
            lbl.setPixmap(pm)
        lbl.setProperty("path", path)
        lbl.mousePressEvent = (lambda ev, p=path: self._show_image(p))
        self.expanded_layout.addWidget(lbl)
@QtCore.pyqtSlot(list)
def _on_scan_done(self, all_paths: list[str]):
    self.current_images = all_paths
    self.current_index = 0 if all_paths else -1
    if all_paths:
        self._show_image(all_paths[0])

@QtCore.pyqtSlot(str)
def _on_scan_error(self, msg: str):
    logging.getLogger(__name__).exception("Dir scan error: %s", msg)
# --- worker wiring: instance-based, explicit shutdown, no thread parent
class DirScanWorker(QtCore.QObject):
    progress = QtCore.pyqtSignal(list)
    done     = QtCore.pyqtSignal(list)
    error    = QtCore.pyqtSignal(str)

    def __init__(self, folder: Path, exts: set[str], chunk_size=256, parent=None):
        super().__init__(parent)
        self.folder = Path(folder)
        self.exts = {e.lower() for e in exts}
        self.chunk_size = max(1, chunk_size)
        self._cancel = False

    @QtCore.pyqtSlot()
    def run(self):
        try:
            if not self.folder.exists():
                self.done.emit([])
                return
            batch, all_paths = [], []
            for p in sorted(self.folder.iterdir()):
                # honor both our cancel flag and QThread interruption
                if self._cancel or QtCore.QThread.currentThread().isInterruptionRequested():
                    return
                if p.is_file() and p.suffix.lower() in self.exts:
                    s = str(p)
                    batch.append(s); all_paths.append(s)
                    if len(batch) >= self.chunk_size:
                        self.progress.emit(batch); batch = []
            if batch and not self._cancel:
                self.progress.emit(batch)
            if not self._cancel:
                self.done.emit(all_paths)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancel = True

# --- augment an existing window instance (not the class)
def get_WorkerScans(self):
    # strong refs so threads aren't GC'd early
    self._threads: list[QtCore.QThread] = []
    self._active_workers: list[DirScanWorker] = []

    # logging view exists on the instance
    self.log = QTextEdit()
    self.log.setReadOnly(True)
    self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    # bind methods to the instance
    self._start_dir_scan = _start_dir_scan.__get__(self)
    self._on_scan_progress = _on_scan_progress.__get__(self)
    self._on_scan_done = _on_scan_done.__get__(self)
    self._on_scan_error = _on_scan_error.__get__(self)

    # graceful shutdown used by both closeEvent and aboutToQuit
    self._graceful_shutdown = _graceful_shutdown.__get__(self)

    # wrap/replace closeEvent to ensure cleanup
    orig_close = getattr(self, "closeEvent", None)
    def _wrapped_close(ev):
        try:
            self._graceful_shutdown()
        finally:
            if orig_close:
                orig_close(ev)
            else:
                super(self.__class__, self).closeEvent(ev)
    self.closeEvent = _wrapped_close
    return self
# --- clean shutdown routine shared by window closing and app exit
def _graceful_shutdown(self):
    # tell workers to stop producing
    for w in list(self._active_workers):
        w.cancel()
    # request threads to quit and block until they do
    for t in list(self._threads):
        if t.isRunning():
            t.requestInterruption()
            t.quit()
            t.wait(5000)  # 5s hard wait
    self._active_workers.clear()
    self._threads.clear()
# Clean shutdown: stop workers before widget dies.
def closeEvent(self, e: QtGui.QCloseEvent) -> None:
    try:
        for w in list(self._active_workers):
            w.cancel()
        for t in list(self._threads):
            if t.isRunning():
                t.quit()
                t.wait(3000)
    finally:
        self._active_workers.clear()
        self._threads.clear()
        super().closeEvent(e)

# Helper to start a worker safely
def _start_dir_scan(self, folder: Path):
    # cancel any existing workers
    for w in list(self._active_workers):
        w.cancel()
    # spin up new worker
    th = QtCore.QThread(self)
    worker = DirScanWorker(folder, self.EXTS)
    worker.moveToThread(th)

    # connect signals
    th.started.connect(worker.run)
    worker.progress.connect(self._on_scan_progress)  # update UI safely
    worker.done.connect(self._on_scan_done)
    worker.error.connect(self._on_scan_error)

    # ensure cleanup
    worker.done.connect(lambda *_: th.quit())
    worker.error.connect(lambda *_: th.quit())
    th.finished.connect(worker.deleteLater)
    th.finished.connect(lambda: self._threads.remove(th) if th in self._threads else None)
    th.finished.connect(lambda: self._active_workers.remove(worker) if worker in self._active_workers else None)

    # keep refs; start
    self._threads.append(th)
    self._active_workers.append(worker)
    th.start()

# Slots that update your UI
@QtCore.pyqtSlot(list)
def _on_scan_progress(self, chunk: list[str]):
    # Append chunk into your expanded strip / tree model incrementally
    for path in chunk:
        # Example: add thumbnail label (keep your existing method if you have one)
        lbl = QtWidgets.QLabel()
        lbl.setFixedSize(self.expanded_thumb_size, self.expanded_thumb_size)
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("border:1px solid #ccc; background:#eee;")
        icon = QtGui.QIcon(path)
        pm = icon.pixmap(self.expanded_thumb_size, self.expanded_thumb_size)
        if not pm.isNull():
            lbl.setPixmap(pm)
        lbl.setProperty("path", path)
        lbl.mousePressEvent = (lambda ev, p=path: self._show_image(p))
        self.expanded_layout.addWidget(lbl)

@QtCore.pyqtSlot(list)
def _on_scan_done(self, all_paths: list[str]):
    self.current_images = all_paths
    self.current_index = 0 if all_paths else -1
    if all_paths:
        self._show_image(all_paths[0])

@QtCore.pyqtSlot(str)
def _on_scan_error(self, msg: str):
    logging.getLogger(__name__).exception("Dir scan error: %s", msg)
   
# Setup robust logging
LOG_DIR = os.path.join(os.path.expanduser("~"), ".cache", "abstract_finder")
LOG_FILE = os.path.join(LOG_DIR, "finder.log")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File: rotating, safe in long sessions
    f = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    f.setLevel(logging.DEBUG)
    f.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    ))
    logger.addHandler(f)

    # Console (stderr) for dev runs
    c = logging.StreamHandler(sys.stderr)
    c.setLevel(logging.INFO)
    c.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(c)

setup_logging()

# Crash handlers
def _format_exc(exctype, value, tb):
    return "".join(traceback.format_exception(exctype, value, tb))

def excepthook(exctype, value, tb):
    msg = _format_exc(exctype, value, tb)
    logging.critical("UNCAUGHT EXCEPTION:\n%s", msg)

sys.excepthook = excepthook

def threading_excepthook(args):
    msg = _format_exc(args.exc_type, args.exc_value, args.exc_traceback)
    logging.critical("THREAD EXCEPTION:\n%s", msg)

threading.excepthook = threading_excepthook

# Optional: hook Qt message handler into Python logging
from PyQt6.QtCore import qInstallMessageHandler, QtMsgType

def qt_message_handler(mode, ctx, message):
    level = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }.get(mode, logging.INFO)
    logging.log(level, "Qt: %s (%s:%d)", message, ctx.file, ctx.line)

qInstallMessageHandler(qt_message_handler)

# Callable startConsole tool
# --- startConsole: instantiate first, then wire workers/logs
def startConsole(console_class, *args, **kwargs):
    try:
        logger.info("Starting console application")
        app = QApplication(sys.argv)

        win = console_class(*args, **kwargs)          # 1) create the instance
        get_WorkerScans(win)                          # 2) now add worker fields/methods
        attach_textedit_to_logs(win.log, tail_file=get_log_file_path())  # 3) textedit exists

        # 4) make sure background threads die cleanly on process exit as well
        app.aboutToQuit.connect(win._graceful_shutdown)

        win.show()
        sys.exit(app.exec())
    except Exception:
        logger.critical("Startup failed: %s", traceback.format_exc())
        print(traceback.format_exc())
        return None
