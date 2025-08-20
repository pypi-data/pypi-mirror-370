# common_form.py
import os
from PyQt6.QtCore import Qt, QSignalBlocker
from PyQt6.QtWidgets import (
    QGridLayout, QLineEdit, QSpinBox, QCheckBox, QPushButton,
    QLabel, QHBoxLayout, QFileDialog, QListWidget, QListWidgetItem,
    QToolButton
)

from .shared_state import SharedStateBus
# --- helpers ---------------------------------------------------------------
def make_string(x):
    if isinstance(x, (list, tuple, set)):
        return ",".join(str(i) for i in x)
    return "" if x is None else str(x)

def _norm_csv(val, *, lower=True, split_chars=(",","|")):
    """Normalize a CSV/pipe string or iterable to a sorted tuple for stable compare."""
    if not val or val is False:
        return tuple()
    if isinstance(val, (list, tuple, set)):
        items = [str(v) for v in val]
    else:
        s = str(val)
        for ch in split_chars[1:]:
            s = s.replace(ch, split_chars[0])
        items = [p.strip() for p in s.split(split_chars[0]) if p.strip()]
    if lower:
        items = [i.lower() for i in items]
    return tuple(sorted(items))

def _filters_subset(state: dict) -> dict:
    """Just the filter fields (the ones you care about for auto-unlink)."""
    return {
        "allowed_exts":    _norm_csv(state.get("allowed_exts", "")),
        "unallowed_exts":  _norm_csv(state.get("unallowed_exts", "")),
        "exclude_types":   _norm_csv(state.get("exclude_types", ""), lower=False),
        "exclude_dirs":    _norm_csv(state.get("exclude_dirs", ""),  lower=False),
        "exclude_patterns":_norm_csv(state.get("exclude_patterns",""),lower=False),
    }

def install_common_inputs(host, grid: QGridLayout, *,
                          bus: SharedStateBus,
                          primary_btn=("Run", None),
                          secondary_btn=("Secondary", None),
                          default_allowed_exts_in="ts,tsx,js,jsx,css",
                          default_unallowed_exts_in="",
                          default_exclude_types_in="",
                          default_exclude_dirs_in=['__pycache__','node_modules','junk','backs','backups','backup','logs'],
                          default_exclude_patterns_in="",
                          # NEW:
                          auto_unlink_on_init_if_diff=True,
                          global_default_filters: dict | None = None):

    """
    Adds the shared controls to `host` and wires them to `bus`.
    Expects `host` to already have a QVBoxLayout() as its layout().
    """
    host._bus = bus
    host._applying_remote = False

    # --- widgets (your exact fields) -------------------------------------
    host.dir_in = QLineEdit(os.getcwd())
    btn_browse = QPushButton("Browse…")
    btn_browse.clicked.connect(lambda: _browse_dir(host))

    host.strings_in = QLineEdit("")
    host.strings_in.setPlaceholderText("comma,separated,strings")

    host.allowed_exts_in   = QLineEdit(make_string(default_allowed_exts_in or ""))
    host.unallowed_exts_in = QLineEdit(make_string(default_unallowed_exts_in or ""))
    host.exclude_types_in  = QLineEdit(make_string(default_exclude_types_in or ""))
    host.exclude_dirs_in   = QLineEdit(make_string(default_exclude_dirs_in or ""))
    host.exclude_patterns_in = QLineEdit(make_string(default_exclude_patterns_in or ""))

    host.chk_add        = QCheckBox("Add");          host.chk_add.setChecked(False)
    host.chk_recursive  = QCheckBox("Recursive");    host.chk_recursive.setChecked(True)
    host.chk_total      = QCheckBox("Require ALL strings (total_strings)")
    host.chk_total.setChecked(False)
    host.chk_parse      = QCheckBox("parse_lines");  host.chk_parse.setChecked(False)
    host.chk_getlines   = QCheckBox("get_lines");    host.chk_getlines.setChecked(True)

    host.spec_spin = QSpinBox(); host.spec_spin.setRange(0, 999999); host.spec_spin.setValue(0)

    # Link / independent toggle
    link_row = QHBoxLayout()
    host.link_btn = QToolButton()
    host.link_btn.setCheckable(True)
    host.link_btn.setChecked(True)
    host.link_btn.setText("🔗 Linked")
    host.link_btn.toggled.connect(lambda on: host.link_btn.setText("🔗 Linked" if on else "⛓ Independent"))
    link_row.addWidget(host.link_btn); link_row.addStretch(1)
    host.layout().addLayout(link_row)

    # --- lay out form -----------------------------------------------------
    r = 0
    grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(host.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
    grid.addWidget(QLabel("Strings"), r, 0); grid.addWidget(host.strings_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Allowed Exts"), r, 0); grid.addWidget(host.allowed_exts_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Unallowed Exts"), r, 0); grid.addWidget(host.unallowed_exts_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Exclude Types"), r, 0); grid.addWidget(host.exclude_types_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Exclude Dirs"), r, 0); grid.addWidget(host.exclude_dirs_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Exclude Patterns"), r, 0); grid.addWidget(host.exclude_patterns_in, r, 1, 1, 2); r+=1

    flags = QHBoxLayout()
    for w in (host.chk_recursive, host.chk_total, host.chk_parse, host.chk_getlines, host.chk_add):
        flags.addWidget(w)
    grid.addLayout(flags, r, 0, 1, 3); r+=1

    sp = QHBoxLayout()
    sp.addWidget(QLabel("spec_line (0=off):")); sp.addWidget(host.spec_spin); sp.addStretch(1)
    grid.addLayout(sp, r, 0, 1, 3); r+=1

    host.layout().addLayout(grid)

    # CTA row
    cta = QHBoxLayout()
    if primary_btn[1]:
        host.btn_run = QPushButton(primary_btn[0]); host.btn_run.clicked.connect(primary_btn[1])
        cta.addWidget(host.btn_run)
    cta.addStretch(1)
    if secondary_btn[1]:
        host.btn_secondary = QPushButton(secondary_btn[0]); host.btn_secondary.clicked.connect(secondary_btn[1])
        cta.addWidget(host.btn_secondary)
    host.layout().addLayout(cta)

    # --- wiring: local changes → bus when linked --------------------------
    def maybe_broadcast(*_):
        if not host.link_btn.isChecked() or host._applying_remote:
            return
        bus.push(host, _read_state(host))

    for le in (host.dir_in, host.strings_in, host.allowed_exts_in,
               host.unallowed_exts_in, host.exclude_types_in,
               host.exclude_dirs_in, host.exclude_patterns_in):
        le.textEdited.connect(maybe_broadcast)

    for cb in (host.chk_add, host.chk_recursive, host.chk_total, host.chk_parse, host.chk_getlines):
        cb.toggled.connect(maybe_broadcast)

    host.spec_spin.valueChanged.connect(maybe_broadcast)

    # bus → host (apply shared state when linked)
    def apply_shared(sender, state: dict):
        if sender is host or not host.link_btn.isChecked():
            return
        _write_state(host, state)
    bus.stateBroadcast.connect(apply_shared)

    # ---------------- initial sync + one-time auto-unlink -----------------
    current = _read_state(host)
    snap = bus.snapshot()

    # Build a comparison baseline if caller didn't pass one
    if global_default_filters is None:
        global_default_filters = dict(
            allowed_exts     = default_allowed_exts_in,
            unallowed_exts   = default_unallowed_exts_in,
            exclude_types    = default_exclude_types_in,
            exclude_dirs     = default_exclude_dirs_in,
            exclude_patterns = default_exclude_patterns_in,
        )

    # If a snapshot exists, compare to it; else compare to declared defaults
    compare_to = snap if snap else global_default_filters

    if auto_unlink_on_init_if_diff and _filters_subset(current) != _filters_subset(compare_to):
        # Filters differ → start Independent (only on init)
        with QSignalBlocker(host.link_btn):
            host.link_btn.setChecked(False)
            host.link_btn.setText("⛓ Independent")
        # Do NOT push/pull now; leave this tab’s values as-is and independent.
    else:
        # Same filters → remain Linked and sync with the bus/defaults
        if snap:
            _write_state(host, snap)      # pull bus
        else:
            bus.push(host, current)       # seed bus
def _browse_dir(host):
    from PyQt6.QtWidgets import QFileDialog
    d = QFileDialog.getExistingDirectory(host, "Choose directory", host.dir_in.text() or os.getcwd())
    if d:
        host.dir_in.setText(d)

def _read_state(h) -> dict:
    return dict(
        directory=h.dir_in.text(),
        strings=h.strings_in.text(),
        allowed_exts=h.allowed_exts_in.text(),
        unallowed_exts=h.unallowed_exts_in.text(),
        exclude_types=h.exclude_types_in.text(),
        exclude_dirs=h.exclude_dirs_in.text(),
        exclude_patterns=h.exclude_patterns_in.text(),
        add=h.chk_add.isChecked(),
        recursive=h.chk_recursive.isChecked(),
        total_strings=h.chk_total.isChecked(),
        parse_lines=h.chk_parse.isChecked(),
        get_lines=h.chk_getlines.isChecked(),
        spec_line=h.spec_spin.value(),
    )

def _write_state(h, s: dict):
    h._applying_remote = True
    try:
        for w, val, setter in (
            (h.dir_in,              s.get("directory",""), lambda w,v: w.setText(v)),
            (h.strings_in,          s.get("strings",""),   lambda w,v: w.setText(v)),
            (h.allowed_exts_in,     s.get("allowed_exts",""), lambda w,v: w.setText(v)),
            (h.unallowed_exts_in,   s.get("unallowed_exts",""), lambda w,v: w.setText(v)),
            (h.exclude_types_in,    s.get("exclude_types",""), lambda w,v: w.setText(v)),
            (h.exclude_dirs_in,     s.get("exclude_dirs",""), lambda w,v: w.setText(v)),
            (h.exclude_patterns_in, s.get("exclude_patterns",""), lambda w,v: w.setText(v)),
        ):
            with QSignalBlocker(w): setter(w, val)

        for w, val in (
            (h.chk_add,       s.get("add", False)),
            (h.chk_recursive, s.get("recursive", True)),
            (h.chk_total,     s.get("total_strings", False)),
            (h.chk_parse,     s.get("parse_lines", False)),
            (h.chk_getlines,  s.get("get_lines", True)),
        ):
            with QSignalBlocker(w): w.setChecked(val)

        with QSignalBlocker(h.spec_spin):
            h.spec_spin.setValue(int(s.get("spec_line", 0)) or 0)
    finally:
        h._applying_remote = False
