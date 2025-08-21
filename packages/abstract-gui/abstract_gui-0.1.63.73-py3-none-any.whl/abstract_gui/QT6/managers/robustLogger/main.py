from PyQt6.QtWidgets import QApplication,QTextEdit
from PyQt6 import QtWidgets, QtGui, QtCore
import traceback, sys, logging, os
from logging.handlers import RotatingFileHandler
import threading

# Setup robust logging
LOG_DIR = os.path.join(os.path.expanduser("~"), ".cache", "abstract_finder")
LOG_FILE = os.path.join(LOG_DIR, "finder.log")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

# Failsafe console starter
def startConsole(console_class):
    try:
        logger.info("Starting console application")
        app = QApplication(sys.argv)
        win = console_class()
        attach_textedit_to_logs(win.log, tail_file=get_log_file_path())  # Attach logs to QTextEdit
        win.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical("Startup failed: %s", traceback.format_exc())
        print(traceback.format_exc())
        return None
