from .collectFilesTab import collectFilesTab
from .diffParserTab import diffParserTab
from .directoryMapTab import directoryMapTab
from .extractImportsTab import extractImportsTab
from .finderTab import finderTab
from .finderConsole import finderConsole
from abstract_gui.QT6.startConsole import  startConsole

def startFinderConsole():
    startConsole(finderConsole)
