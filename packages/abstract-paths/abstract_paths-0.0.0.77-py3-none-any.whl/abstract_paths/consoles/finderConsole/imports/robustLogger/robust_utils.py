# main.py — global logging + crash hooks
import os, sys, logging, traceback, threading
from logging.handlers import RotatingFileHandler
# robustLogger/robust_utils.py (append)
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QTextEdit
from .logHandler import get_log_emitter, ensure_qt_log_handler_attached
import io
# inside __init__, after creating self.log:

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

# ---- crash handlers: keep app alive, log, and surface in GUI ----
def _format_exc(exctype, value, tb):
    return "".join(traceback.format_exception(exctype, value, tb))

def excepthook(exctype, value, tb):
    msg = _format_exc(exctype, value, tb)
    logging.critical("UNCAUGHT EXCEPTION:\n%s", msg)
    # Don't kill the app; just warn. You can emit to a Qt signal if desired.
    # (Qt will keep running.)

sys.excepthook = excepthook

def threading_excepthook(args):
    # Python 3.8+: threading.excepthook
    msg = _format_exc(args.exc_type, args.exc_value, args.exc_traceback)
    logging.critical("THREAD EXCEPTION:\n%s", msg)

setattr(threading, "excepthook", threading_excepthook)

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

# Make LOG_FILE path available to widgets
def get_log_file_path():
    return LOG_FILE


def attach_textedit_to_logs(textedit: QTextEdit, tail_file: str | None = None):
    """
    - Routes live Python/Qt logs to the given QTextEdit.
    - Optionally tails a file (e.g., the rotating log) to show external lines too.
    """
    ensure_qt_log_handler_attached()  # idempotent
    emitter = get_log_emitter()
    emitter.new_log.connect(textedit.append)

    if tail_file:
        # simple non-blocking tail
        textedit._tail_pos = 0
        timer = QTimer(textedit)
        timer.setInterval(500)
        def _poll():
            try:
                with io.open(tail_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(getattr(textedit, "_tail_pos", 0))
                    chunk = f.read()
                    textedit._tail_pos = f.tell()
                if chunk:
                    textedit.moveCursor(textedit.textCursor().MoveOperation.End)
                    textedit.insertPlainText(chunk)
            except FileNotFoundError:
                pass
        timer.timeout.connect(_poll)
        timer.start()
        # keep a ref
        textedit._tail_timer = timer
