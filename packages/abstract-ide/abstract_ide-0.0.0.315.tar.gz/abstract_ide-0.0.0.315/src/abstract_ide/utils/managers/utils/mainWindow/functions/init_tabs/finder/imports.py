#!/usr/bin/env python3
import os
import sys
import traceback
from typing import *
from dataclasses import dataclass
# e.g., if finder code is at project_root/tools/find_tools.py
sys.path.append("/path/to/project_root")
from abstract_paths import findContent, findContentAndEdit
from abstract_paths import get_directory_map, findGlobFiles,collect_filepaths,define_defaults,get_py_script_paths
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSpinBox, QMessageBox
)
# your code: the functions you pasted
from abstract_paths import ( # <- change to your package path
    findContent, findContentAndEdit
)

