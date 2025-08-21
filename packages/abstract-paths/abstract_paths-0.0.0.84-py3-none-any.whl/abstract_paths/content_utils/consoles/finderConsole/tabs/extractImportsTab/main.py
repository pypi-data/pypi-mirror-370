from ..imports import *
from .initFuncs import initFuncs
class extractImportsTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Extract Imports", self.start_extract),
            secondary_btn=('copy Imports', None),
            default_allowed_exts_in=".py",
            default_unallowed_exts_in=".pyc",
            default_exclude_types_in="compression",
            default_exclude_dirs_in=["__init__","node_modules"]
            
        )

        # Layout form

        # Output area
        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.layout().addWidget(QLabel("Results"))
        self.layout().addWidget(self.log, stretch=2)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.start_extract)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []
        attach_textedit_to_logs(self.log, tail_file=get_log_file_path())
extractImportsTab = initFuncs(extractImportsTab)
