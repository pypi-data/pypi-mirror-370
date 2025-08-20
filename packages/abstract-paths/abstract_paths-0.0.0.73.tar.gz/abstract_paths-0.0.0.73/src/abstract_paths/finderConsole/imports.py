#!/usr/bin/env python3
import os
import sys
import traceback
from typing import *
from dataclasses import dataclass

# Keep your project search-path extension if you need it:
# sys.path.append("/path/to/project_root")

# Keep abstract_* as-is per your preference

from ..file_filtering.filter_params import define_defaults
from ..content_utils.src.find_content import findContentAndEdit,findContent
from ..file_filtering.file_filters import collect_filepaths
from ..content_utils.src.file_utils import findGlobFiles
from ..python_utils.utils.utils import get_py_script_paths
# ✅ Qt6 imports
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSpinBox, QMessageBox
)
from PyQt6.QtGui import QTextCursor
