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
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class ContentFinderConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)

        # all content tabs share THIS console’s bus
        inner.addTab(finderTab(self.bus),         "Find Content")
        inner.addTab(directoryMapTab(self.bus),   "Directory Map")
        inner.addTab(collectFilesTab(self.bus),   "Collect Files")
        inner.addTab(extractImportsTab(self.bus), "Extract Python Imports")
        inner.addTab(diffParserTab(self.bus),             "Diff (Repo)")

# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class reactRunnerConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)

        # all content tabs share THIS console’s bus
        inner.addTab(runnerTab(),         "react Runner")
        inner.addTab(functionsTab(),   "Functions")

class reactFinderShell(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Tools")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # If you want these consoles independent, give each its OWN bus.
        # If you want them to share state globally, make ONE bus and pass it to all.
        self.reachRunner   = reactRunnerConsole()                # independent
        self.contentFinder = ContentFinderConsole()              # own bus for content-group only

        self.tabs.addTab(self.reachRunner,   "Reach Runner")
        self.tabs.addTab(self.contentFinder, "Content Finder")
