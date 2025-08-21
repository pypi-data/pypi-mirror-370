from ..imports import *
from .initFuncs import initFuncs
# New Tab: Directory Map
class finderTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Run search", self.start_search),
            secondary_btn=("Open all hits", self.open_all_hits),
        )


        # Output area
        set_self_log(self)
        self.layout().addWidget(QLabel("Results"))
        self.layout().addWidget(self.log, stretch=2)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_one)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []
        attach_textedit_to_logs(self.log, tail_file=get_log_file_path())
finderTab = initFuncs(finderTab)
