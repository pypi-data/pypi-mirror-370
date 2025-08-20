#!/usr/bin/env python3
import os
import sys
import traceback
from typing import *
from dataclasses import dataclass
from abstract_paths import define_defaults
from abstract_paths.content_utils.file_utils import getLineNums,get_directory_map, findGlobFiles
from abstract_paths.content_utils import findContentAndEdit,findContent , get_line_content
from abstract_paths.file_filtering.file_filters import collect_filepaths
from abstract_paths.content_utils.file_utils import findGlobFiles
from abstract_paths.python_utils.utils.utils import get_py_script_paths
# your code: the functions you pasted
# ✅ Qt6 imports
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSignalBlocker
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSpinBox, QMessageBox,QToolButton, QHBoxLayout
)
from PyQt6.QtGui import QTextCursor
from .robustLogger import *

