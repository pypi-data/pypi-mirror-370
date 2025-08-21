# functions_console.py
from .imports import QWidget,pyqtSignal
from .initFuncs import initFuncs
# --- Console ---------------------------------------------------------------
class functionsTab(QWidget):
    functionSelected = pyqtSignal(str)
    scanRequested = pyqtSignal(str)  # scope string ("all" | "reachable")

    def __init__(self, parent=None, use_flow=True):
        super().__init__(parent)
        self.func_map = {}
        self.fn_filter_mode = "io"
        self.current_fn = None
        self._build_ui(use_flow)
functionsTab = initFuncs(functionsTab)
