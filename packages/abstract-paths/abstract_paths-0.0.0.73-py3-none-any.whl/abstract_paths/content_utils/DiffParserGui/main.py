from .functions import *
from .imports import *

class diffParserTab(QWidget):
    def __init__(self):
        super().__init__()
        self._params = None  # NEW: stash Finder params
        self.setLayout(QVBoxLayout())
        # File picker
        try:
            h1 = QHBoxLayout()
            self.file_in = QLineEdit()
            btn_browse = QPushButton("Browse File")
            btn_browse.clicked.connect(self.browse_file)
            h1.addWidget(QLabel("File:"))
            h1.addWidget(self.file_in)
            h1.addWidget(btn_browse)
            self.layout().addLayout(h1)
        except Exception as e:
            logger.info(f"File picker: {e}")
        # Diff paste area
        try:
            self.diff_text = QTextEdit()
            self.diff_text.setPlaceholderText("Paste the diff here...")
            self.layout().addWidget(QLabel("Diff:"))
            self.layout().addWidget(self.diff_text, stretch=1)
        except Exception as e:
            logger.info(f"Diff paste area: {e}")
        # Parse button
        try:
            btn_parse = QPushButton("Parse and Preview")
            btn_parse.clicked.connect(self.preview_patch)
            self.layout().addWidget(btn_parse)
        except Exception as e:
            logger.info(f"Parse button: {e}")
        # Preview area
        try:
            self.preview = QTextEdit()
            self.preview.setReadOnly(True)
            self.layout().addWidget(QLabel("Preview:"))
            self.layout().addWidget(self.preview, stretch=1)
        except Exception as e:
            logger.info(f"Preview area: {e}")
        # Approve save
        try:
            btn_save = QPushButton("Approve and Save")
            btn_save.clicked.connect(self.save_patch)
            self.layout().addWidget(btn_save)
        except Exception as e:
            logger.info(f"Approve save: {e}")
diffParserTab = initFuncs(diffParserTab)
def startDiffGUI():
    app = QApplication(sys.argv)
    window = diffParserTab()
    window.show()
    sys.exit(app.exec_())
