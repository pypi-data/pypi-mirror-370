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
def set_self_log(self,layout):
    self.log = QTextEdit()
    self.log.setReadOnly(True)
    self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap,)
    # Output area
    self.filter_row = QHBoxLayout()
    self.filter_row.addWidget(QLabel("Log Output:")); filter_row.addStretch(1)
    self.filter_row.addWidget(self.rb_all); filter_row.addWidget(self.rb_err); filter_row.addWidget(self.rb_wrn)
    self.filter_row.addWidget(self.cb_try_alt_ext)
    layout.addLayout(self.filter_row)
