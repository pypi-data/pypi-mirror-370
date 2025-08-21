from .main import *
from abstract_gui.QT6.startConsole import  startConsole

def startContentFinderConsole():
    startConsole(ContentFinderConsole)

def startReactRunnerConsole():
    startConsole(reactRunnerConsole)
    
def startReactFinderShell():
    startConsole(reactFinderShell)
