#!/usr/bin/env python3
import os
import sys
import traceback
from typing import *
from dataclasses import dataclass
# e.g., if finder code is at project_root/tools/find_tools.py
sys.path.append("/path/to/project_root")
from abstract_paths import findContent, findContentAndEdit, getLineNums, get_line_content

from abstract_paths import get_directory_map, findGlobFiles,collect_filepaths,define_defaults,get_py_script_paths

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QSpinBox, QMessageBox
)


# your code: the functions you pasted
from abstract_paths import (   # <- change to your package path
    findContent, findContentAndEdit, getLineNums, get_line_content
)

# Data structures

@dataclass
class SearchParams:
    directory: str
    paths: Union[bool, str] = True
    exts: Union[bool, str, List[str]] = True
    recursive: bool = True
    strings: List[str] = None
    total_strings: bool = False
    parse_lines: bool = False
    spec_line: Union[bool, int] = False
    get_lines: bool = True


# ————————————————————————————————————————————————————————————————
# Background worker so the UI doesn’t freeze
class SearchWorker(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal(list)

    def __init__(self, params: SearchParams):
        super().__init__()
        self.params = params

    def run(self):
        try:
            if findContent is None:
                raise RuntimeError(
                    "Could not import your finder functions. Import error:\n"
                    f"{_IMPORT_ERR if '_IMPORT_ERR' in globals() else 'unknown'}"
                )
            self.log.emit("🔎 Searching…\n")
            results = findContent(
                directory=self.params.directory,
                paths=self.params.paths,
                exts=self.params.exts,
                recursive=self.params.recursive,
                strings=self.params.strings or [],
                total_strings=self.params.total_strings,
                parse_lines=self.params.parse_lines,
                spec_line=self.params.spec_line,
                get_lines=self.params.get_lines
            )
            
            self.done.emit(results)
        except Exception:
            self.log.emit(traceback.format_exc())
            self.done.emit([])


# ————————————————————————————————————————————————————————————————
# Main GUI
# Define SearchParams if not already defined
# Define SearchParams if not already defined
@dataclass
class SearchParams:
    directory: str
    allowed_exts: Union[bool, Set[str]]
    unallowed_exts: Union[bool, Set[str]]
    exclude_types: Union[bool, Set[str]]
    exclude_dirs: Union[bool, List[str]]
    exclude_patterns: Union[bool, List[str]]
    add: bool
    recursive: bool
    strings: List[str]
    total_strings: bool
    parse_lines: bool
    spec_line: Union[bool, int]
    get_lines: bool

class SearchWorker(QThread):
    log = pyqtSignal(str)
    done = pyqtSignal(list)

    def __init__(self, params: SearchParams):
        super().__init__()
        self.params = params

    def run(self):
        self.log.emit("Starting search...\n")
        try:
            results = findContent(
                directory=self.params.directory,
                allowed_exts=self.params.allowed_exts,
                unallowed_exts=self.params.unallowed_exts,
                exclude_types=self.params.exclude_types,
                exclude_dirs=self.params.exclude_dirs,
                exclude_patterns=self.params.exclude_patterns,
                add=self.params.add,
                recursive=self.params.recursive,
                strings=self.params.strings,
                total_strings=self.params.total_strings,
                parse_lines=self.params.parse_lines,
                spec_line=self.params.spec_line,
                get_lines=self.params.get_lines
            )
            self.done.emit(results)
        except Exception as e:
            self.log.emit(f"Error: {str(e)}\n")
            self.done.emit([])

class FinderTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)
        # Strings to find (comma-separated)
        self.strings_in = QLineEdit("")
        self.strings_in.setPlaceholderText("comma,separated,strings")
        # Allowed Extensions (comma-separated or pipe: ts,tsx,js,jsx or ts|tsx|js|jsx)
        self.allowed_exts_in = QLineEdit("ts,tsx,js,jsx,css")
        self.allowed_exts_in.setPlaceholderText("ts,tsx,js,jsx,css")
        # Unallowed Extensions (comma-separated or pipe)
        self.unallowed_exts_in = QLineEdit("")
        self.unallowed_exts_in.setPlaceholderText("comma,separated,unallowed,exts")
        # Exclude Types (comma-separated)
        self.exclude_types_in = QLineEdit("")
        self.exclude_types_in.setPlaceholderText("file,dir,etc")
        # Exclude Dirs (comma-separated)
        self.exclude_dirs_in = QLineEdit("")
        self.exclude_dirs_in.setPlaceholderText("dir1,dir2")
        # Exclude Patterns (comma-separated regex)
        self.exclude_patterns_in = QLineEdit("")
        self.exclude_patterns_in.setPlaceholderText("^src/,pattern2")
        # Add checkbox
        self.chk_add = QCheckBox("Add"); self.chk_add.setChecked(False)
        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)
        self.chk_total = QCheckBox("Require ALL strings (total_strings)"); self.chk_total.setChecked(False)
        self.chk_parse = QCheckBox("parse_lines"); self.chk_parse.setChecked(False)
        self.chk_getlines = QCheckBox("get_lines"); self.chk_getlines.setChecked(True)
        # Spec line (0 = off). Your code uses False to mean “disabled”, so we map 0→False.
        self.spec_spin = QSpinBox(); self.spec_spin.setRange(0, 999999)
        self.spec_spin.setValue(0)
        self.spec_spin.setToolTip("0 disables spec_line. >0 checks only that line (1-based).")
        # Run + Open in editor
        self.btn_run = QPushButton("Run search")
        self.btn_run.clicked.connect(self.start_search)
        self.btn_open_all = QPushButton("Open all hits in VS Code")
        self.btn_open_all.clicked.connect(self.open_all_hits)
        self.btn_open_all.setEnabled(False)
        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
        grid.addWidget(QLabel("Strings"), r, 0); grid.addWidget(self.strings_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Allowed Exts"),r, 0); grid.addWidget(self.allowed_exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Unallowed Exts"),r, 0); grid.addWidget(self.unallowed_exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Types"),r, 0); grid.addWidget(self.exclude_types_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Dirs"),r, 0); grid.addWidget(self.exclude_dirs_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Patterns"),r, 0); grid.addWidget(self.exclude_patterns_in, r, 1, 1, 2); r+=1
        flag_row = QHBoxLayout()
        for w in (self.chk_recursive, self.chk_total, self.chk_parse, self.chk_getlines, self.chk_add):
            flag_row.addWidget(w)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1
        sp = QHBoxLayout()
        sp.addWidget(QLabel("spec_line (0=off):"))
        sp.addWidget(self.spec_spin)
        sp.addStretch(1)
        grid.addLayout(sp, r, 0, 1, 3); r+=1
        self.layout().addLayout(grid)
        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        cta.addStretch(1)
        cta.addWidget(self.btn_open_all)
        self.layout().addLayout(cta)
        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Results"))
        self.layout().addWidget(self.log, stretch=2)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_one)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []
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
        return SearchParams(
            directory=directory,
            allowed_exts=allowed_exts,
            unallowed_exts=unallowed_exts,
            exclude_types=exclude_types,
            exclude_dirs=exclude_dirs,
            exclude_patterns=exclude_patterns,
            add=add,
            recursive=self.chk_recursive.isChecked(),
            strings=s_raw,
            total_strings=self.chk_total.isChecked(),
            parse_lines=self.chk_parse.isChecked(),
            spec_line=spec_line,
            get_lines=self.chk_getlines.isChecked(),
        )
    # — Actions —
    def start_search(self):
        self.list.clear()
        self.log.clear()
        self.btn_run.setEnabled(False)
        try:
            params = self.make_params()
        except Exception as e:
            QMessageBox.critical(self, "Bad input", str(e))
            self.btn_run.setEnabled(True)
            return
        self.worker = SearchWorker(params)
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
            self.append_log("✅ No matches found.\n")
            self.btn_open_all.setEnabled(False)
            return
        self.append_log(f"✅ Found {len(results)} file(s).\n")
        self.btn_open_all.setEnabled(True)
        for fp in results:
            if isinstance(fp, dict):
                file_path = fp.get("file_path")
                lines = fp.get("lines", [])
            else:
                file_path = fp
                lines = []
            if not isinstance(file_path, str):
                continue
            if lines:
                for obj in lines:
                    line = obj.get('line')
                    content = obj.get('content')
                    text = f"{file_path}:{line}"
                    self.list.addItem(QListWidgetItem(text))
                    self.append_log(text + "\n")
            else:
                self.list.addItem(QListWidgetItem(file_path))
                self.append_log(file_path + "\n")
    def open_one(self, item: QListWidgetItem):
        info = item.text()
        # VS Code: code -g file:line[:col]
        os.system(f'code -g "{info}"')
    def open_all_hits(self):
        for i in range(self.list.count()):
            self.open_one(self.list.item(i))

# New Tab: Directory Map
class DirectoryMapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()

        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)

        # Allowed Extensions (comma-separated)
        self.allowed_exts_in = QLineEdit("ts,tsx,js,jsx,css")
        self.allowed_exts_in.setPlaceholderText("ts,tsx,js,jsx,css")

        # Unallowed Extensions (comma-separated)
        self.unallowed_exts_in = QLineEdit("")
        self.unallowed_exts_in.setPlaceholderText("pdf,docx")

        # Exclude Types (comma-separated)
        self.exclude_types_in = QLineEdit("")
        self.exclude_types_in.setPlaceholderText("image,video,audio")

        # Exclude Dirs (comma-separated)
        self.exclude_dirs_in = QLineEdit("")
        self.exclude_dirs_in.setPlaceholderText("")

        # Exclude Patterns (comma-separated)
        self.exclude_patterns_in = QLineEdit("")
        self.exclude_patterns_in.setPlaceholderText("")

        # Prefix
        self.prefix_in = QLineEdit("")
        self.prefix_in.setPlaceholderText("Optional prefix")

        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)
        self.chk_include_files = QCheckBox("Include Files"); self.chk_include_files.setChecked(True)
        self.chk_add = QCheckBox("Add to defaults"); self.chk_add.setChecked(False)

        # Run
        self.btn_run = QPushButton("Get Directory Map")
        self.btn_run.clicked.connect(self.start_map)

        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
        grid.addWidget(QLabel("Allowed Exts"), r, 0); grid.addWidget(self.allowed_exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Unallowed Exts"), r, 0); grid.addWidget(self.unallowed_exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Types"), r, 0); grid.addWidget(self.exclude_types_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Dirs"), r, 0); grid.addWidget(self.exclude_dirs_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Patterns"), r, 0); grid.addWidget(self.exclude_patterns_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Prefix"), r, 0); grid.addWidget(self.prefix_in, r, 1, 1, 2); r+=1

        flag_row = QHBoxLayout()
        flag_row.addWidget(self.chk_recursive)
        flag_row.addWidget(self.chk_include_files)
        flag_row.addWidget(self.chk_add)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1

        self.layout().addLayout(grid)

        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        self.layout().addLayout(cta)

        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Directory Map"))
        self.layout().addWidget(self.log, stretch=2)

    def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
        if d:
            self.dir_in.setText(d)

    def make_params(self):
        directory = self.dir_in.text().strip()
        if not directory or not os.path.isdir(directory):
            raise ValueError("Directory is missing or not a valid folder.")

        def process_input(input_widget, prefix_dot=False):
            raw = input_widget.text().strip()
            if not raw:
                return False
            items = [item.strip() for item in raw.split(',') if item.strip()]
            if prefix_dot:
                items = [f'.{item}' if not item.startswith('.') else item for item in items]
            return set(items) if items else False

        allowed_exts = process_input(self.allowed_exts_in, prefix_dot=True)
        unallowed_exts = process_input(self.unallowed_exts_in, prefix_dot=True)
        exclude_types = process_input(self.exclude_types_in)
        exclude_dirs = list(process_input(self.exclude_dirs_in)) if process_input(self.exclude_dirs_in) else False
        exclude_patterns = list(process_input(self.exclude_patterns_in)) if process_input(self.exclude_patterns_in) else False

        add = self.chk_add.isChecked()
        recursive = self.chk_recursive.isChecked()
        include_files = self.chk_include_files.isChecked()
        prefix = self.prefix_in.text().strip()

        return {
            'directory': directory,
            'allowed_exts': allowed_exts,
            'unallowed_exts': unallowed_exts,
            'exclude_types': exclude_types,
            'exclude_dirs': exclude_dirs,
            'exclude_patterns': exclude_patterns,
            'add': add,
            'recursive': recursive,
            'include_files': include_files,
            'prefix': prefix
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
        self.log.moveCursor(self.log.textCursor().End)
        self.log.insertPlainText(text)

    def display_map(self, map_str: str):
        if map_str:
            self.log.setPlainText(map_str)
        else:
            self.append_log("No map generated.\n")

# New Tab: Collect Files
class CollectFilesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()

        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)

        # Extensions (comma-separated)
        self.exts_in = QLineEdit("ts,tsx,js,jsx,css")
        self.exts_in.setPlaceholderText("ts,tsx,js,jsx,css")

        # Optional: restrict to a sub-path (regex or boolean True)
        self.paths_in = QLineEdit("")
        self.paths_in.setPlaceholderText("True (all) or regex like ^src/")

        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)

        # Run + Open in editor
        self.btn_run = QPushButton("Collect Files")
        self.btn_run.clicked.connect(self.start_collect)

        self.btn_open_all = QPushButton("Open all files in VS Code")
        self.btn_open_all.clicked.connect(self.open_all_hits)
        self.btn_open_all.setEnabled(False)

        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
        grid.addWidget(QLabel("Extensions"),r, 0); grid.addWidget(self.exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Paths"),     r, 0); grid.addWidget(self.paths_in, r, 1, 1, 2); r+=1

        flag_row = QHBoxLayout()
        flag_row.addWidget(self.chk_recursive)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1

        self.layout().addLayout(grid)

        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        cta.addStretch(1)
        cta.addWidget(self.btn_open_all)
        self.layout().addLayout(cta)

        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Results"))
        self.layout().addWidget(self.log, stretch=2)

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_one)
        self.layout().addWidget(self.list, stretch=3)

        self._last_results = []

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

        recursive = self.chk_recursive.isChecked()  # but collect_filepaths always recursive?

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
                QListWidgetItem(file_path, self.list)
                self.append_log(file_path + "\n")

    def open_one(self, item: QListWidgetItem):
        info = item.text()
        os.system(f'code -g "{info}"')

    def open_all_hits(self):
        for i in range(self.list.count()):
            self.open_one(self.list.item(i))


# New Tab: Extract Python Imports
class ExtractImportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()

        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)

        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)

        # Run
        self.btn_run = QPushButton("Extract Imports")
        self.btn_run.clicked.connect(self.start_extract)

        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1

        flag_row = QHBoxLayout()
        flag_row.addWidget(self.chk_recursive)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1

        self.layout().addLayout(grid)

        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        self.layout().addLayout(cta)

        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Extracted Imports"))
        self.layout().addWidget(self.log, stretch=2)

    def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
        if d:
            self.dir_in.setText(d)

    def make_params(self):
        directory = self.dir_in.text().strip()
        if not directory or not os.path.isdir(directory):
            raise ValueError("Directory is missing or not a valid folder.")

        recursive = self.chk_recursive.isChecked()

        # For python, exts='.py'
        cfg = define_defaults(allowed_exts=['.py'])

        return directory, cfg, recursive

    def start_extract(self):
        self.log.clear()
        self.btn_run.setEnabled(False)
        try:
            directory, cfg, recursive = self.make_params()
        except Exception as e:
            QMessageBox.critical(self, "Bad input", str(e))
            self.btn_run.setEnabled(True)
            return

        class ExtractWorker(QThread):
            log = pyqtSignal(str)
            done = pyqtSignal(tuple)

            def __init__(self, directory, cfg, recursive):
                super().__init__()
                self.directory = directory
                self.cfg = cfg
                self.recursive = recursive  # note: collect_filepaths is recursive by default

            def run(self):
                try:
                    py_files = collect_filepaths([self.directory], self.cfg)
                    module_paths, imports = get_py_script_paths(py_files)
                    self.done.emit((module_paths, imports))
                except Exception:
                    self.log.emit(traceback.format_exc())
                    self.done.emit(([], []))

        self.worker = ExtractWorker(directory, cfg, recursive)
        self.worker.log.connect(self.append_log)
        self.worker.done.connect(self.display_imports)
        self.worker.finished.connect(lambda: self.btn_run.setEnabled(True))
        self.worker.start()

    def append_log(self, text: str):
        self.log.moveCursor(self.log.textCursor().End)
        self.log.insertPlainText(text)

    def display_imports(self, result: tuple):
        module_paths, imports = result
        if not imports:
            self.append_log("✅ No imports found.\n")
            return

        output = "Module Paths:\n" + "\n".join(module_paths) + "\n\nImports:\n" + "\n".join(imports)
        self.log.setPlainText(output)


class FinderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔎 Finder — Expanded GUI")
        self.resize(1000, 700)
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        self.finder = FinderTab()
        tabs.addTab(self.finder, "Find Content")

        self.map_tab = DirectoryMapTab()
        tabs.addTab(self.map_tab, "Directory Map")

        self.collect_tab = CollectFilesTab()
        tabs.addTab(self.collect_tab, "Collect Files")

        self.imports_tab = ExtractImportsTab()
        tabs.addTab(self.imports_tab, "Extract Python Imports")

        layout.addWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinderWindow()
    window.show()
    sys.exit(app.exec_())
