from .imports import *
from .tabs import runnerTab,functionsTab,collectFilesTab,diffParserTab,directoryMapTab,extractImportsTab,finderTab
from .imports.shared_state import SharedStateBus
class finderConsole(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        tabs = QTabWidget()
        self.layout().addWidget(tabs)

        bus = SharedStateBus(self)
        self.runner_tab = runnerTab()
        self.functions_tab = functionsTab()
        self.finder_tab = finderTab(bus)
        self.map_tab    = directoryMapTab(bus)
        self.collect_tab = collectFilesTab(bus)
        self.imports_tab    = extractImportsTab(bus)
        self.diff_tab    = diffParserTab()
        tabs.addTab(self.runner_tab, "Reach Runner")
        tabs.addTab(self.functions_tab, "Functions")
        tabs.addTab(self.finder_tab, "Find Content")
        tabs.addTab(self.map_tab, "Directory Map")
        tabs.addTab(self.collect_tab, "Collect Files")
        tabs.addTab(self.imports_tab, "Extract Python Imports")
        tabs.addTab(self.diff_tab, "Diff (Repo)")
        self.layout().addWidget(tabs)

    def _add_tab(self, tabs: QTabWidget, TabClass, *, attr_name: str, tab_name: str | None = None, **kwargs):
        """Create a tab instance, store it on self, and add it to the QTabWidget."""
        tab_name  = tab_name or attr_name
        instance  = TabClass(**kwargs)  # supports constructors with **kwargs (e.g., bus=self.bus)
        setattr(self, attr_name, instance)
        tabs.addTab(instance, tab_name)
        return instance
