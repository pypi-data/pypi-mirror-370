from ..imports import *
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Union, Set
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Hunk:
    subs: List[str] = field(default_factory=list)
    adds: List[str] = field(default_factory=list)
    content: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_multiline(self) -> bool:
        return len(self.subs) > 1 or len(self.adds) > 1

@dataclass
class ApplyReport:
    changed_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    hunks_applied: int = 0
    hunks_skipped: int = 0
    
    def extend_changed(self, path: str):
        if path not in self.changed_files:
            self.changed_files.append(path)
    
    def extend_skipped(self, path: str):
        if path not in self.skipped_files:
            self.skipped_files.append(path)

def read_any_file(file_path: str) -> str:
    """Read file content as string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise

def write_to_file(data: str, file_path: str):
    """Write string to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        raise

def get_files_and_dirs(
    directory: str,
    allowed_exts: Union[bool, Set[str], List[str], None] = None,
    unallowed_exts: Union[bool, Set[str], List[str], None] = None,
    exclude_types: Union[bool, Set[str], List[str], None] = None,
    exclude_dirs: Union[bool, List[str], None] = None,
    exclude_patterns: Union[bool, List[str], None] = None,
    add: bool = False,
    recursive: bool = True
) -> Tuple[List[str], List[str]]:
    """Get list of directories and files with filtering."""
    dirs = []
    files = []
    exclude_dirs = list(exclude_dirs) if isinstance(exclude_dirs, (set, list)) else []
    allowed_exts = list(allowed_exts) if isinstance(allowed_exts, (set, list)) else []
    unallowed_exts = list(unallowed_exts) if isinstance(unallowed_exts, (set, list)) else []
    exclude_types = list(exclude_types) if isinstance(exclude_types, (set, list)) else []
    exclude_patterns = list(exclude_patterns) if isinstance(exclude_patterns, (list, set)) else []
    for root, subdirs, filenames in os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]:
        subdirs[:] = [d for d in subdirs if d not in exclude_dirs]
        dirs.extend([os.path.join(root, d) for d in subdirs])
        for fname in filenames:
            fpath = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1]
            if allowed_exts and ext not in allowed_exts:
                continue
            if unallowed_exts and ext in unallowed_exts:
                continue
            if any(re.search(pat, fpath) for pat in exclude_patterns):
                continue
            files.append(fpath)
    return dirs, files

def browse_dir(self):
    d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
    if d:
        self.dir_in.setText(d)

def make_params(self) -> List[str]:
    directory = self.dir_in.text().strip()
    if not directory or not os.path.isdir(directory):
        raise ValueError("Directory is missing or not a valid folder.")
    s_raw = [s.strip() for s in self.strings_in.text().split(",") if s.strip()]
    e_raw = self.allowed_exts_in.text().strip()
    allowed_exts: Union[bool, Set[str]] = False
    if e_raw:
        splitter = '|' if '|' in e_raw else ','
        exts_list = [e.strip() for e in e_raw.split(splitter) if e.strip()]
        allowed_exts = {'.' + e if not e.startswith('.') else e for e in exts_list}
    ue_raw = self.unallowed_exts_in.text().strip()
    unallowed_exts: Union[bool, Set[str]] = False
    if ue_raw:
        splitter = '|' if '|' in ue_raw else ','
        exts_list = [e.strip() for e in ue_raw.split(splitter) if e.strip()]
        unallowed_exts = {'.' + e if not e.startswith('.') else e for e in exts_list}
    et_raw = self.exclude_types_in.text().strip()
    exclude_types: Union[bool, Set[str]] = False
    if et_raw:
        exclude_types = {e.strip() for e in et_raw.split(',') if e.strip()}
    ed_raw = self.exclude_dirs_in.text().strip()
    exclude_dirs: Union[bool, List[str]] = False
    if ed_raw:
        exclude_dirs = [e.strip() for e in ed_raw.split(',') if e.strip()]
    ep_raw = self.exclude_patterns_in.text().strip()
    exclude_patterns: Union[bool, List[str]] = False
    if ep_raw:
        exclude_patterns = [e.strip() for e in ep_raw.split(',') if e.strip()]
    add = self.chk_add.isChecked()
    spec_line = self.spec_spin.value()
    spec_line = False if spec_line == 0 else int(spec_line)
    _, files = get_files_and_dirs(
        directory=directory,
        allowed_exts=allowed_exts,
        unallowed_exts=unallowed_exts,
        exclude_types=exclude_types,
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns,
        add=add,
        recursive=self.chk_recursive.isChecked()
    )
    return files

def make_list(strings: Any) -> List[str]:
    if isinstance(strings, list):
        return strings
    return [strings]

def getPaths(files: List[str], strings: Any) -> Tuple[List[str], List[Dict[str, Any]]]:
    strings = make_list(strings)
    tot_strings = '\n'.join(strings) if len(strings) > 1 else (strings[0] if strings else '')
    if not tot_strings:
        return [], []
    nu_files = set()
    found_paths = []
    for file_path in files:
        try:
            og_content = read_any_file(file_path)
            if tot_strings not in og_content:
                continue
            nu_files.add(file_path)
            og_lines = og_content.split('\n')
            for m in re.finditer(re.escape(tot_strings), og_content):
                start_byte = m.start()
                start_line = og_content[:start_byte].count('\n')  # 0-based
                curr = {'file_path': file_path, 'lines': []}
                for j in range(len(strings)):
                    ln = start_line + j
                    if ln >= len(og_lines):
                        break
                    curr['lines'].append({'line': ln, 'content': og_lines[ln]})
                if len(curr['lines']) == len(strings):
                    found_paths.append(curr)
        except Exception as e:
            logger.error(f"Error in getPaths for {file_path}: {e}")
    return list(nu_files), found_paths

def parse_unified_diff(diff_text: str) -> List[Hunk]:
    hunks: List[Hunk] = []
    current = Hunk()
    open_block = False
    def close():
        nonlocal current, open_block
        if open_block and current.subs:
            hunks.append(current)
        current = Hunk()
        open_block = False
    for raw in diff_text.splitlines():
        if raw.startswith('-'):
            open_block = True
            current.subs.append(raw[1:].rstrip())
        elif raw.startswith('+'):
            open_block = True
            current.adds.append(raw[1:].rstrip())
        else:
            if open_block:
                close()
    if open_block:
        close()
    return hunks

def apply_diff_to_directory(self, diff_text: str) -> ApplyReport:
    report = ApplyReport()
    try:
        files = self.make_params()
    except ValueError as e:
        QMessageBox.critical(self, "Error", str(e))
        self.status_label.setText(f"Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        return report
    if not diff_text.strip():
        QMessageBox.critical(self, "Error", "No diff provided.")
        self.status_label.setText("Error: No diff provided.")
        self.status_label.setStyleSheet("color: red;")
        return report
    hunks = parse_unified_diff(diff_text)
    if not hunks:
        QMessageBox.warning(self, "Warning", "No valid hunks found in diff.")
        self.status_label.setText("Warning: No valid hunks found.")
        self.status_label.setStyleSheet("color: orange;")
        return report
    file_to_replacements = defaultdict(list)
    for hunk in hunks:
        if not hunk.subs:
            report.hunks_skipped += 1
            logger.warning("Skipping hunk with empty subs")
            self.log.append("Skipping hunk with empty subs\n")
            continue
        nu_files, found_paths = getPaths(files, hunk.subs)
        hunk.content = found_paths
        any_applied = False
        for content in found_paths:
            if not content['lines']:
                continue
            start_line = content['lines'][0]['line']
            file_path = content['file_path']
            file_to_replacements[file_path].append({
                'start': start_line,
                'end': start_line + len(hunk.subs),
                'adds': hunk.adds.copy(),
                'subs': hunk.subs.copy()
            })
            any_applied = True
        if any_applied:
            report.hunks_applied += 1
            self.log.append(f"Applied hunk to {len(nu_files)} file(s)\n")
        else:
            report.hunks_skipped += 1
            self.log.append("No matches found for hunk\n")
    for file_path, repls in file_to_replacements.items():
        sorted_repls = sorted(repls, key=lambda r: r['start'])
        for i in range(1, len(sorted_repls)):
            if sorted_repls[i-1]['end'] > sorted_repls[i]['start']:
                logger.error(f"Overlapping hunks detected in {file_path}. Skipping file.")
                self.log.append(f"Error: Overlapping hunks in {file_path}. Skipped.\n")
                report.extend_skipped(file_path)
                continue
        sorted_repls.reverse()
        try:
            og_content = read_any_file(file_path)
            lines = og_content.split('\n')
            for r in sorted_repls:
                if r['start'] >= len(lines) or r['end'] > len(lines):
                    logger.warning(f"Invalid line range {r['start']}:{r['end']} in {file_path}, skipping hunk")
                    self.log.append(f"Warning: Invalid line range in {file_path}, skipping hunk\n")
                    continue
                if lines[r['start']:r['end']] != r['subs']:
                    logger.warning(f"Mismatch after previous applies in {file_path}, skipping hunk")
                    self.log.append(f"Warning: Mismatch in {file_path}, skipping hunk\n")
                    continue
                lines = lines[:r['start']] + r['adds'] + lines[r['end']:]
            new_content = '\n'.join(lines)
            if new_content + '\n' != og_content:
                write_to_file(new_content, f"{file_path}.new")
                report.extend_changed(file_path)
                self.log.append(f"Patched {file_path}.new\n")
            else:
                report.extend_skipped(file_path)
                self.log.append(f"No changes needed for {file_path}\n")
        except Exception as e:
            logger.error(f"Error applying to {file_path}: {e}")
            self.log.append(f"Error applying to {file_path}: {str(e)}\n")
            report.extend_skipped(file_path)
    self.status_label.setText(f"Applied {report.hunks_applied} hunks, skipped {report.hunks_skipped} hunks")
    self.status_label.setStyleSheet("color: green;" if report.hunks_applied > 0 else "color: orange;")
    return report

def apply_custom_diff(original_lines: List[str], diff_lines: List[str]) -> str:
    if diff_lines and '/' in diff_lines[0]:
        diff_lines = diff_lines[1:]
    hunks = parse_unified_diff('\n'.join(diff_lines))
    replacements = []
    og_content = '\n'.join(original_lines)
    for hunk in hunks:
        if not hunk.subs:
            continue
        tot_subs = '\n'.join(hunk.subs)
        for m in re.finditer(re.escape(tot_subs), og_content):
            start_byte = m.start()
            start_line = og_content[:start_byte].count('\n')
            if original_lines[start_line:start_line + len(hunk.subs)] == hunk.subs:
                replacements.append({
                    'start': start_line,
                    'end': start_line + len(hunk.subs),
                    'adds': hunk.adds[:]
                })
    sorted_repls = sorted(replacements, key=lambda r: r['start'])
    for i in range(1, len(sorted_repls)):
        if sorted_repls[i-1]['end'] > sorted_repls[i]['start']:
            raise ValueError("Overlapping hunks detected.")
    sorted_repls.reverse()
    lines = original_lines[:]
    for r in sorted_repls:
        lines = lines[:r['start']] + r['adds'] + lines[r['end']:]
    return '\n'.join(lines)

def preview_patch(self):
    file_path = self.file_in.text().strip()
    if not file_path or not os.path.isfile(file_path):
        QMessageBox.critical(self, "Error", "Invalid file path or file does not exist.")
        self.status_label.setText("Error: Invalid file path.")
        self.status_label.setStyleSheet("color: red;")
        return
    diff = self.diff_text.toPlainText().strip()
    if not diff:
        QMessageBox.critical(self, "Error", "No diff provided.")
        self.status_label.setText("Error: No diff provided.")
        self.status_label.setStyleSheet("color: red;")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read().splitlines()
        patched = apply_custom_diff(original, diff.splitlines())
        self.preview.setPlainText(patched)
        self.status_label.setText("Preview generated successfully.")
        self.status_label.setStyleSheet("color: green;")
        self.log.append("Preview generated for single file\n")
    except ValueError as e:
        QMessageBox.critical(self, "Error", str(e))
        self.status_label.setText(f"Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        self.log.append(f"Error in preview: {str(e)}\n")
    except Exception as e:
        QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
        self.status_label.setText(f"Unexpected Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        self.log.append(f"Unexpected error in preview: {str(e)}\n")

def save_patch(self):
    file_path = self.file_in.text().strip()
    patched = self.preview.toPlainText()
    if not patched:
        QMessageBox.warning(self, "Warning", "No preview to save. Generate a preview first.")
        self.status_label.setText("Warning: No preview to save.")
        self.status_label.setStyleSheet("color: orange;")
        return
    if not file_path:
        QMessageBox.critical(self, "Error", "No file path specified.")
        self.status_label.setText("Error: No file path specified.")
        self.status_label.setStyleSheet("color: red;")
        return
    try:
        reply = QMessageBox.question(self, "Confirm Save", "Are you sure you want to overwrite the file?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(patched + '\n')
            QMessageBox.information(self, "Success", "File saved successfully.")
            self.status_label.setText("File saved successfully.")
            self.status_label.setStyleSheet("color: green;")
            self.log.append(f"Saved patched file: {file_path}\n")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        self.status_label.setText(f"Error saving file: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        self.log.append(f"Error saving file: {str(e)}\n")
