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
    return {
            'directory': directory,
            'allowed_exts': allowed_exts,
            'unallowed_exts': unallowed_exts,
            'exclude_types': exclude_types,
            'exclude_dirs': exclude_dirs,
            'exclude_patterns': exclude_patterns,
            'add': add,
            'recursive': self.chk_recursive.isChecked(),
            'include_files': self.chk_include_files.isChecked(),
            'prefix': self.prefix_in.text().strip()
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
    self.log.moveCursor(self.log.textCursor().MoveOperation.End)
    self.log.insertPlainText(text)
def display_map(self, map_str: str):
    if map_str:
        self.log.setPlainText(map_str)
    else:
        self.append_log("No map generated.\n")

