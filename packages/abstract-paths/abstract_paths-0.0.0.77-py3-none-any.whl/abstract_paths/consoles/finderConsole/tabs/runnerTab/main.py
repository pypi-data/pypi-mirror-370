from abstract_gui.QT6 import QWidget, QVBoxLayout, QTabWidget
from .initFuncs import initFuncs

class runnerTab(QWidget):
    def __init__(self, layout=None):
        super().__init__()
        # wire all functions first
        # set up state and widgets
        self.initializeInit()
        # build UI
        root = layout or QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)
        # build runner tab
        self.getRunner(tabs=self.tabs)

runnerTab = initFuncs(runnerTab)
