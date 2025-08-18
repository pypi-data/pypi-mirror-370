#!/usr/bin/env python3
import os, shutil, sys
from typing import *
from dataclasses import dataclass, field
from abstract_utilities import get_logFile
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QLabel,
    QTextEdit, QFileDialog, QMessageBox,
    QWidget, QApplication
)

# abstract_paths primitives
from ..src.diff_engine import plan_previews, apply_diff_text
from ..src.diff_engine import ApplyReport  # optional if you want counts
from ..src.diff_engine import write_text_atomic  # already re-exported in diff_engine via ...
logger = get_logFile(__name__)
