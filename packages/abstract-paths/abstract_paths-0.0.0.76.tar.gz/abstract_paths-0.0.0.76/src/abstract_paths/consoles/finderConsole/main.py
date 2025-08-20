from .tabs import collectFilesTab,diffParserTab,directoryMapTab,extractImportsTab,finderTab
from .finderConsole import finderConsole
from abstract_gui.QT6.startConsole import  startConsole

def startFinderConsole():
    startConsole(finderConsole)
