from .collectFilesTab import collectFilesTab
from .diffParserTab import diffParserTab
from .directoryMapTab import directoryMapTab
from .extractImportsTab import extractImportsTab
from .finderTab import finderTab
from .finderConsole import finderConsole
from abstract_gui.QT6 import QApplication,sys
import traceback
def startFinderConsole():
    try:
        app = QApplication(sys.argv)
        win = finderConsole()
        win.show()
        sys.exit(app.exec())
    except Exception:
        print(traceback.format_exc())
