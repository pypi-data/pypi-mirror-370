from ..imports import *
from .imports import *
from .tabs import (
    runnerTab, functionsTab, collectFilesTab, diffParserTab,
    directoryMapTab, extractImportsTab, finderTab
)
from .imports.shared_state import SharedStateBus

class ConsoleBase(QWidget):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(parent)
        self.bus = bus or SharedStateBus(self)
        self.setLayout(QVBoxLayout())

