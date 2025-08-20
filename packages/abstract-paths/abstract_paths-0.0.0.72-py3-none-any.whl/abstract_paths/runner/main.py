from abstract_gui.QT6 import QWidget
from .initFuncs import initFuncs
import logging

class Runner(QWidget):
    def __init__(self, layout=None):
        super().__init__()                 # ← fixed
        

Runner= initFuncs(Runner)
