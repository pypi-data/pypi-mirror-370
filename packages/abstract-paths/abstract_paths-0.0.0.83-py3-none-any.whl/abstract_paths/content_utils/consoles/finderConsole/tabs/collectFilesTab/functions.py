from ..imports import *
# — UI helpers —
def browse_dir(self):
    d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
    if d:
        self.dir_in.setText(d)
  
def make_params(self) -> SearchParams:
    directory = self.dir_in.text().strip()
    if not directory or not os.path.isdir(directory):
        raise ValueError("Directory is missing or not a valid folder.")
    # strings
    s_raw = [s.strip() for s in self.strings_in.text().split(",") if s.strip()]
    # allowed_exts: allow "ts,tsx" or "ts|tsx"
    e_raw = self.allowed_exts_in.text().strip()
    allowed_exts: Union[bool, Set[str]] = False
    if e_raw:
        splitter = '|' if '|' in e_raw else ','
        exts_list = [e.strip() for e in e_raw.split(splitter) if e.strip()]
        allowed_exts = {'.' + e if not e.startswith('.') else e for e in exts_list}
    # unallowed_exts similar
    ue_raw = self.unallowed_exts_in.text().strip()
    unallowed_exts: Union[bool, Set[str]] = False
    if ue_raw:
        splitter = '|' if '|' in ue_raw else ','
        exts_list = [e.strip() for e in ue_raw.split(splitter) if e.strip()]
        unallowed_exts = {'.' + e if not e.startswith('.') else e for e in exts_list}
    # exclude_types
    et_raw = self.exclude_types_in.text().strip()
    exclude_types: Union[bool, Set[str]] = False
    if et_raw:
        exclude_types = {e.strip() for e in et_raw.split(',') if e.strip()}
    # exclude_dirs
    ed_raw = self.exclude_dirs_in.text().strip()
    exclude_dirs: Union[bool, List[str]] = False
    if ed_raw:
        exclude_dirs = [e.strip() for e in ed_raw.split(',') if e.strip()]
    # exclude_patterns
    ep_raw = self.exclude_patterns_in.text().strip()
    exclude_patterns: Union[bool, List[str]] = False
    if ep_raw:
        exclude_patterns = [e.strip() for e in ep_raw.split(',') if e.strip()]
    # add
    add = self.chk_add.isChecked()
    # spec_line
    spec_line = self.spec_spin.value()
    spec_line = False if spec_line == 0 else int(spec_line)
    cfg = define_defaults(
        allowed_exts=allowed_exts,
        unallowed_exts=unallowed_exts,
        exclude_types=exclude_types,
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns,
        add=add,
        )
    recursive=self.chk_recursive.isChecked()
    return directory,cfg,recursive
def start_collect(self):
    self.list.clear()
    self.log.clear()
    self.btn_run.setEnabled(False)
    try:
        directory,cfg,recursive = self.make_params()
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
    self.log.moveCursor(self.log.textCursor().MoveOperation.End)
    self.log.insertPlainText(text)
def populate_results(self, results: list):
    self._last_results = results or []
    if not results:
        self.append_log("✅ No files found.\n")
        self.btn_secondary.setEnabled(False)
        return
    self.append_log(f"✅ Found {len(results)} file(s).\n")
    self.btn_secondary.setEnabled(True)
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
