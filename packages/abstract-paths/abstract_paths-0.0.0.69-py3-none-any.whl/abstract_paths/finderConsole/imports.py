#!/usr/bin/env python3
import os
import sys
import traceback
from typing import *
from dataclasses import dataclass

# Keep your project search-path extension if you need it:
# sys.path.append("/path/to/project_root")

# Keep abstract_* as-is per your preference
from abstract_paths import (
    findContent, findContentAndEdit,
    get_directory_map, findGlobFiles, collect_filepaths,
    define_defaults, get_py_script_paths
)

# ✅ Qt6 imports
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSpinBox, QMessageBox
)
from PyQt6.QtGui import QTextCursor
