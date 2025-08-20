# functions_console.py
from .imports import initFuncs,QWidget
from .initFuncs import initFuncs
# --- FlowLayout (chips that wrap) -------------------------------------------
class flowLayout(QLayout):
    def __init__(self, parent=None, margin=0, hspacing=8, vspacing=6):
        super().__init__(parent)
        self._items = []; self._h = hspacing; self._v = vspacing
        self.setContentsMargins(margin, margin, margin, margin)
flowLayout = initFuncs(flowLayout)
