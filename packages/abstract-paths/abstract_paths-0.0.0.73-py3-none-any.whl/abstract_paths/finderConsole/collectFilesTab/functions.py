from ..functions import *
def browse_dir(self):
    d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
    if d:
        self.dir_in.setText(d)
def make_params(self):
    directory = self.dir_in.text().strip()
    if not directory or not os.path.isdir(directory):
        raise ValueError("Directory is missing or not a valid folder.")
    # exts: list for allowed_exts
    e_raw = self.exts_in.text().strip()
    exts_list = [f".{e.strip()}" if not e.strip().startswith('.') else e.strip() for e in e_raw.split(",") if e.strip()]
    # paths: for simplicity, not used in cfg, but could set exclude_patterns if needed
    p_raw = self.paths_in.text().strip()
    # For now, ignore paths or use as exclude_patterns
    exclude_patterns = [p_raw] if p_raw else None
    recursive = self.chk_recursive.isChecked() # but collect_filepaths always recursive?
    cfg = define_defaults(allowed_exts=exts_list if exts_list else None, exclude_patterns=exclude_patterns)
    return directory, cfg
def start_collect(self):
    self.list.clear()
    self.log.clear()
    self.btn_run.setEnabled(False)
    try:
        directory, cfg = self.make_params()
    except Exception as e:
        QMessageBox.critical(self, "Bad input", str(e))
        self.btn_run.setEnabled(True)
        return
    class CollectWorker(QThread):
        log = pyqtSignal(str)
        done = pyqtSignal(list)
        def __init__(self, directory, cfg):
            super().__init__()
            self.directory = directory
            self.cfg = cfg
        def run(self):
            try:
                results = collect_filepaths([self.directory], self.cfg)
                self.done.emit(results)
            except Exception:
                self.log.emit(traceback.format_exc())
                self.done.emit([])
    self.worker = CollectWorker(directory, cfg)
    self.worker.log.connect(self.append_log)
    self.worker.done.connect(self.populate_results)
    self.worker.finished.connect(lambda: self.btn_run.setEnabled(True))
    self.worker.start()
def append_log(self, text: str):
    self.log.moveCursor(self.log.textCursor().End)
    self.log.insertPlainText(text)
def populate_results(self, results: list):
    self._last_results = results or []
    if not results:
        self.append_log("✅ No files found.\n")
        self.btn_open_all.setEnabled(False)
        return
    self.append_log(f"✅ Found {len(results)} file(s).\n")
    self.btn_open_all.setEnabled(True)
    for file_path in results:
        if isinstance(file_path, str):
            self.list.addItem(QListWidgetItem(file_path))
            self.append_log(file_path + "\n")
def open_one(self, item: QListWidgetItem):
    info = item.text()
    os.system(f'code -g "{info}"')
def open_all_hits(self):
    for i in range(self.list.count()):
        self.open_one(self.list.item(i))
