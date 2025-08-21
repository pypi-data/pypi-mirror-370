from ..imports import *
def appendLog(self, text: str):
    """Append text to the console log."""
    cursor = self.log_view.textCursor()
    cursor.movePosition(QTextCursor.End)
    self.log_view.setTextCursor(cursor)
    self.log_view.insertPlainText(text)


