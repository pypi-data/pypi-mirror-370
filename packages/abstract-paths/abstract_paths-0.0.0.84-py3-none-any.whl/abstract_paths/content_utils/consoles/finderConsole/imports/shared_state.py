# shared_state.py
from PyQt6.QtCore import QObject, pyqtSignal

class SharedStateBus(QObject):
    stateBroadcast = pyqtSignal(object, dict)  # (sender, state)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._snap: dict = {}

    def snapshot(self) -> dict:
        return dict(self._snap)

    def push(self, sender, state: dict):
        self._snap = dict(state)
        self.stateBroadcast.emit(sender, self.snapshot())
