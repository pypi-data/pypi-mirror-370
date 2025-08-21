from ..imports import *
from .initFuncs import initFuncs
class diffParserTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Parse and Preview", self.preview_patch),
            secondary_btn=("Preview:", self.preview),
        )
        # Diff paste area
        self.diff_text = QTextEdit()
        self.diff_text.setPlaceholderText("Paste the diff here...")
        self.layout().addWidget(QLabel("Diff:"))
        self.layout().addWidget(self.diff_text, stretch=1)
        # Parse button
        btn_parse = QPushButton("Parse and Preview")
        btn_parse.clicked.connect(self.preview_patch)
        self.layout().addWidget(btn_parse)
        # Preview area
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.layout().addWidget(QLabel("Preview:"))
        self.layout().addWidget(self.preview, stretch=1)
        # Approve save
        btn_save = QPushButton("Approve and Save")
        btn_save.clicked.connect(self.save_patch)
        self.layout().addWidget(btn_save)
        set_self_log(self)
        attach_textedit_to_logs(self.log, tail_file=get_log_file_path())
diffParserTab = initFuncs(diffParserTab)
