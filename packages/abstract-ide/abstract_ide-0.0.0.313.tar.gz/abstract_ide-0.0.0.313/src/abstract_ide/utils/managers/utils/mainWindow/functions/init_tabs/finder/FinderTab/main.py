from ..functions import *
from .initFuncs import initFuncs
class finderTab(QWidget):
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
finderTab = initFuncs(finderTab)
