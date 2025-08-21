from ..imports import *
from .initFuncs import initFuncs
from PyQt6.QtWidgets import (
    QVBoxLayout, QGridLayout, QLabel, QTextEdit, QPushButton, QWidget
)
from PyQt6.QtCore import Qt

class diffParserTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()

        # --- top-level layout
        root = QVBoxLayout()
        self.setLayout(root)

        # --- common inputs (your existing helper populates self.* fields)
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Parse and Preview", self.preview_patch),
            secondary_btn=("Preview:", self.save_patch),
        )
        # if install_common_inputs doesn't insert 'grid' itself, you can add:
        # root.addLayout(grid)

        # --- diff editor
        root.addWidget(QLabel("Diff:"))
        self.diff_text = QTextEdit()
        self.diff_text.setPlaceholderText("Paste the diff here...")
        root.addWidget(self.diff_text, stretch=1)

        # --- preview
        root.addWidget(QLabel("Preview:"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        root.addWidget(self.preview, stretch=1)

        # --- actions
        btn_save = QPushButton("Approve and Save")
        btn_save.clicked.connect(self.save_patch)
        root.addWidget(btn_save)

        # --- status line (ADD THIS)
        self.status_label = QLabel("Ready.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet("color: #4caf50; padding: 4px 0;")  # green
        root.addWidget(self.status_label)

        # --- log hookup (you already had these)
        set_self_log(self)
        attach_textedit_to_logs(self.log, tail_file=get_log_file_path())

diffParserTab = initFuncs(diffParserTab)
