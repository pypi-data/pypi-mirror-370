from ..functions import *
def browse_dir(self):
    d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
    if d:
        self.dir_in.setText(d)
def make_params(self):
    directory = self.dir_in.text().strip()
    if not directory or not os.path.isdir(directory):
        raise ValueError("Directory is missing or not a valid folder.")
    def process_input(input_widget, prefix_dot=False):
        raw = input_widget.text().strip()
        if not raw:
            return False
        items = [item.strip() for item in raw.split(',') if item.strip()]
        if prefix_dot:
            items = [f'.{item}' if not item.startswith('.') else item for item in items]
        return set(items) if items else False
    allowed_exts = process_input(self.allowed_exts_in, prefix_dot=True)
    unallowed_exts = process_input(self.unallowed_exts_in, prefix_dot=True)
    exclude_types = process_input(self.exclude_types_in)
    exclude_dirs = list(process_input(self.exclude_dirs_in)) if process_input(self.exclude_dirs_in) else False
    exclude_patterns = list(process_input(self.exclude_patterns_in)) if process_input(self.exclude_patterns_in) else False
    add = self.chk_add.isChecked()
    recursive = self.chk_recursive.isChecked()
    include_files = self.chk_include_files.isChecked()
    prefix = self.prefix_in.text().strip()
    return {
        'directory': directory,
        'allowed_exts': allowed_exts,
        'unallowed_exts': unallowed_exts,
        'exclude_types': exclude_types,
        'exclude_dirs': exclude_dirs,
        'exclude_patterns': exclude_patterns,
        'add': add,
        'recursive': recursive,
        'include_files': include_files,
        'prefix': prefix
    }
def start_map(self):
    self.log.clear()
    self.btn_run.setEnabled(False)
    try:
        params = self.make_params()
    except Exception as e:
        QMessageBox.critical(self, "Bad input", str(e))
        self.btn_run.setEnabled(True)
        return
    class MapWorker(QThread):
        log = pyqtSignal(str)
        done = pyqtSignal(str)
        def __init__(self, params):
            super().__init__()
            self.params = params
        def run(self):
            try:
                map_str = get_directory_map(**self.params)
                self.done.emit(map_str)
            except Exception:
                self.log.emit(traceback.format_exc())
                self.done.emit("")
    self.worker = MapWorker(params)
    self.worker.log.connect(self.append_log)
    self.worker.done.connect(self.display_map)
    self.worker.finished.connect(lambda: self.btn_run.setEnabled(True))
    self.worker.start()
def append_log(self, text: str):
    self.log.moveCursor(self.log.textCursor().End)
    self.log.insertPlainText(text)
def display_map(self, map_str: str):
    if map_str:
        self.log.setPlainText(map_str)
    else:
        self.append_log("No map generated.\n")

